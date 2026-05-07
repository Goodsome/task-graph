import logging
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Callable, override, Self

from sqlalchemy.orm import Session, sessionmaker
from task_graph.shared.application.ports.event_publisher import EventPublisher
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.shared.domain.ports.repository import Repository

logger = logging.getLogger(__name__)


@dataclass
class SqlAlchemyUnitOfWork[T_Repo: Repository[Any, Any]](UnitOfWork[T_Repo]):
    # --- 1. 由 DI 容器注入的依赖项 (自动参与 __init__) ---
    session_factory: sessionmaker[Session]
    repository_factory: Callable[[Session], T_Repo]
    event_publisher_factory: Callable[[Session], EventPublisher]

    # --- 2. UoW 生命周期内部维护的状态项 (不参与 __init__) ---
    session: Session | None = field(default=None, init=False)
    _repository: T_Repo | None = field(default=None, init=False)
    _event_publisher: EventPublisher | None = field(default=None, init=False)

    @override
    def __enter__(self) -> Self:
        self.session = self.session_factory()
        self._repository = self.repository_factory(self.session)
        self._event_publisher = self.event_publisher_factory(self.session)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is not None:
            self.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            pass

        if self.session:
            self.session.close()
            self.session = None
            self._repository = None
            self._event_publisher = None

    @property
    @override
    def repository(self) -> T_Repo:
        if not self._repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._repository

    @property
    @override
    def event_publisher(self) -> EventPublisher:
        if not self._event_publisher:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._event_publisher

    @override
    def commit(self):
        if self.session:
            self.session.commit()

        for aggregate in self.repository.collect_seens():
            for event in aggregate.collect_events():
                self.event_publisher.publish(event)

    @override
    def rollback(self):
        if self.session:
            self.session.rollback()
