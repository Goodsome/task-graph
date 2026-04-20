from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.acceptance_criterion import AcceptanceCriterion


class SubTaskInfo(ValueObject):
    """要拆分的子任务信息"""

    name: str = Field(..., description="与子任务 scope_level 对应的名字（将赋值给 ScopeContext）")
    description: str
    effort: StoryPoint
    base_value: ValueScore
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
