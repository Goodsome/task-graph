from types import TracebackType
import logging

from abc import ABC, abstractmethod
from typing import Self, Any
from task_graph.shared.domain.ports.repository import Repository
from task_graph.shared.application.ports.event_publisher import EventPublisher

logger = logging.getLogger(__name__)

class UnitOfWork[T_Repo: Repository[Any, Any]](ABC):

    @property
    @abstractmethod
    def repository(self) -> T_Repo:
        pass

    @property
    @abstractmethod
    def event_publisher(self) -> EventPublisher:
        pass

    @abstractmethod
    def __enter__(self) -> Self:
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
