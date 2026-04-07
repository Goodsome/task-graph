from abc import ABC, abstractmethod
from typing import Any

from task_graph.shared.events import DomainEvent


class IssueEventPublisher(ABC):
    """Publisher for Issue domain events"""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None: ...

    @abstractmethod
    def publish_all(self, events: list[DomainEvent]) -> None: ...
