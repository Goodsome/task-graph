import uuid
import logging
from typing import Optional, Callable

from sqlalchemy.orm import Session, sessionmaker
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.shared.ports.event_bus import EventBus

logger = logging.getLogger(__name__)

class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        event_bus_channel: str,
        task_repository_factory: Callable[[Session], TaskRepository],
        event_bus_factory: Callable[[Session, str], EventBus]
    ):
        self._session_factory = session_factory
        self._event_bus_channel = event_bus_channel
        self._task_repository_factory = task_repository_factory
        self._event_bus_factory = event_bus_factory
        self.session: Optional[Session] = None
        self._tasks: Optional[TaskRepository] = None
        self._event_bus: Optional[EventBus] = None

    def __enter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self._tasks = self._task_repository_factory(session=self.session)
        self._event_bus = self._event_bus_factory(self.session, channel=self._event_bus_channel)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            # Note: We do NOT auto-commit here in order to be explicit in Use Cases.
            self.session.close()

    @property
    def tasks(self) -> TaskRepository:
        if not self._tasks:
            raise RuntimeError("Unit of work is not active")
        return self._tasks

    @property
    def event_bus(self) -> EventBus:
        if not self._event_bus:
            raise RuntimeError("Unit of work is not active")
        return self._event_bus

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()
