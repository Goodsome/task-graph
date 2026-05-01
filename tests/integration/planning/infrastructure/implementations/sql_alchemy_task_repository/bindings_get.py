import pytest
from sqlalchemy.orm import Session
from dataclasses import dataclass, field

from tests.factories.task_factory import TaskFactory, TaskOutputFactory, ScopeContextFactory
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import ScopeLevel
from task_graph.planning.domain.exceptions import TaskNotFoundError
from task_graph.planning.infrastructure.adapters.sql_alchemy_task_repository import (
    SqlAlchemyTaskRepository,
)


@dataclass
class GetBindings:
    session: Session
    repository: SqlAlchemyTaskRepository = field(init=False)
    _arranged_task: Task | None = field(default=None, init=False)
    _arranged_task_id: TaskId | None = field(default=None, init=False)
    _nonexistent_task_id: TaskId = field(init=False)
    _retrieved_task: Task | None = field(default=None, init=False)
    _get_result: Task | None = field(default=None, init=False)
    _captured_error: Exception | None = field(default=None, init=False)

    def __post_init__(self: "GetBindings") -> None:
        self.repository = SqlAlchemyTaskRepository(session=self.session)
        self._nonexistent_task_id = TaskId.create()

    # ─────────────────────────── BDD Interface ────────────────────────────

    def given(self, semantic_text: str) -> "GetBindings":
        match semantic_text:
            case "a Task with the given TaskId exists in the repository":
                self._arrange_existing_task()
            case "no Task with the given TaskId exists in the repository":
                self._arrange_nonexistent_id()
            case "a Task was previously saved with all attributes populated":
                self._arrange_fully_populated_task()
            case _:
                raise NotImplementedError(f"Unhandled given: {semantic_text}")
        return self

    def arrange_done(self) -> "GetBindings":
        return self

    def when(self, semantic_text: str) -> "GetBindings":
        match semantic_text:
            case "get is invoked with that TaskId":
                self._when_get_by_id()
            case "get is invoked with the Task's TaskId":
                self._when_get_by_id()
            case _:
                raise NotImplementedError(f"Unhandled when: {semantic_text}")
        return self

    def then(self, semantic_text: str) -> "GetBindings":
        match semantic_text:
            case "the complete Task is returned with all its attributes intact":
                self._then_returns_complete_task()
            case "TaskNotFoundError is raised":
                self._then_raises_not_found()
            case "the returned Task has identical attribute values including nested objects and value objects":
                self._then_returns_identical_task()
            case _:
                raise NotImplementedError(f"Unhandled then: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_existing_task(self) -> None:
        self._arranged_task = TaskFactory.build(
            project_id="test-project",
            name="Existing Task",
            description="A task that exists",
            scope_level=ScopeLevel.COMPONENT,
        )
        self.repository.save(self._arranged_task)
        self._arranged_task_id = self._arranged_task.id

    def _arrange_nonexistent_id(self) -> None:
        self._arranged_task_id = self._nonexistent_task_id

    def _arrange_fully_populated_task(self) -> None:
        self._arranged_task = TaskFactory.build(
            project_id="full-project",
            name="Fully Populated Task",
            description="Task with all fields set",
            scope_level=ScopeLevel.ARCHITECTURAL,
            scope_context=ScopeContextFactory.build(),
        )
        # PENDING -> READY -> IN_PROGRESS (required for set_output)
        self._arranged_task.mark_ready()
        self._arranged_task.claim()
        self._arranged_task.set_output(TaskOutputFactory.build())
        self.repository.save(self._arranged_task)
        self._arranged_task_id = self._arranged_task.id

    # ─────────────────────────── Act ────────────────────────────

    def _when_get_by_id(self) -> None:
        assert self._arranged_task_id is not None
        try:
            self._get_result = self.repository.get(self._arranged_task_id)
        except Exception as e:
            self._captured_error = e

    # ─────────────────────────── Assert ────────────────────────────

    def _then_returns_complete_task(self) -> None:
        assert self._arranged_task is not None
        self._retrieved_task = self.repository.get(self._arranged_task.id)
        assert self._retrieved_task is not None
        # 深度比对所有属性，自动覆盖所有新增字段
        assert self._retrieved_task.model_dump() == self._arranged_task.model_dump()

    def _then_raises_not_found(self) -> None:
        assert isinstance(self._captured_error, TaskNotFoundError)

    def _then_returns_identical_task(self) -> None:
        assert self._arranged_task is not None
        self._retrieved_task = self.repository.get(self._arranged_task.id)
        assert self._retrieved_task is not None
        # 全量深度比对，包含所有嵌套值对象、集合和新增字段
        assert self._retrieved_task.model_dump() == self._arranged_task.model_dump()


@pytest.fixture
def get_bindings(db_session: Session) -> GetBindings:
    return GetBindings(session=db_session)
