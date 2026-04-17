from pydantic import Field, field_validator
from task_graph.planning.domain.enums import CompletionLogic, TaskStatus, ScopeLevel
from task_graph.planning.domain.exceptions import (
    IllegalStateTransitionError,
    TaskNotClaimableError,
)
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.scope_context import ScopeContext
from task_graph.shared.domain.core.aggregate_root import AggregateRoot
from typing import Any, Self
from task_graph.planning.domain.value_objects.recurrence_policy import RecurrencePolicy
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.review_feedback import ReviewFeedback
from task_graph.planning.domain.events import (
    TaskBlockedEvent,
    TaskChangesRequestedEvent,
    TaskCompletedEvent,
    TaskInProgressEvent,
    TaskReadyEvent,
    TaskReviewRequestedEvent,
    TaskDecomposingEvent,
)


class Task(AggregateRoot):
    """The atomic unit of planning, representing a node in the DAG."""

    id: TaskId
    project_id: str
    name: str
    description: str
    status: TaskStatus
    completion_logic: CompletionLogic
    effort: StoryPoint
    base_value: ValueScore
    dependencies: set[TaskId]
    scope_level: ScopeLevel
    scope_context: ScopeContext | None = Field(default=None)
    parent_id: TaskId | None = Field(default=None)
    recurrence: RecurrencePolicy | None = Field(default=None)
    output: TaskOutput | None = Field(default=None)
    review_feedback: ReviewFeedback | None = Field(default=None)

    @field_validator("dependencies", mode="before")
    @classmethod
    def validate_dependencies(cls, value: Any) -> set[TaskId]:
        """Convert dependencies from various formats to TaskId set.

        Supports:
        - Set of TaskId objects
        - Set of str/UUID
        - Set of ORM objects with 'id' attribute
        """
        if not isinstance(value, (set, list)):
            raise ValueError("Dependencies must be a set or list")

        deps = set()
        for item in value:
            if hasattr(item, "id"):
                # ORM model or other object with id attribute
                deps.add(TaskId.model_validate(item.id))
            else:
                # Direct primitive or TaskId
                deps.add(TaskId.model_validate(item))
        return deps

    @classmethod
    def create(
        cls: type[Self],
        project_id: str,
        name: str,
        description: str,
        effort: StoryPoint,
        base_value: ValueScore,
        completion_logic: CompletionLogic,
        dependencies: set[TaskId],
        scope_level: ScopeLevel,
        parent_id: TaskId | None = None,
        scope_context: ScopeContext | None = None,
    ) -> Self:
        """Factory method to create a new Task"""
        if isinstance(scope_level, str):
            scope_level = ScopeLevel(scope_level)

        return cls(
            id=TaskId.create(),
            project_id=project_id,
            name=name,
            description=description,
            status=TaskStatus.PENDING,
            completion_logic=completion_logic,
            effort=effort,
            base_value=base_value,
            dependencies=dependencies,
            scope_level=scope_level,
            scope_context=scope_context,
            parent_id=parent_id,
        )

    def mark_ready(self: Self) -> None:
        """将任务标记为 READY（依赖已满足，可被领取）。

        Raises:
            IllegalStateTransitionError: 当前状态不是 PENDING 或 BLOCKED"""
        if self.status not in (TaskStatus.PENDING, TaskStatus.BLOCKED):
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked ready: current status is {self.status}, expected PENDING or BLOCKED"
            )
        self.status = TaskStatus.READY
        self.add_domain_event(
            TaskReadyEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
            )
        )

    def mark_pending(self: Self) -> None:
        """将任务标记为 PENDING（新增了未满足的依赖）。

        Raises:
            IllegalStateTransitionError: 当前状态不是 READY"""
        if self.status != TaskStatus.READY:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked pending: current status is {self.status}, expected READY"
            )
        self.status = TaskStatus.PENDING

    def claim(self: Self) -> None:
        """领取任务开始执行。

        Raises:
            TaskNotClaimableError: 当前状态不是 READY 或 CHANGES_REQUESTED"""
        if not self.is_claimable():
            raise TaskNotClaimableError(
                f"Task {self.id} cannot be claimed: current status is {self.status}, expected READY or CHANGES_REQUESTED"
            )
        self.status = TaskStatus.IN_PROGRESS
        self.add_domain_event(
            TaskInProgressEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
            )
        )

    def set_output(self: Self, output: TaskOutput) -> None:
        """设置任务执行结果。

        Raises:
            IllegalStateTransitionError: 当前状态不是 IN_PROGRESS"""
        if self.status is not TaskStatus.IN_PROGRESS:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot set output: current status is {self.status}, expected IN_PROGRESS"
            )
        self.output = output
        if output.error:
            self.mark_blocked(reason=output.error)
        else:
            self.mark_reviewing()

    def mark_blocked(self: Self, reason: str) -> None:
        """标记任务被阻塞。

        Args:
            reason: 阻塞原因
        Raises:
            IllegalStateTransitionError: 如果当前状态不是 IN_PROGRESS"""
        if self.status != TaskStatus.IN_PROGRESS:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked blocked: current status is {self.status}, expected IN_PROGRESS"
            )
        self.status = TaskStatus.BLOCKED
        self.add_domain_event(
            TaskBlockedEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
                reason=reason,
            )
        )

    def mark_reviewing(self: Self) -> None:
        """标记任务进入审核状态。

        Raises:
            IllegalStateTransitionError: 如果当前状态不是 IN_PROGRESS"""
        if self.status != TaskStatus.IN_PROGRESS:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked reviewing: current status is {self.status}, expected IN_PROGRESS"
            )
        self.status = TaskStatus.REVIEWING
        self.add_domain_event(
            TaskReviewRequestedEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
            )
        )

    def mark_completed(self: Self) -> None:
        """直接标记任务完成（用于手动/自动完成场景）。

        Raises:
            IllegalStateTransitionError: 当前状态不允许直接完成"""
        allowed = (TaskStatus.REVIEWING, TaskStatus.DECOMPOSING)
        if self.status not in allowed:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked completed: current status is {self.status}"
            )
        self.status = TaskStatus.DONE
        self.add_domain_event(
            TaskCompletedEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
            )
        )

    def review(self: Self, approved: bool, feedback: str, requires_decomposition: bool = False) -> None:
        """验证任务并记录反馈。

        Args:
            approved: 是否通过
            feedback: 详细评价意见
            requires_decomposition: 是否需要将该任务进一步拆分为子任务
        Raises:
            IllegalStateTransitionError: 如果当前状态不是 REVIEWING"""
        if self.status != TaskStatus.REVIEWING:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be reviewed: current status is {self.status}, expected REVIEWING"
            )
        self.review_feedback = ReviewFeedback(
            decision="approved" if approved else "changes_requested", comment=feedback
        )
        if approved:
            if requires_decomposition:
                self.mark_decomposing()
            else:
                self.mark_completed()
        else:
            self.mark_changes_requested(feedback=feedback)

    def mark_decomposition_completed(self: Self) -> None:
        """标记任务分解完成。

        Raises:
            IllegalStateTransitionError: 如果当前状态不是 DECOMPOSING"""
        if self.status != TaskStatus.DECOMPOSING:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot mark decomposition completed: current status is {self.status}, expected DECOMPOSING"
            )
        self.mark_completed()

    def mark_changes_requested(self: Self, feedback: str) -> None:
        """标记任务需要修改。

        Args:
            feedback: 审核反馈意见
        Raises:
            IllegalStateTransitionError: 如果当前状态不是 REVIEWING"""
        if self.status != TaskStatus.REVIEWING:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked changes requested: current status is {self.status}, expected REVIEWING"
            )
        self.status = TaskStatus.CHANGES_REQUESTED
        self.add_domain_event(
            TaskChangesRequestedEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
                feedback=feedback,
            )
        )

    def mark_decomposing(self: Self) -> None:
        """标记任务需要分解。

        Raises:
            IllegalStateTransitionError: 如果当前状态不是 REVIEWING"""
        if self.status != TaskStatus.REVIEWING:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked decomposing: current status is {self.status}, expected REVIEWING"
            )
        self.status = TaskStatus.DECOMPOSING
        self.add_domain_event(
            TaskDecomposingEvent(
                task_id=str(self.id),
                project_id=self.project_id,
                scope_level=self.scope_level,
            )
        )

    def is_done(self: Self) -> bool:
        return self.status is TaskStatus.DONE

    def is_claimable(self: Self) -> bool:
        return self.status in (TaskStatus.READY, TaskStatus.CHANGES_REQUESTED)
