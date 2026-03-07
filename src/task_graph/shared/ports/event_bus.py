from abc import ABC, abstractmethod
from task_graph.shared.events import DomainEvent

class EventBus(ABC):
    """
    Abstract port for publishing domain events.
    """
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.
        """
        pass
