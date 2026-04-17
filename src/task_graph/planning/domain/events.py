from task_graph.shared.domain.core.domain_event import DomainEvent
from pydantic import Field
from task_graph.planning.domain.enums import ScopeLevel, ArchitectureLayer


class BaseTaskEvent(DomainEvent):
    """Task 领域事件的基础类，包含所有公共上下文信息"""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
    bounded_context: str | None = Field(default=None, description="Bounded context the task belongs to")
    architecture_layer: ArchitectureLayer | None = Field(default=None, description="DDD architecture layer the task targets")


class TaskReadyEvent(BaseTaskEvent):
    """Event emitted when a task is ready to be claimed."""
    pass


class TaskCompletedEvent(BaseTaskEvent):
    """Event emitted when a task is completed."""
    pass


class TaskReviewRequestedEvent(BaseTaskEvent):
    """Event emitted when a task is submitted for review."""
    pass


class TaskBlockedEvent(BaseTaskEvent):
    """Event emitted when a task is blocked (e.g., execution error)."""
    reason: str = Field(description="Reason for being blocked")


class TaskInProgressEvent(BaseTaskEvent):
    """Event emitted when a task is claimed and starts execution."""
    pass


class TaskChangesRequestedEvent(BaseTaskEvent):
    """Event emitted when a task review is rejected and changes are requested."""
    feedback: str = Field(description="Review feedback describing required changes")


class TaskDecomposingEvent(BaseTaskEvent):
    """Event emitted when a task is approved for decomposition."""
    pass
