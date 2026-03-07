from task_graph.shared.events import DomainEvent
from pydantic import Field

class TaskReadyEvent(DomainEvent):
    """Event emitted when a task is ready to be claimed."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")

class TaskCompletedEvent(DomainEvent):
    """Event emitted when a task is completed."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")

class TaskReviewRequestedEvent(DomainEvent):
    """Event emitted when a task is submitted for review."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")

class TaskBlockedEvent(DomainEvent):
    """Event emitted when a task is blocked (e.g., execution error)."""
    task_id: str = Field(description="Task ID")
    project_id: str = Field(description="Project ID")
    reason: str = Field(description="Reason for being blocked")
