import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from task_graph.shared.ports.event_bus import EventBus
from task_graph.shared.events import DomainEvent
import logging

logger = logging.getLogger(__name__)

class PgNotifyEventBus(EventBus):
    """
    EventBus implementation using PostgreSQL NOTIFY.
    Uses the provided SQLAlchemy Session to execute NOTIFY without committing.
    """
    def __init__(self, session: Session, channel: str = "domain_events"):
        self._session = session
        self._channel = channel

    def publish(self, event: DomainEvent) -> None:
        try:
            payload = event.model_dump_json()
            # PostgreSQL NOTIFY channel name cannot be parameterized safely via BindParams in all drivers,
            # but here channel is a static string or injected setting, so we assemble it securely.
            stmt = text(f"SELECT pg_notify('{self._channel}', :payload)")
            self._session.execute(stmt, {"payload": payload})
            logger.debug(f"Published event {event.event_type} to channel {self._channel}")
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            raise
