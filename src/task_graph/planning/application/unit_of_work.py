import uuid
import logging
from typing import Optional

from abc import ABC, abstractmethod
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.shared.ports.event_bus import EventBus
from sqlalchemy.orm import Session, sessionmaker
from task_graph.planning.infrastructure.repositories.sql_alchemy_task_repository import SqlAlchemyTaskRepository
from task_graph.shared.infrastructure.event_bus import PgNotifyEventBus

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
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory
        self.session: Optional[Session] = None
        self._tasks: Optional[SqlAlchemyTaskRepository] = None
        self._event_bus: Optional[PgNotifyEventBus] = None

    def __enter__(self) -> "UnitOfWork":
        from task_graph.planning.config import get_settings
        settings = get_settings()

        self.session = self._session_factory()
        self._tasks = SqlAlchemyTaskRepository(session=self.session)
        self._event_bus = PgNotifyEventBus(self.session, channel=settings.EVENT_BUS_CHANNEL)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            # Note: We do NOT auto-commit here in order to be explicit in Use Cases.
            self.session.close()

    @property
    def tasks(self) -> SqlAlchemyTaskRepository:
        if not self._tasks:
            raise RuntimeError("Unit of work is not active")
        return self._tasks

    @property
    def event_bus(self) -> PgNotifyEventBus:
        if not self._event_bus:
            raise RuntimeError("Unit of work is not active")
        return self._event_bus

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()
