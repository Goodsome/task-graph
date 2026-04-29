from pydantic import Field

from task_graph.planning.domain.value_objects.gherkin_step import GherkinStep
from task_graph.shared.domain.core.value_object import ValueObject


class Scenario(ValueObject):
    """Gherkin 场景，由名称和有序步骤列表组成。"""

    name: str = Field(..., description="场景名称，用于唯一标识该场景")
    steps: list[GherkinStep] = Field(default_factory=list, description="有序步骤列表")
