from typing import Union, Any, Optional, Callable
from sqlalchemy.orm import Session
from sqlalchemy import or_
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import PlanningLevel, TaskStatus
from task_graph.planning.infrastructure.orm import TaskModel
from dataclasses import dataclass


@dataclass
class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    session_factory: Callable[[], Session]

    def save(self, task: Task) -> None:
        with self.session_factory() as session:
            model = self._to_model(task, session)
            session.add(model)
            session.commit()

    def get(self, task_id: TaskId) -> Optional[Task]:
        with self.session_factory() as session:
            model = session.query(TaskModel).filter(TaskModel.id == str(task_id.value)).first()
            if not model:
                return None
            return self._to_domain(model)

    def find_all_active(self, project_id: Optional[str] = None) -> list[Task]:
        with self.session_factory() as session:
            query = session.query(TaskModel).filter(TaskModel.status != TaskStatus.DONE.value)
            if project_id:
                query = query.filter(TaskModel.project_id == project_id)
            models = query.all()
            return [self._to_domain(m) for m in models]

    def find_all(self) -> list[Task]:
        with self.session_factory() as session:
            models = session.query(TaskModel).all()
            return [self._to_domain(m) for m in models]

    def find_dependents(self, task_id: TaskId) -> list[Task]:
        with self.session_factory() as session:
            model = session.query(TaskModel).filter(TaskModel.id == str(task_id.value)).first()
            if not model:
                return []
            return [self._to_domain(d) for d in model.dependents]

    def delete(self, task_id: TaskId) -> None:
        with self.session_factory() as session:
            model = session.query(TaskModel).filter(TaskModel.id == str(task_id.value)).first()
            if model:
                session.delete(model)
                session.commit()

    def find_by_id(self, task_id: TaskId) -> Task | None:
        return self.get(task_id)

    def find_by_ids(self, task_ids: set[TaskId]) -> list[Task]:
        ids = [str(tid.value) for tid in task_ids]
        with self.session_factory() as session:
            models = session.query(TaskModel).filter(TaskModel.id.in_(ids)).all()
            return [self._to_domain(m) for m in models]

    def find_paged(
        self,
        status: Optional[TaskStatus],
        project_id: Optional[str],
        planning_level: Optional[PlanningLevel],
        search: Optional[str],
        page: int,
        page_size: int,
    ) -> tuple[list[Task], int]:
        with self.session_factory() as session:
            query = session.query(TaskModel)
            if status:
                query = query.filter(TaskModel.status == status.value)
            if project_id:
                query = query.filter(TaskModel.project_id == project_id)
            if planning_level:
                query = query.filter(TaskModel.planning_level == planning_level.value)
            if search:
                query = query.filter(
                    or_(
                        TaskModel.name.ilike(f"%{search}%"),
                        TaskModel.description.ilike(f"%{search}%"),
                    )
                )

            total = query.count()
            models = (
                query.offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return [self._to_domain(m) for m in models], total

    def _to_domain(self, model: TaskModel) -> Task:
        return Task.reconstitute(
            task_id=model.id,
            project_id=model.project_id,
            name=model.name,
            description=model.description,
            status=model.status,
            effort=model.effort,
            base_value=model.base_value,
            completion_logic=model.completion_logic,
            dependencies={d.id for d in model.dependencies},
            planning_level=model.planning_level,
            output=model.output,
        )

    def _to_model(self, task: Task, session: Session) -> TaskModel:
        model = session.query(TaskModel).filter(TaskModel.id == str(task.id.value)).first()
        if not model:
            model = TaskModel(id=str(task.id.value))

        model.project_id = task.project_id
        model.name = task.name
        model.description = task.description
        model.status = task.status.value
        model.planning_level = task.planning_level.value
        model.completion_logic = task.completion_logic.value
        model.effort = task.effort.value
        model.base_value = task.base_value.value
        model.output = task.output.model_dump(mode="json") if task.output else None
        model.review_feedback = (
            task.review_feedback.model_dump(mode="json") if task.review_feedback else None
        )

        # Handle dependencies
        dep_ids = [str(tid.value) for tid in task.dependencies]
        if dep_ids:
            dependencies = session.query(TaskModel).filter(TaskModel.id.in_(dep_ids)).all()
            if len(dependencies) != len(dep_ids):
                # Optionally handle missing dependencies, but for now we trust the domain or assume they exist
                pass
            model.dependencies = dependencies
        else:
            model.dependencies = []

        return model
