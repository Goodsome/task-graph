import pytest
from dataclasses import dataclass, field
from typing import Self, cast
from unittest.mock import MagicMock

from sqlalchemy.orm import Session, sessionmaker

from tests.factories.task_factory import TaskFactory
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import ScopeLevel, TaskStatus
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.infrastructure.adapters.sql_alchemy_task_repository import (
    SqlAlchemyTaskRepository,
)
from task_graph.shared.application.ports.event_publisher import EventPublisher
from task_graph.shared.infrastructure.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from task_graph.planning.application.use_cases.decompose_task import DecomposeTask
from task_graph.planning.application.dtos.decompose_task_command import (
    DecomposeTaskCommand,
)
from task_graph.planning.application.dtos.decompose_task_result import (
    DecomposeTaskResult,
)


_SUB_TASK_ALPHA = "alpha"
_SUB_TASK_BETA = "beta"

_SEMANTIC_GIVEN_PARENT_IN_DB = (
    "一个状态为 decomposing 的父任务存储在数据库中，"
    "其 output.sub_tasks 包含两个子任务定义"
    "且第二个子任务的 dependencies 包含第一个子任务的名称"
)
_SEMANTIC_GIVEN_EXPLICIT_DEP = (
    "父任务的 output.sub_tasks 中第二个子任务显式依赖第一个子任务"
)
_SEMANTIC_WHEN_EXECUTE = "执行 DecomposeTask 用例并提交事务"
_SEMANTIC_WHEN_EXECUTE_ROUNDTRIP = (
    "执行 DecomposeTask 用例使子任务持久化到数据库后重新读取"
)
_SEMANTIC_THEN_PERSISTED = (
    "从数据库查询应返回两个已创建的子任务，"
    "第一个子任务状态为 READY 且无依赖，"
    "第二个子任务状态为 BLOCKED 且其依赖列表包含第一个子任务的 TaskId"
)
_SEMANTIC_THEN_ROUNDTRIP = (
    "第二个子任务的依赖集合应包含第一个子任务的 TaskId，"
    "确保 name 到 TaskId 的解析结果在数据库持久化后保持完整"
)


