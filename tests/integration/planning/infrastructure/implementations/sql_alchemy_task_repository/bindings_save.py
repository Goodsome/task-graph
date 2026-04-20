import pytest
from sqlalchemy.orm import Session
from dataclasses import dataclass, field

from tests.factories.task_factory import TaskFactory
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import ScopeLevel
from task_graph.planning.domain.value_objects.acceptance_criterion import AcceptanceCriterion
from task_graph.planning.infrastructure.repositories.sql_alchemy_task_repository import (
    SqlAlchemyTaskRepository,
)


@dataclass
class SaveBindings:
    session: Session
    repository: SqlAlchemyTaskRepository = field(init=False)
    _arranged_task: Task | None = field(default=None, init=False)
    _arranged_dependency_tasks: list[Task] = field(default_factory=list, init=False)
    _retrieved_task: Task | None = field(default=None, init=False)

    def __post_init__(self: "SaveBindings") -> None:
        self.repository = SqlAlchemyTaskRepository(session=self.session)

    # ─────────────────────────── BDD Interface ────────────────────────────

    def given(self, semantic_text: str) -> "SaveBindings":
        match semantic_text:
            case "a valid Task with a unique TaskId":
                self._arrange_valid_task()
            case "a Task already persisted in the repository":
                self._arrange_existing_task()
            case "a Task with a non-empty set of dependencies":
                self._arrange_task_with_dependencies()
            case "a Task with acceptance criteria":
                self._arrange_task_with_acceptance_criteria()
            case _:
                raise NotImplementedError(f"Unhandled given: {semantic_text}")
        return self

    def arrange_done(self) -> "SaveBindings":
        return self

    def when(self, semantic_text: str) -> "SaveBindings":
        match semantic_text:
            case "save is invoked with the Task":
                self._when_save_task()
            case "save is invoked again with the same Task":
                self._when_save_again()
            case _:
                raise NotImplementedError(f"Unhandled when: {semantic_text}")
        return self

    def then(self, semantic_text: str) -> "SaveBindings":
        match semantic_text:
            case "the Task can be retrieved from the repository by its TaskId":
                self._then_task_can_be_retrieved()
            case "no error is raised and the Task state remains unchanged":
                self._then_no_error_and_state_unchanged()
            case "the saved Task's dependencies are identical to the original set of TaskIds":
                self._then_dependencies_preserved()
            case "the saved Task's acceptance criteria are identical to the originals":
                self._then_acceptance_criteria_preserved()
            case _:
                raise NotImplementedError(f"Unhandled then: {semantic_text}")
        return self
        
    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_valid_task(self) -> None:
        self._arranged_task = TaskFactory.build(
            project_id="test-project",
            name="Test Task",
            description="A test task",
            scope_level=ScopeLevel.ATOMIC,
        )

    def _arrange_existing_task(self) -> None:
        self._arranged_task = TaskFactory.build(
            project_id="test-project",
            name="Existing Task",
            description="An existing task",
            scope_level=ScopeLevel.ATOMIC,
        )
        self.repository.save(self._arranged_task)

    def _arrange_task_with_dependencies(self) -> None:
        dep_task_1 = TaskFactory.build(
            project_id="test-project",
            name="Dependency Task 1",
            description="First dependency",
            scope_level=ScopeLevel.ATOMIC,
        )
        dep_task_2 = TaskFactory.build(
            project_id="test-project",
            name="Dependency Task 2",
            description="Second dependency",
            scope_level=ScopeLevel.ATOMIC,
        )
        self.repository.save(dep_task_1)
        self.repository.save(dep_task_2)
        self._arranged_dependency_tasks = [dep_task_1, dep_task_2]

        self._arranged_task = TaskFactory.build(
            project_id="test-project",
            name="Task with Dependencies",
            description="A task that depends on others",
            dependencies={dep_task_1.id, dep_task_2.id},
            scope_level=ScopeLevel.ATOMIC,
        )

    def _arrange_task_with_acceptance_criteria(self) -> None:
        criteria = [
            AcceptanceCriterion(
                title="任务创建后可查询",
                given="项目已存在",
                when="调用 create_task",
                then="可通过任务 ID 查询到该任务",
                test_type="integration",
            ),
            AcceptanceCriterion(
                title="任务状态初始为 PENDING",
                given="新任务已创建",
                when="读取任务状态",
                then="状态为 PENDING",
                test_type="unit",
            ),
        ]
        self._arranged_task = TaskFactory.build(
            project_id="test-project",
            name="Task with Acceptance Criteria",
            description="A task with BDD acceptance criteria",
            scope_level=ScopeLevel.ATOMIC,
            acceptance_criteria=criteria,
        )

    # ─────────────────────────── Act ────────────────────────────

    def _when_save_task(self) -> None:
        assert self._arranged_task is not None
        self.repository.save(self._arranged_task)

    def _when_save_again(self) -> None:
        assert self._arranged_task is not None
        self.repository.save(self._arranged_task)

    # ─────────────────────────── Assert ────────────────────────────

    def _then_task_can_be_retrieved(self) -> None:
        assert self._arranged_task is not None
        self._retrieved_task = self.repository.get(self._arranged_task.id)
        assert self._retrieved_task is not None
        # 全量深度比对所有属性，确保没有字段遗漏
        assert self._retrieved_task.model_dump() == self._arranged_task.model_dump()

    def _then_no_error_and_state_unchanged(self) -> None:
        assert self._arranged_task is not None
        # Save again should not raise
        self.repository.save(self._arranged_task)
        self._retrieved_task = self.repository.get(self._arranged_task.id)
        assert self._retrieved_task is not None
        # 验证幂等性：重复保存后所有状态完全不变
        assert self._retrieved_task.model_dump() == self._arranged_task.model_dump()

    def _then_dependencies_preserved(self) -> None:
        assert self._arranged_task is not None
        self._retrieved_task = self.repository.get(self._arranged_task.id)
        assert self._retrieved_task is not None
        # 专门验证依赖关系正确性
        original_ids = {str(d) for d in self._arranged_task.dependencies}
        retrieved_ids = {str(d) for d in self._retrieved_task.dependencies}
        assert original_ids == retrieved_ids
        # 同时全量比对其他属性，确保依赖保存时没有破坏其他字段
        assert self._retrieved_task.model_dump() == self._arranged_task.model_dump()

    def _then_acceptance_criteria_preserved(self) -> None:
        assert self._arranged_task is not None
        self._retrieved_task = self.repository.get(self._arranged_task.id)
        assert self._retrieved_task is not None
        # 验证验收标准数量与内容完全一致
        original_criteria = [ac.model_dump() for ac in self._arranged_task.acceptance_criteria]
        retrieved_criteria = [ac.model_dump() for ac in self._retrieved_task.acceptance_criteria]
        assert retrieved_criteria == original_criteria
        # 全量比对确保其他字段未受影响
        assert self._retrieved_task.model_dump() == self._arranged_task.model_dump()


@pytest.fixture
def save_bindings(db_session: Session) -> SaveBindings:
    return SaveBindings(session=db_session)
