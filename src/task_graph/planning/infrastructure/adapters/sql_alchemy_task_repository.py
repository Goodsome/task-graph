from typing import cast, override
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.exceptions import TaskNotFoundError
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel, CompletionLogic
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.scope_context import ScopeContext
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.review_feedback import ReviewFeedback
from task_graph.planning.domain.value_objects.scenario import Scenario
from task_graph.planning.infrastructure.orm_models.task_model import TaskModel
from dataclasses import dataclass, field


@dataclass
class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    session: Session
    _seen_tasks: set[Task] = field(default_factory=set, init=False)

    @override
    def collect_seen_tasks(self) -> set[Task]:
        return self._seen_tasks

    @override
    def save(self, task: Task) -> None:
        model = self._to_model(task)
        self.session.add(model)
        self._track_task(task)

    @override
    def add(self, task: Task) -> None:
        model = self._to_model(task)
        self.session.add(model)
        self._track_task(task)

    @override
    def get(self, task_id: TaskId) -> Task:
        model = self.session.get(TaskModel, task_id.value)
        if not model:
            raise TaskNotFoundError(f"Task with ID {task_id.value} not found")
        task = self._to_domain(model)

        self._track_task(task)
        return task
        
    @override
    def find_all_active(self, project_id: str | None = None) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.status != TaskStatus.DONE.value)
        if project_id:
            stmt = stmt.where(TaskModel.project_id == project_id)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    @override
    def delete(self, task_id: TaskId) -> None:
        model = self.session.get(TaskModel, task_id.value)
        if model:
            self.session.delete(model)

    @override
    def find_by_ids(self, task_ids: set[TaskId]) -> list[Task]:
        ids = [tid.value for tid in task_ids]
        stmt = select(TaskModel).where(TaskModel.id.in_(ids))
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    @override
    def find_by_parent_id(self, parent_id: TaskId) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.parent_id == parent_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=TaskId.model_validate(model.id),
            project_id=model.project_id,
            name=model.name,
            description=model.description,
            status=TaskStatus(model.status),
            completion_logic=CompletionLogic(model.completion_logic),
            effort=StoryPoint(value=model.effort),
            base_value=ValueScore(value=model.base_value),
            dependencies={TaskId.model_validate(d.id) for d in model.dependencies},
            scope_level=ScopeLevel(model.scope_level),
            scope_context=ScopeContext.model_validate(model.scope_context)
            if model.scope_context
            else None,
            parent_id=TaskId.model_validate(model.parent_id)
            if model.parent_id
            else None,
            output=TaskOutput.model_validate(model.output) if model.output else None,
            review_feedback=ReviewFeedback.model_validate(model.review_feedback)
            if model.review_feedback
            else None,
            acceptance_criteria=[
                Scenario.model_validate(ac) for ac in (model.acceptance_criteria or [])
            ],
            recurrence=None,  # Not currently in TaskModel
        )

    def _to_model(self, task: Task) -> TaskModel:
        model = self.session.get(TaskModel, task.id.value)

        if not model:
            model = TaskModel(id=task.id.value)

        return self._sync_to_model(task, model)

    def _sync(self, task: Task) -> None:
        model = self.session.get(TaskModel, task.id.value)

        if not model:
            return None

        self._sync_to_model(task, model)

    def _create_model(self, task: Task) -> TaskModel:
        model = TaskModel(id=task.id.value)
        return self._sync_to_model(task, model)

    def _sync_to_model(self, task: Task, model: TaskModel) -> TaskModel:

        model.project_id = task.project_id
        model.name = task.name
        model.description = task.description
        model.status = task.status.value
        model.scope_level = task.scope_level.value
        model.scope_context = (
            task.scope_context.model_dump(mode="json") if task.scope_context else None
        )
        model.completion_logic = task.completion_logic.value
        model.parent_id = task.parent_id.value if task.parent_id else None
        model.effort = task.effort.value
        model.base_value = task.base_value.value
        model.output = task.output.model_dump(mode="json") if task.output else None
        model.review_feedback = (
            task.review_feedback.model_dump(mode="json")
            if task.review_feedback
            else None
        )
        model.acceptance_criteria = [
            ac.model_dump(mode="json") for ac in task.acceptance_criteria
        ] or None

        # Handle dependencies
        dep_ids = [tid.value for tid in task.dependencies]
        if dep_ids:
            dep_stmt = select(TaskModel).where(TaskModel.id.in_(dep_ids))
            dependencies = self.session.execute(dep_stmt).scalars().all()
            model.dependencies = list(dependencies)
        else:
            model.dependencies = []

        return model

    def _track_task(self, task: Task) -> None:
        self._seen_tasks.add(task)
        