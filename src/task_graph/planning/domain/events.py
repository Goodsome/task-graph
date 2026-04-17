from task_graph.shared.domain.core.domain_event import DomainEvent
from pydantic import Field
from task_graph.planning.domain.enums import ScopeLevel, ArchitectureLayer

class TaskReadyEvent(DomainEvent):
    """Event emitted when a task is ready to be claimed."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
    bounded_context: str | None = Field(default=None, description="Bounded context the task belongs to")
    architecture_layer: ArchitectureLayer | None = Field(default=None, description="DDD architecture layer the task targets")

class TaskCompletedEvent(DomainEvent):
    """Event emitted when a task is completed."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")

class TaskReviewRequestedEvent(DomainEvent):
    """Event emitted when a task is submitted for review."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")

class TaskBlockedEvent(DomainEvent):
    """Event emitted when a task is blocked (e.g., execution error)."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
    reason: str = Field(description="Reason for being blocked")

class TaskInProgressEvent(DomainEvent):
    """Event emitted when a task is claimed and starts execution."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")

class TaskChangesRequestedEvent(DomainEvent):
    """Event emitted when a task review is rejected and changes are requested."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
    feedback: str = Field(description="Review feedback describing required changes")


class TaskDecomposingEvent(DomainEvent):
    """Event emitted when a task is approved for decomposition."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    scope_level: ScopeLevel = Field(description="Scope level of the task")
