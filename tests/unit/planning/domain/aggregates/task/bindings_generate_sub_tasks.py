from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

import pytest

from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import CompletionLogic, ScopeLevel, TaskStatus
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.value_score import ValueScore


def _make_parent(sub_tasks: list[SubTaskInfo]) -> Task:
    """创建一个处于 DECOMPOSING 状态的父任务。"""
    parent = Task.create(
        project_id="proj-test",
        name="Parent",
        description="Parent task for decomposition",
        effort=StoryPoint.create(8),
        base_value=ValueScore.create(100.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        scope_level=ScopeLevel.ARCHITECTURE,
    )
    parent.status = TaskStatus.IN_PROGRESS
    parent.set_output(
        TaskOutput(summary="Needs decomposition", artifacts=[], sub_tasks=sub_tasks)
    )
    parent.review(approved=True, feedback="Decompose this task")
    return parent


@dataclass
class GenerateSubTasksBindings:
    _last_step_type: str | None = None
    _sub_task_infos: list[SubTaskInfo] = field(default_factory=list)
    _parent: Task | None = None
    _result: list[Task] = field(default_factory=list)
    _raised_exception: Exception | None = None

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case "SubTaskInfo 列表中所有子任务均未设置 dependencies":
                self._sub_task_infos = [
                    SubTaskInfo(
                        name="A",
                        description="Task A",
                        effort=StoryPoint.create(1),
                        base_value=ValueScore.create(10.0),
                    ),
                    SubTaskInfo(
                        name="B",
                        description="Task B",
                        effort=StoryPoint.create(2),
                        base_value=ValueScore.create(20.0),
                    ),
                    SubTaskInfo(
                        name="C",
                        description="Task C",
                        effort=StoryPoint.create(3),
                        base_value=ValueScore.create(30.0),
                    ),
                ]
                self._parent = _make_parent(self._sub_task_infos)

            case "子任务 Frontend 的 dependencies 包含 {Backend}，Backend 无依赖":
                self._sub_task_infos = [
                    SubTaskInfo(
                        name="Backend",
                        description="Backend service",
                        effort=StoryPoint.create(3),
                        base_value=ValueScore.create(50.0),
                    ),
                    SubTaskInfo(
                        name="Frontend",
                        description="Frontend UI",
                        effort=StoryPoint.create(2),
                        base_value=ValueScore.create(40.0),
                        dependencies={"Backend"},
                    ),
                ]
                self._parent = _make_parent(self._sub_task_infos)

            case "子任务列表为 [A, B, C]，B 显式依赖 A，C 未设置 dependencies":
                self._sub_task_infos = [
                    SubTaskInfo(
                        name="A",
                        description="Task A",
                        effort=StoryPoint.create(1),
                        base_value=ValueScore.create(10.0),
                    ),
                    SubTaskInfo(
                        name="B",
                        description="Task B",
                        effort=StoryPoint.create(2),
                        base_value=ValueScore.create(20.0),
                        dependencies={"A"},
                    ),
                    SubTaskInfo(
                        name="C",
                        description="Task C",
                        effort=StoryPoint.create(3),
                        base_value=ValueScore.create(30.0),
                    ),
                ]
                self._parent = _make_parent(self._sub_task_infos)

            case "子任务 Frontend 的 dependencies 包含不存在的子任务名 NonExistent":
                self._sub_task_infos = [
                    SubTaskInfo(
                        name="Frontend",
                        description="Frontend UI",
                        effort=StoryPoint.create(2),
                        base_value=ValueScore.create(40.0),
                        dependencies={"NonExistent"},
                    ),
                ]
                self._parent = _make_parent(self._sub_task_infos)

            case "第一个子任务未设置 dependencies 且列表中存在后续子任务":
                self._sub_task_infos = [
                    SubTaskInfo(
                        name="First",
                        description="First task",
                        effort=StoryPoint.create(1),
                        base_value=ValueScore.create(10.0),
                    ),
                    SubTaskInfo(
                        name="Second",
                        description="Second task",
                        effort=StoryPoint.create(2),
                        base_value=ValueScore.create(20.0),
                    ),
                ]
                self._parent = _make_parent(self._sub_task_infos)

            case "包含多个 SubTaskInfo 的列表":
                self._sub_task_infos = [
                    SubTaskInfo(
                        name="X",
                        description="Task X",
                        effort=StoryPoint.create(1),
                        base_value=ValueScore.create(10.0),
                    ),
                    SubTaskInfo(
                        name="Y",
                        description="Task Y",
                        effort=StoryPoint.create(2),
                        base_value=ValueScore.create(20.0),
                        dependencies={"X"},
                    ),
                ]
                self._parent = _make_parent(self._sub_task_infos)

            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case "调用 generate_sub_tasks() 方法":
                assert self._parent is not None
                try:
                    self._result = self._parent.generate_sub_tasks()
                except Exception as exc:
                    self._raised_exception = exc
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case "第一个子任务无依赖且状态为 READY，后续每个子任务隐式依赖列表中前一个子任务":
                self._assert_implicit_serial_dependency()
            case (
                "Frontend 的 dependencies 应包含 Backend 对应的 TaskId 且状态为 BLOCKED"
            ):
                self._assert_explicit_dependency_resolved()
            case "A 无依赖状态为 READY，B 显式依赖 A 状态为 BLOCKED，C 隐式依赖 B 状态为 BLOCKED":
                self._assert_mixed_dependency()
            case "应抛出 ValueError 提示依赖的子任务名不存在":
                self._assert_invalid_dependency_raises()
            case "第一个子任务的 dependencies 为空且状态为 READY":
                self._assert_first_subtask_ready()
            case "第一阶段创建所有 Task 实例并建立 name 到 TaskId 的映射表，第二阶段解析 dependencies 中的 name 为对应 TaskId":
                self._assert_two_phase_processing()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ── 私有断言方法 ──────────────────────────────────────────────

    def _assert_implicit_serial_dependency(self) -> None:
        """场景: 无显式依赖时子任务串行依赖。"""
        assert len(self._result) == 3

        # 第一个子任务: 无依赖, READY
        first = self._result[0]
        assert first.name == "Parent[A]"
        assert first.dependencies == set()
        assert first.status == TaskStatus.READY

        # 第二个子任务: 隐式依赖第一个, BLOCKED
        second = self._result[1]
        assert second.name == "Parent[B]"
        assert first.id in second.dependencies
        assert second.status == TaskStatus.BLOCKED

        # 第三个子任务: 隐式依赖第二个, BLOCKED
        third = self._result[2]
        assert third.name == "Parent[C]"
        assert second.id in third.dependencies
        assert third.status == TaskStatus.BLOCKED

    def _assert_explicit_dependency_resolved(self) -> None:
        """场景: 显式指定依赖时按 name 解析为 TaskId。"""
        assert len(self._result) == 2
        by_name = {t.name.split("[")[1].rstrip("]"): t for t in self._result}

        backend = by_name["Backend"]
        frontend = by_name["Frontend"]

        assert backend.dependencies == set()
        assert backend.status == TaskStatus.READY

        assert backend.id in frontend.dependencies
        assert frontend.status == TaskStatus.BLOCKED

    def _assert_mixed_dependency(self) -> None:
        """场景: 混合显式与隐式依赖。"""
        assert len(self._result) == 3
        by_name = {t.name.split("[")[1].rstrip("]"): t for t in self._result}

        a = by_name["A"]
        b = by_name["B"]
        c = by_name["C"]

        # A: 无依赖, READY
        assert a.dependencies == set()
        assert a.status == TaskStatus.READY

        # B: 显式依赖 A, BLOCKED
        assert a.id in b.dependencies
        assert b.status == TaskStatus.BLOCKED

        # C: 隐式依赖 B（前一个子任务）, BLOCKED
        assert b.id in c.dependencies
        assert c.status == TaskStatus.BLOCKED

    def _assert_invalid_dependency_raises(self) -> None:
        """场景: 依赖 name 不存在时抛出 ValueError。"""
        assert self._raised_exception is not None
        assert isinstance(self._raised_exception, ValueError)

    def _assert_first_subtask_ready(self) -> None:
        """场景: 第一个子任务无显式依赖时为 READY。"""
        assert len(self._result) >= 1
        first = self._result[0]
        assert first.dependencies == set()
        assert first.status == TaskStatus.READY

    def _assert_two_phase_processing(self) -> None:
        """场景: 两阶段处理与 name→TaskId 映射。"""
        assert len(self._result) == 2
        by_name = {t.name.split("[")[1].rstrip("]"): t for t in self._result}

        x_task = by_name["X"]
        y_task = by_name["Y"]

        # 第一阶段: 所有任务均已创建
        assert x_task.id is not None
        assert y_task.id is not None
        assert x_task.id != y_task.id

        # 第二阶段: Y 的 name 依赖 "X" 已解析为 TaskId
        assert x_task.id in y_task.dependencies

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


@pytest.fixture
def generate_sub_tasks_bindings() -> GenerateSubTasksBindings:
    return GenerateSubTasksBindings()
