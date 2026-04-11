from dataclasses import dataclass, field
from typing import Optional, Callable
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
    
    session: Optional[Session] = field(default=None, init=False)
    _issues: Optional[IssueRepository] = field(default=None, init=False)
    _event_bus: Optional[EventBus] = field(default=None, init=False)
    
    def __enter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        self._issues = self.issue_repository_factory(session=self.session)
        self._event_bus = self.event_bus_factory(self.session, channel=self.event_bus_channel)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            pass
        
        if self.session:
            self.session.close()
            self.session = None
            self._issues = None
            self._event_bus = None

    @property
    def issues(self) -> IssueRepository:
        if not self._issues:
            raise RuntimeError("Unit of work is not active")
        return self._issues

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
