from dataclasses import dataclass
from typing import override

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from task_graph.planning.application.dtos.summary_task import (
    ScopeContextSummary,
    SummaryTask,
)
from task_graph.planning.application.ports.task_query_service import TaskQueryService
from task_graph.planning.domain.enums import ScopeLevel, TaskStatus
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.infrastructure.orm_models.task_model import TaskModel


@dataclass
class SqlAlchemyTaskQueryService(TaskQueryService):
    """SQLAlchemy implementation of TaskQueryService.

    Queries operate directly on ORM models and project lightweight DTOs
    without materialising full domain aggregates.
    """

    session_factory: sessionmaker[Session]

    def _to_dto(self, model: TaskModel) -> SummaryTask:
        scope_context = None
        if model.scope_context:
            scope_context = ScopeContextSummary(
                bounded_context=model.scope_context.get("bounded_context"),
                architecture_layer=model.scope_context.get("architecture_layer"),
            )

        return SummaryTask(
            id=str(model.id),
            project_id=model.project_id,
            name=model.name,
            status=model.status,
            scope_level=model.scope_level,
            scope_context=scope_context,
            parent_id=str(model.parent_id) if model.parent_id else None,
            effort=model.effort,
            base_value=model.base_value,
        )

    @override
    def find_paged(
        self,
        page: int,
        page_size: int,
        status: TaskStatus | None,
        project_id: str | None,
        scope_level: ScopeLevel | None,
        search: str | None,
        exclude_status: TaskStatus | None = None,
    ) -> tuple[list[SummaryTask], int]:
        with self.session_factory() as session:
            stmt = select(TaskModel)
            if status:
                stmt = stmt.where(TaskModel.status == status.value)
            elif exclude_status:
                stmt = stmt.where(TaskModel.status != exclude_status.value)
            if project_id:
                stmt = stmt.where(TaskModel.project_id == project_id)
            if scope_level:
                stmt = stmt.where(TaskModel.scope_level == scope_level.value)
            if search:
                stmt = stmt.where(
                    or_(
                        TaskModel.name.ilike(f"%{search}%"),
                        TaskModel.description.ilike(f"%{search}%"),
                    )
                )

            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = session.execute(count_stmt).scalar() or 0

            paged_stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            models = session.execute(paged_stmt).scalars().all()

            return [self._to_dto(m) for m in models], total

    @override
    def find_dependents(self, task_id: TaskId) -> list[SummaryTask]:
        with self.session_factory() as session:
            model = session.get(TaskModel, task_id.value)
            if not model:
                return []
            return [self._to_dto(d) for d in model.dependents]