@dataclass
class ExecuteBindings:
    """BDD bindings for DecomposeTask integration tests.

    Orchestrates a real SqlAlchemyUnitOfWork and SqlAlchemyTaskRepository
    against a test-managed database session to verify that the DecomposeTask
    use case correctly persists sub-tasks with explicit dependencies.
    """

    db_session: Session
    _last_step_type: str | None = field(default=None, init=False)
    _repository: SqlAlchemyTaskRepository = field(init=False)
    _uow: SqlAlchemyUnitOfWork[TaskRepository] = field(init=False)
    _parent_task: Task = field(init=False)
    _result: DecomposeTaskResult = field(init=False)
    _sub_tasks_by_name: dict[str, Task] = field(default_factory=dict, init=False)

    def __post_init__(self: Self) -> None:
        self._repository = SqlAlchemyTaskRepository(session=self.db_session)
        session_factory = self._build_session_factory()
        self._uow = cast(
            SqlAlchemyUnitOfWork[TaskRepository],
            SqlAlchemyUnitOfWork(
                session_factory=session_factory,
                repository_factory=lambda session: SqlAlchemyTaskRepository(
                    session=session
                ),
                event_publisher_factory=lambda session: MagicMock(spec=EventPublisher),
            ),
        )

    def _build_session_factory(self: Self) -> sessionmaker[Session]:
        """Create a sessionmaker bound to the test's connection.

        Ensures the UnitOfWork operates on the same transaction as the
        test fixture, so committed data is visible within the test and
        rolled back on teardown.
        """
        connection = self.db_session.connection()
        return sessionmaker(bind=connection)

    # ─────────────────────────── BDD Interface ────────────────────────────

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case _ if semantic_text == _SEMANTIC_GIVEN_PARENT_IN_DB:
                self._arrange_decomposing_parent_with_explicit_deps()
            case _ if semantic_text == _SEMANTIC_GIVEN_EXPLICIT_DEP:
                self._arrange_decomposing_parent_with_explicit_deps()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        self.db_session.flush()
        return self

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case _ if semantic_text == _SEMANTIC_WHEN_EXECUTE:
                self._act_execute_decompose_task()
            case _ if semantic_text == _SEMANTIC_WHEN_EXECUTE_ROUNDTRIP:
                self._act_execute_decompose_task()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case _ if semantic_text == _SEMANTIC_THEN_PERSISTED:
                self._assert_sub_tasks_persisted_with_correct_status()
            case _ if semantic_text == _SEMANTIC_THEN_ROUNDTRIP:
                self._assert_dependency_roundtrip_integrity()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    def and_(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    def but(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_decomposing_parent_with_explicit_deps(self: Self) -> None:
        """Create a DECOMPOSING parent task with two sub-tasks.

        The second sub-task has an explicit dependency on the first by name.
        The parent task is persisted to the database before execution.
        """
        parent_output = self._build_parent_output()
        self._parent_task = self._create_decomposing_parent(parent_output)
        self._repository.save(self._parent_task)

    def _build_parent_output(self: Self) -> TaskOutput:
        """Build TaskOutput containing two SubTaskInfo with explicit dependency."""
        alpha_info = SubTaskInfo(
            name=_SUB_TASK_ALPHA,
            description="First sub-task (no dependencies)",
            effort=StoryPoint.create(3),
            base_value=ValueScore.create(5.0),
        )
        beta_info = SubTaskInfo(
            name=_SUB_TASK_BETA,
            description="Second sub-task (depends on alpha)",
            effort=StoryPoint.create(5),
            base_value=ValueScore.create(8.0),
            dependencies={_SUB_TASK_ALPHA},
        )
        return TaskOutput(
            summary="Parent output with explicit dependency sub-tasks",
            artifacts=[],
            sub_tasks=[alpha_info, beta_info],
        )

    def _create_decomposing_parent(self, output: TaskOutput) -> Task:
        """Create a Task in DECOMPOSING status with the given output.

        Uses Task.create() factory then forces status to DECOMPOSING
        (skipping the REVIEWING gate for test simplicity).
        """
        parent = TaskFactory.build(
            project_id="test-project",
            name="Parent Task",
            description="A task to be decomposed",
            scope_level=ScopeLevel.ARCHITECTURE,
            status=TaskStatus.DECOMPOSING,
            output=output,
        )
        return parent

    # ─────────────────────────── Act ────────────────────────────

    def _act_execute_decompose_task(self: Self) -> None:
        """Execute the DecomposeTask use case with a real UnitOfWork."""
        use_case = DecomposeTask(uow=self._uow)
        cmd = DecomposeTaskCommand(task_id=str(self._parent_task.id))
        self._result = use_case.execute(cmd)

        self._load_sub_tasks_by_name()

    def _load_sub_tasks_by_name(self: Self) -> None:
        """Query persisted sub-tasks and index them by name suffix."""
        assert self._result.success, f"DecomposeTask failed: {self._result.error}"

        self._sub_tasks_by_name = {}
        for sub_task_id_str in self._result.sub_task_ids:
            sub_task = self._repository.get(TaskId.reconstitute(sub_task_id_str))
            name_suffix = self._extract_name_suffix(sub_task.name)
            self._sub_tasks_by_name[name_suffix] = sub_task

    def _extract_name_suffix(self, full_name: str) -> str:
        """Extract sub-task name suffix from 'Parent[Suffix]' format."""
        start = full_name.find("[")
        end = full_name.find("]")
        if start == -1 or end == -1:
            return full_name
        return full_name[start + 1 : end]

    # ─────────────────────────── Assert ────────────────────────────

    def _assert_sub_tasks_persisted_with_correct_status(self: Self) -> None:
        """Assert exactly 2 sub-tasks persisted with correct statuses and deps.

        - alpha: READY, no dependencies
        - beta: BLOCKED, depends on alpha's TaskId
        """
        assert len(self._result.sub_task_ids) == 2, (
            f"Expected 2 sub-tasks, got {len(self._result.sub_task_ids)}"
        )

        alpha = self._sub_tasks_by_name[_SUB_TASK_ALPHA]
        beta = self._sub_tasks_by_name[_SUB_TASK_BETA]

        self._assert_ready_with_no_deps(alpha)
        self._assert_blocked_with_dep_on(beta, alpha.id)

    def _assert_dependency_roundtrip_integrity(self: Self) -> None:
        """Assert name→TaskId resolution survives DB persistence round-trip.

        After DecomposeTask persists sub-tasks, re-reading beta from the
        database must show its dependency resolved to alpha's TaskId.
        """
        alpha = self._sub_tasks_by_name[_SUB_TASK_ALPHA]
        beta = self._sub_tasks_by_name[_SUB_TASK_BETA]

        self._assert_blocked_with_dep_on(beta, alpha.id)

    def _assert_ready_with_no_deps(self, task: Task) -> None:
        """Assert a task is READY with an empty dependency set."""
        assert task.status == TaskStatus.READY, f"Expected READY, got {task.status}"
        assert len(task.dependencies) == 0, (
            f"Expected no dependencies, got {task.dependencies}"
        )

    def _assert_blocked_with_dep_on(self, task: Task, expected_dep_id: TaskId) -> None:
        """Assert a task is BLOCKED with expected_dep_id in its dependencies."""
        assert task.status == TaskStatus.BLOCKED, f"Expected BLOCKED, got {task.status}"
        assert expected_dep_id in task.dependencies, (
            f"Expected {expected_dep_id} in dependencies, got {task.dependencies}"
        )


@pytest.fixture
def execute_bindings(db_session: Session) -> ExecuteBindings:
    return ExecuteBindings(db_session=db_session)
