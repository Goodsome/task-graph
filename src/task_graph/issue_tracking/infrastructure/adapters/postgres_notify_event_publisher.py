from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from task_graph.shared.events import DomainEvent

Connection = Any


@dataclass
class PostgresNotifyEventPublisher(IssueEventPublisher):
    """PostgreSQL NOTIFY implementation of IssueEventPublisher"""

    connection: Connection

    def publish(self, event: DomainEvent) -> None: ...

    def publish_all(self, events: list[DomainEvent]) -> None: ...
