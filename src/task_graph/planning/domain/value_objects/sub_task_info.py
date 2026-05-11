from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.scenario import Scenario


class SubTaskInfo(ValueObject):
    """要拆分的子任务信息"""

    name: str
    description: str
    effort: StoryPoint
    base_value: ValueScore
    acceptance_criteria: list[Scenario] = Field(default_factory=list)
    dependencies: set[str] = Field(default_factory=set)
