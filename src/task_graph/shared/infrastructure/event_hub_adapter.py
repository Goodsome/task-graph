from sqlalchemy.orm import Session
from task_graph.shared.ports.event_bus import EventBus
from event_hub import EventHub, DomainEvent, IntegrationEvent
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
        # 注意：因为 UoW.commit() 是同步的，这里必须使用同步发布
        if isinstance(event, DomainEvent):
            self.hub.publish_domain_sync(event)
            logger.info(f"Published domain event: {event}")
        elif isinstance(event, IntegrationEvent):
            # 假设你的 EventHub 也有针对集成事件的同步发布方法
            # self.hub.publish_integration_sync(event)
            pass
        else:
            raise ValueError(f"Unknown event type: {type(event)}")


    @classmethod
    def build_factory(cls, hub: EventHub) -> Callable[[Session, str], EventBus]:
        """
        作为类方法提供给 UoW 或 DI 容器使用的工厂构建器
        """
        def factory(session: Session, channel: str) -> EventBus:
            return cls(session=session, channel=channel, hub=hub)
        
        return factory