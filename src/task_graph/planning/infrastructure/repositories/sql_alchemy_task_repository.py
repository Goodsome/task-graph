from typing import Union, Any, Optional, Callable, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel
from task_graph.planning.infrastructure.orm import TaskModel
from dataclasses import dataclass


@dataclass
class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    session: Session

    def save(self, task: Task) -> None:
        model = self._to_model(task)
        self.session.add(model)
        self.session.flush()

    def get(self, task_id: TaskId) -> Optional[Task]:
        stmt = select(TaskModel).where(TaskModel.id == task_id.value)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    def find_all_active(self, project_id: Optional[str] = None) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.status != TaskStatus.DONE.value)
        if project_id:
            stmt = stmt.where(TaskModel.project_id == project_id)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def find_all(self) -> list[Task]:
        stmt = select(TaskModel)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def find_dependents(self, task_id: TaskId) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.id == task_id.value)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return []
        return [self._to_domain(d) for d in model.dependents]

    def delete(self, task_id: TaskId) -> None:
        stmt = select(TaskModel).where(TaskModel.id == task_id.value)
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            self.session.delete(model)
            self.session.flush()

    def find_by_id(self, task_id: TaskId) -> Task | None:
        return self.get(task_id)

    def find_by_ids(self, task_ids: set[TaskId]) -> list[Task]:
        ids = [tid.value for tid in task_ids]
        stmt = select(TaskModel).where(TaskModel.id.in_(ids))
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def find_paged(
        self,
        page: int,
        page_size: int,
        status: Optional[TaskStatus],
        project_id: Optional[str],
        scope_level: Optional[ScopeLevel],
        search: Optional[str],
    ) -> tuple[list[Task], int]:
        # Create base select statement
        stmt = select(TaskModel)
        if status:
            stmt = stmt.where(TaskModel.status == status.value)
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

        # Get total count using a scalar subquery or separate count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(count_stmt).scalar() or 0

        # Get paged results
        paged_stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        models = self.session.execute(paged_stmt).scalars().all()
        
        return [self._to_domain(m) for m in models], total

    def _to_domain(self, model: TaskModel) -> Task:
        return Task.model_validate(model)

    def _to_model(self, task: Task) -> TaskModel:
        stmt = select(TaskModel).where(TaskModel.id == task.id.value)
        model = self.session.execute(stmt).scalar_one_or_none()
        
        if not model:
            model = TaskModel(id=task.id.value)

        model.project_id = task.project_id
        model.name = task.name
        model.description = task.description
        model.status = task.status.value
        model.scope_level = task.scope_level.value
        model.scope_context = task.scope_context.model_dump(mode="json") if task.scope_context else None
        model.completion_logic = task.completion_logic.value
        model.parent_id = task.parent_id.value if task.parent_id else None
        model.effort = task.effort.value
        model.base_value = task.base_value.value
        model.output = task.output.model_dump(mode="json") if task.output else None
        model.review_feedback = (
            task.review_feedback.model_dump(mode="json") if task.review_feedback else None
        )

        # Handle dependencies
        dep_ids = [tid.value for tid in task.dependencies]
        if dep_ids:
            dep_stmt = select(TaskModel).where(TaskModel.id.in_(dep_ids))
            dependencies = self.session.execute(dep_stmt).scalars().all()
            model.dependencies = list(dependencies)
        else:
            model.dependencies = []

        return model
