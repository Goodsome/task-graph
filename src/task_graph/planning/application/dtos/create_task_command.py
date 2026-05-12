from task_graph.planning.domain.value_objects.scenario import Scenario
from task_graph.planning.domain.enums import ArchitectureLayer, ScopeLevel
from pydantic import BaseModel, Field


class CreateTaskCommand(BaseModel):
    """创建一个新的规划任务。
    用于 Agent (Planner) 将用户需求转化为具体的执行单元。"""

    project_id: str
    name: str
    description: str
    effort: int
    base_value: float
    scope_level: ScopeLevel
    dependencies: list[str] = Field(default_factory=list)
    parent_id: str | None = Field(default=None)
    bounded_context: str | None = Field(default=None)
    architecture_layer: ArchitectureLayer | None = Field(default=None)
    component_name: str | None = Field(default=None)
    acceptance_criteria: list[Scenario] = Field(default_factory=list)
