import logging
from dataclasses import dataclass, field
from typing import Optional, Callable

from sqlalchemy.orm import Session, sessionmaker
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.shared.ports.event_bus import EventBus

logger = logging.getLogger(__name__)

@dataclass
class SqlAlchemyUnitOfWork(UnitOfWork):
    # --- 1. 由 DI 容器注入的依赖项 (自动参与 __init__) ---
    session_factory: sessionmaker[Session]
    event_bus_channel: str
    task_repository_factory: Callable[[Session], TaskRepository]
    event_bus_factory: Callable[[Session, str], EventBus]

    # --- 2. UoW 生命周期内部维护的状态项 (不参与 __init__) ---
    # 使用 init=False 告诉 dataclass 不要把它们放到构造函数里
    session: Optional[Session] = field(default=None, init=False)
    _tasks: Optional[TaskRepository] = field(default=None, init=False)
    _event_bus: Optional[EventBus] = field(default=None, init=False)

    def __enter__(self) -> "UnitOfWork":
        # 开启数据库会话
        self.session = self.session_factory()
        
        # 将会话传递给具体的仓储和事件总线工厂进行实例化
        self._tasks = self.task_repository_factory(session=self.session)
        self._event_bus = self.event_bus_factory(self.session, channel=self.event_bus_channel)
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            # 同样遵循显示提交的原则，仅在 exit 时清理资源
            pass 
            
        if self.session:
            self.session.close()
            self.session = None
            self._tasks = None
            self._event_bus = None

    @property
    def tasks(self) -> TaskRepository:
        if not self._tasks:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._tasks

    @property
    def event_bus(self) -> EventBus:
        if not self._event_bus:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._event_bus

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()