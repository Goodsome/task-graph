from abc import ABC, abstractmethod
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.shared.ports.event_bus import EventBus


class UnitOfWork(ABC):

    @property
    @abstractmethod
    def issues(self) -> IssueRepository:
        pass

    @property
    @abstractmethod
    def event_bus(self) -> EventBus:
        pass

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
