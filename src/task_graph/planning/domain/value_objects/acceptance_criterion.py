from typing import Literal
from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject


TestType = Literal["unit", "integration", "subcutaneous", "e2e"]


class AcceptanceCriterion(ValueObject):
    """
    以 BDD（Behavior-Driven Development）风格记录的单条验收标准。

    每一条验收标准将被转换为一个具体的测试用例。
    结构上遵循 Given-When-Then 范式，以便后续工具自动解析并生成测试代码。
    """

    title: str = Field(..., description="该验收标准的简短标题，用于唯一标识该条目")
    given: str = Field(..., description="前置条件（Given），描述测试的初始上下文")
    when: str = Field(..., description="触发动作（When），描述发生了什么操作或事件")
    then: str = Field(..., description="预期结果（Then），描述系统应有的可观测响应")
    test_type: TestType = Field(
        default="unit",
        description="对应测试用例的类型：unit（单元）、integration（集成）、subcutaneous（皮下）、e2e（端到端）",
    )
