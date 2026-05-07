from dataclasses import dataclass, field
from types import TracebackType
from typing import Callable, override
from sqlalchemy.orm import Session, sessionmaker
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.shared.ports.event_bus import EventBus
import logging

logger = logging.getLogger(__name__)


@dataclass
class SqlAlchemyUnitOfWork(UnitOfWork):
    session_factory: sessionmaker[Session]
    event_bus_channel: str
    issue_repository_factory: Callable[[Session], IssueRepository]
    event_bus_factory: Callable[[Session, str], EventBus]

    session: Session | None = field(default=None, init=False)
    _issues: IssueRepository | None = field(default=None, init=False)
    _event_bus: EventBus | None = field(default=None, init=False)

    @override
    def __enter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        self._issues = self.issue_repository_factory(self.session)
        self._event_bus = self.event_bus_factory(self.session, self.event_bus_channel)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")

        if self.session:
            self.session.close()
            self.session = None
            self._issues = None
            self._event_bus = None

    @property
    @override
    def issues(self) -> IssueRepository:
        if not self._issues:
            raise RuntimeError("Unit of work is not active")
        return self._issues

    @property
    @override
    def event_bus(self) -> EventBus:
        if not self._event_bus:
            raise RuntimeError("Unit of work is not active")
        return self._event_bus

    @override
    def commit(self) -> None:
        if self.session:
            self.session.commit()

    @override
    def rollback(self) -> None:
        if self.session:
            self.session.rollback()
