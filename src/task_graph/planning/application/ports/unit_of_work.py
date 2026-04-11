from types import TracebackType
import logging

from abc import ABC, abstractmethod
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.shared.ports.event_bus import EventBus

logger = logging.getLogger(__name__)

class UnitOfWork(ABC):

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        pass

    @property
    @abstractmethod
    def event_bus(self) -> EventBus:
        pass

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
