from pydantic import Field, field_validator
from task_graph.planning.domain.enums import CompletionLogic, TaskStatus, ScopeLevel
from task_graph.planning.domain.exceptions import (
    IllegalStateTransitionError,
    TaskNotClaimableError,
)
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.shared.domain.core.aggregate_root import AggregateRoot
from typing import Any, Self, Union
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
            parent_id=parent_id,
        )

    def to_summary_dict(self: Self) -> dict:
        """Returns a simplified dictionary representation for listing."""
        return {
            "id": str(self.id),
            "project_id": self.project_id,
            "name": self.name,
            "status": self.status.value,
            "scope_level": self.scope_level.value,
            "parent_id": str(self.parent_id.value) if self.parent_id else None,
            "effort": self.effort.value,
            "base_value": self.base_value.value,
        }

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
            self.status = TaskStatus.BLOCKED
            self.add_domain_event(
                TaskBlockedEvent(
                    task_id=str(self.id),
                    project_id=self.project_id,
                    scope_level=self.scope_level,
                    reason=output.error,
                )
            )
        else:
            self.status = TaskStatus.REVIEW
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
        allowed = (TaskStatus.REVIEW, TaskStatus.IN_PROGRESS, TaskStatus.READY)
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

    def review(self: Self, approved: bool, feedback: str) -> None:
        """验证任务并记录反馈。

        Args:
            approved: 是否通过
            feedback: 详细评价意见
        Raises:
            IllegalStateTransitionError: 如果当前状态不是 REVIEW"""
        if self.status != TaskStatus.REVIEW:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be reviewed: current status is {self.status}, expected REVIEW"
            )
        self.review_feedback = ReviewFeedback(
            decision="approved" if approved else "changes_requested", comment=feedback
        )
        if approved:
            self.status = TaskStatus.DONE
            self.add_domain_event(
                TaskCompletedEvent(
                    task_id=str(self.id),
                    project_id=self.project_id,
                    scope_level=self.scope_level,
                )
            )
        else:
            self.status = TaskStatus.CHANGES_REQUESTED
            self.add_domain_event(
                TaskChangesRequestedEvent(
                    task_id=str(self.id),
                    project_id=self.project_id,
                    scope_level=self.scope_level,
                    feedback=feedback,
                )
            )

    def is_done(self: Self) -> bool:
        return self.status is TaskStatus.DONE

    def is_claimable(self: Self) -> bool:
        return self.status in (TaskStatus.READY, TaskStatus.CHANGES_REQUESTED)
