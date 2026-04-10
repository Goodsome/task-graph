from __future__ import annotations
from typing import Any
from sqlalchemy import text
from dataclasses import dataclass
from sqlalchemy.orm import Session
from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from task_graph.shared.domain.core.domain_event import DomainEvent

import logging

logger = logging.getLogger(__name__)

@dataclass
class PostgresNotifyEventPublisher(IssueEventPublisher):
    """PostgreSQL NOTIFY implementation of IssueEventPublisher"""

    session: Session
    channel: str = "issue_events"
    
    def publish(self, event: DomainEvent) -> None:
        try:
            payload = event.model_dump_json()
            # PostgreSQL NOTIFY channel name cannot be parameterized safely via BindParams in all drivers,
            # but here channel is a static string or injected setting, so we assemble it securely.
            stmt = text(f"SELECT pg_notify('{self.channel}', :payload)")
            self.session.execute(stmt, {"payload": payload})
            logger.info(f"Published event {event.event_type} to channel {self.channel}")
            logger.debug(f"Event payload: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            raise

