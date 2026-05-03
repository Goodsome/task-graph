from sqlalchemy.orm import Session
from task_graph.shared.ports.event_bus import EventBus
from event_hub import EventHub, DomainEvent
from dataclasses import dataclass
from typing import Callable

import logging

logger = logging.getLogger(__name__)

@dataclass
class EventHubAdapter(EventBus):
    session: Session
    channel: str
    hub: EventHub

    def publish(self, event: DomainEvent):
        """
        实现 EventBus port 的 publish 方法。
        根据事件类型路由到具体的 hub 发布方法。
        """
        self.hub.publish_domain_sync(event)
        logger.info(f"Published domain event: {event.event_type}")


    @staticmethod
    def build_factory(hub: EventHub) -> Callable[[Session, str], EventBus]:
        """
        作为类方法提供给 UoW 或 DI 容器使用的工厂构建器
        """
        def factory(session: Session, channel: str) -> EventBus:
            return EventHubAdapter(session=session, channel=channel, hub=hub)

        return factory