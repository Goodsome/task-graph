from abc import ABC, abstractmethod
from event_hub import DomainEvent

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
