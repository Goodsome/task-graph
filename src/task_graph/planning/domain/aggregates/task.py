from pydantic import Field
from task_graph.planning.domain.enums import CompletionLogic, ScopeLevel, TaskStatus
from task_graph.planning.domain.exceptions import (
    IllegalStateTransitionError,
    TaskNotClaimableError,
)
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.scope_context import ScopeContext
from task_graph.shared.domain.core.aggregate_root import AggregateRoot
from task_graph.planning.domain.events import (
    TaskBlocked,
    TaskChangesRequested,
    TaskCompleted,
    TaskCreated,
    TaskDecomposing,
    TaskDelegated,
    TaskInProgress,
    TaskReady,
    TaskReviewRequested,
)
from typing import Any, Self, TypeVar, Union, override
from task_graph.shared.domain.core.domain_event import DomainEvent
from task_graph.planning.domain.value_objects.recurrence_policy import RecurrencePolicy
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.review_feedback import ReviewFeedback
from task_graph.planning.domain.value_objects.scenario import Scenario

T = TypeVar("T", bound=DomainEvent)


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
    acceptance_criteria: list[Scenario] = Field(
        default_factory=list,
        description="以 Gherkin 场景定义的验收标准列表",
    )

    @override
    def __hash__(self) -> int:
        return hash(self.id)

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
        acceptance_criteria: list[Scenario] | None = None,
    ) -> Self:
        """Factory method to create a new Task"""
        if isinstance(scope_level, str):
            scope_level = ScopeLevel(scope_level)
        task = cls(
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
            acceptance_criteria=acceptance_criteria or [],
        )
        task.add_domain_event(task._build_task_event(TaskCreated))
        return task

    def mark_ready(self: Self) -> None:
        """将任务标记为 READY（依赖已满足，可被领取）。

        Raises:
            IllegalStateTransitionError: 当前状态不是 PENDING 或 BLOCKED"""
        if self.status not in (TaskStatus.PENDING, TaskStatus.BLOCKED):
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked ready: current status is {self.status}, expected PENDING or BLOCKED"
            )
        self.status = TaskStatus.READY
        self.add_domain_event(self._build_task_event(TaskReady))

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
        self.add_domain_event(self._build_task_event(TaskInProgress))

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
        self.add_domain_event(self._build_task_event(TaskBlocked, reason=reason))

    def mark_reviewing(self: Self) -> None:
        """标记任务进入审核状态。

        Raises:
            IllegalStateTransitionError: 如果当前状态不是 IN_PROGRESS"""
        if self.status != TaskStatus.IN_PROGRESS:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked reviewing: current status is {self.status}, expected IN_PROGRESS"
            )
        self.status = TaskStatus.REVIEWING
        self.add_domain_event(self._build_task_event(TaskReviewRequested))

    def mark_completed(self: Self) -> None:
        """直接标记任务完成（用于手动/自动完成场景）。

        Raises:
            IllegalStateTransitionError: 当前状态不允许直接完成"""
        allowed = (TaskStatus.REVIEWING, TaskStatus.DECOMPOSING, TaskStatus.DELEGATED)
        if self.status not in allowed:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked completed: current status is {self.status}"
            )
        self.status = TaskStatus.DONE
        self.add_domain_event(self._build_task_event(TaskCompleted))

    def review(
        self: Self, approved: bool, feedback: str
    ) -> None:
        """验证任务并记录反馈。

        Args:
            approved: 是否通过
            feedback: 详细评价意见
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
            if self.output and self.output.sub_tasks:
                self.mark_decomposing()
            else:
                self.mark_completed()
        else:
            self.mark_changes_requested(feedback=feedback)

    def generate_sub_tasks(self: Self) -> list['Task']:
        """根据输出中的 sub_tasks 生成子任务。

        Returns:
            list[Task]: 生成的子任务列表
        Raises:
            IllegalStateTransitionError: 只有 DECOMPOSING 状态可以生成子任务
        """
        if self.status != TaskStatus.DECOMPOSING:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot generate sub tasks: current status is {self.status}, expected DECOMPOSING"
            )
        if not self.output or not self.output.sub_tasks:
            return []

        level_map = {
            ScopeLevel.PROJECT: ScopeLevel.CONTEXT,
            ScopeLevel.CONTEXT: ScopeLevel.ARCHITECTURAL,
            ScopeLevel.ARCHITECTURAL: ScopeLevel.COMPONENT,
        }
        child_scope_level = level_map.get(self.scope_level)
        if not child_scope_level:
            return []

        sub_tasks = []
        for sub_info in self.output.sub_tasks:
            child_name = f"{self.name}[{sub_info.name}]"

            # 继承父任务的上下文信息
            parent_bc = self.scope_context.bounded_context if self.scope_context else None
            parent_al = self.scope_context.architecture_layer if self.scope_context else None

            from task_graph.planning.domain.enums import ArchitectureLayer

            child_bc = parent_bc
            child_al = parent_al
            child_cn = None

            if child_scope_level == ScopeLevel.CONTEXT:
                child_bc = sub_info.name
            elif child_scope_level == ScopeLevel.ARCHITECTURAL:
                try:
                    child_al = ArchitectureLayer(sub_info.name)
                except ValueError:
                    child_al = ArchitectureLayer.NONE
            elif child_scope_level == ScopeLevel.COMPONENT:
                child_cn = sub_info.name

            child_context = ScopeContext.create(
                bounded_context=child_bc,
                architecture_layer=child_al,
                component_name=child_cn,
            )

            child_task = Task.create(
                project_id=self.project_id,
                name=child_name,
                description=sub_info.description,
                effort=sub_info.effort,
                base_value=sub_info.base_value,
                completion_logic=self.completion_logic,
                dependencies=set(),
                scope_level=child_scope_level,
                parent_id=self.id,
                scope_context=child_context,
                acceptance_criteria=sub_info.acceptance_criteria,
            )
            child_task.mark_ready()
            sub_tasks.append(child_task)

        return sub_tasks

    def mark_decomposition_completed(self: Self) -> None:
        """标记任务分解完成。

        Raises:
            IllegalStateTransitionError: 如果当前状态不是 DECOMPOSING 或 DELEGATED"""
        if self.status not in (TaskStatus.DECOMPOSING, TaskStatus.DELEGATED):
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot mark decomposition completed: current status is {self.status}, expected DECOMPOSING or DELEGATED"
            )
        self.mark_completed()

    def mark_delegated(self: Self) -> None:
        """标记任务已分解并委派子任务。

        Raises:
            IllegalStateTransitionError: 如果当前状态不是 DECOMPOSING"""
        if self.status != TaskStatus.DECOMPOSING:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be marked delegated: current status is {self.status}, expected DECOMPOSING"
            )
        self.status = TaskStatus.DELEGATED
        self.add_domain_event(self._build_task_event(TaskDelegated))

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
            self._build_task_event(TaskChangesRequested, feedback=feedback)
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
        self.add_domain_event(self._build_task_event(TaskDecomposing))

    def is_done(self: Self) -> bool:
        return self.status is TaskStatus.DONE

    def _build_task_event(
        self: Self,
        event_class: type[T],
        reason: str | None = None,
        feedback: str | None = None,
    ) -> T:
        """内部辅助方法：统一构造 Task 相关的领域事件，处理基础属性的映射和展平。"""
        bounded_context = (
            self.scope_context.bounded_context if self.scope_context else None
        )
        architecture_layer = (
            self.scope_context.architecture_layer if self.scope_context else None
        )
        params: dict[str, Any] = {
            "task_id": str(self.id),
            "project_id": self.project_id,
            "scope_level": self.scope_level,
            "bounded_context": bounded_context,
            "architecture_layer": architecture_layer,
            "parent_id": str(self.parent_id) if self.parent_id else None,
        }
        if reason is not None:
            params["reason"] = reason
        if feedback is not None:
            params["feedback"] = feedback
        return event_class(**params)

    def is_claimable(self: Self) -> bool:
        return self.status in (TaskStatus.READY, TaskStatus.CHANGES_REQUESTED)
