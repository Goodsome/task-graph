from abc import ABC, abstractmethod
from typing import Any

from task_graph.shared.domain.core.domain_event import DomainEvent


class IssueEventPublisher(ABC):
    """Publisher for Issue domain events"""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None: ...
