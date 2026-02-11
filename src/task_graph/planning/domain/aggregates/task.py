from pydantic import Field
from task_graph.planning.domain.enums import (
    CompletionLogic,
    TaskStatus,
    PlanningLevel,
)
from task_graph.planning.domain.exceptions import (
    TaskNotClaimableError,
    IllegalStateTransitionError,
)
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.shared.models import Aggregate
from typing import Union, Any
from task_graph.planning.domain.value_objects.recurrence_policy import (
    RecurrencePolicy,
)
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.review_feedback import ReviewFeedback


class Task(Aggregate):
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
    dependents: set[TaskId] = Field(default_factory=set)
    planning_level: PlanningLevel
    recurrence: RecurrencePolicy | None = Field(default=None)
    output: TaskOutput | None = Field(default=None)
    review_feedback: ReviewFeedback | None = Field(default=None)

    @classmethod
    def create(
        cls: Any,
        project_id: str,
        name: str,
        description: str,
        effort: StoryPoint,
        base_value: ValueScore,
        completion_logic: CompletionLogic,
        dependencies: set[TaskId],
        planning_level: str | PlanningLevel,
        status: TaskStatus | None = None,
    ) -> "Task":
        """Factory method to create a new Task"""
        if isinstance(planning_level, str):
            planning_level = PlanningLevel(planning_level)
        
        if status is None:
            status = TaskStatus.PENDING
                
        return cls(
            id=TaskId.create(),
            project_id=project_id,
            name=name,
            description=description,
            status=status,
            completion_logic=completion_logic,
            effort=effort,
            base_value=base_value,
            dependencies=dependencies,
            dependents=set(),
            planning_level=planning_level,
        )

    @classmethod
    def reconstitute(
        cls: Any,
        task_id: str,
        project_id: str,
        name: str,
        description: str,
        status: Union[TaskStatus, str],
        effort: Union[StoryPoint, int],
        base_value: Union[ValueScore, float],
        completion_logic: Union[CompletionLogic, str],
        dependencies: Union[set[str], set[TaskId]],
        planning_level: Union[PlanningLevel, str],
        output: Union[TaskOutput, None] = None,
    ) -> Any:

        if not isinstance(status, TaskStatus):
            status = TaskStatus(status)
        if not isinstance(effort, StoryPoint):
            effort = StoryPoint.create(effort=effort)
        if not isinstance(base_value, ValueScore):
            base_value = ValueScore.create(base_value)
        if not isinstance(completion_logic, CompletionLogic):
            completion_logic = CompletionLogic(completion_logic)
        if not isinstance(planning_level, PlanningLevel):
            planning_level = PlanningLevel(planning_level)
        dependencies = set(TaskId.reconstitute(d) for d in dependencies)
        return cls(
            id=TaskId.reconstitute(task_id),
            project_id=project_id,
            name=name,
            description=description,
            status=status,
            effort=effort,
            base_value=base_value,
            completion_logic=completion_logic,
            dependencies=dependencies,
            planning_level=planning_level,
            output=output,
        )
    
    def to_dict(self) -> dict:
        return self.model_dump(
            mode="json"
        )


    def mark_completed(
        self,
    ) -> None:

        self.status = TaskStatus.DONE

    def is_done(
        self,
    ) -> bool:

        return self.status is TaskStatus.DONE

    def set_output(
        self,
        output: TaskOutput,
    ) -> None:
        """Set the task output with execution result."""
        if not self.status is TaskStatus.IN_PROGRESS:
            raise RuntimeError(f"task {self.id} current status is {self.status}, not in_progress")
        self.output = output
        if output.error:
            self.status = TaskStatus.BLOCKED
        else:
            self.status = TaskStatus.REVIEW

    def claim(self) -> None:
        """
        Claim this task for execution.

        Raises:
            TaskNotClaimableError: If task is not in READY state.
        """
        if self.status != TaskStatus.READY:
            raise TaskNotClaimableError(
                f"Task {self.id} cannot be claimed: current status is {self.status}, expected READY"
            )

        self.status = TaskStatus.IN_PROGRESS

    def review(self, approved: bool, feedback: str) -> None:
        """
        验证任务并记录反馈。
        
        Args:
            approved: 是否通过
            feedback: 详细评价意见
        Raises:
            IllegalStateTransitionError: 如果当前状态不是 REVIEW
        """
        if self.status != TaskStatus.REVIEW:
            raise IllegalStateTransitionError(
                f"Task {self.id} cannot be reviewed: current status is {self.status}, expected REVIEW"
            )
        
        self.review_feedback = ReviewFeedback(
            decision="approved" if approved else "rejected",
            comment=feedback
        )

        if approved:
            self.status = TaskStatus.DONE
        else:
            self.status = TaskStatus.REJECTED
