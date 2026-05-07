from sqlalchemy.orm import Session
from task_graph.shared.application.ports.event_publisher import EventPublisher
from event_hub import EventHub, DomainEvent
from dataclasses import dataclass
from typing import Callable

import logging

logger = logging.getLogger(__name__)


@dataclass
class EventHubAdapter(EventPublisher):
    session: Session
    hub: EventHub

    def publish(self, event: DomainEvent):
        self.hub.publish_domain_sync(event)
        logger.info(f"Published domain event: {event.event_type}")

    @staticmethod
    def build_factory(hub: EventHub) -> Callable[[Session], EventPublisher]:
        def factory(session: Session) -> EventPublisher:
            return EventHubAdapter(session=session, hub=hub)

        return factory
