from pydantic import Field

from task_graph.planning.domain.enums import GherkinKeyword
from task_graph.shared.domain.core.value_object import ValueObject


class GherkinStep(ValueObject):
    """Gherkin 场景中的单一步骤，由关键字和步骤文本组成。"""

    keyword: GherkinKeyword = Field(..., description="步骤关键字：Given / When / Then / And / But")
    text: str = Field(..., description="步骤描述文本")
