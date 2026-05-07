from event_hub import DomainEvent
from pydantic import Field


class IssueClosedEvent(DomainEvent):
    """Event emitted when an issue is closed."""
    issue_id: str = Field(description="Issue ID")
    resolution: str | None = Field(description="Optional resolution note")
