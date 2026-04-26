from pydantic import Field
from task_graph.shared.domain.core.domain_event import DomainEvent
from task_graph.planning.domain.enums import ScopeLevel, ArchitectureLayer


class BaseTask(DomainEvent):
    """Task 领域模型的基础类，包含所有公共上下文信息"""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
    bounded_context: str | None = Field(default=None, description="Bounded context the task belongs to")
    architecture_layer: ArchitectureLayer | None = Field(default=None, description="DDD architecture layer the task targets")
