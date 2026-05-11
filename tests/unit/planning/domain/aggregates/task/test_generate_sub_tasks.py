from tests.unit.planning.domain.aggregates.task.bindings_generate_sub_tasks import (
    GenerateSubTasksBindings,
    generate_sub_tasks_bindings,
)

_ = generate_sub_tasks_bindings


def test_implicit_serial_dependency_when_no_explicit(
    generate_sub_tasks_bindings: GenerateSubTasksBindings,
) -> None:
    generate_sub_tasks_bindings.given(
        "SubTaskInfo 列表中所有子任务均未设置 dependencies"
    ).arrange_done().when("调用 generate_sub_tasks() 方法").then(
        "第一个子任务无依赖且状态为 READY，后续每个子任务隐式依赖列表中前一个子任务"
    )


def test_explicit_dependency_resolved_by_name(
    generate_sub_tasks_bindings: GenerateSubTasksBindings,
) -> None:
    generate_sub_tasks_bindings.given(
        "子任务 Frontend 的 dependencies 包含 {Backend}，Backend 无依赖"
    ).arrange_done().when("调用 generate_sub_tasks() 方法").then(
        "Frontend 的 dependencies 应包含 Backend 对应的 TaskId 且状态为 BLOCKED"
    )


def test_mixed_explicit_and_implicit_dependency(
    generate_sub_tasks_bindings: GenerateSubTasksBindings,
) -> None:
    generate_sub_tasks_bindings.given(
        "子任务列表为 [A, B, C]，B 显式依赖 A，C 未设置 dependencies"
    ).arrange_done().when("调用 generate_sub_tasks() 方法").then(
        "A 无依赖状态为 READY，B 显式依赖 A 状态为 BLOCKED，C 隐式依赖 B 状态为 BLOCKED"
    )


def test_invalid_dependency_name_raises_error(
    generate_sub_tasks_bindings: GenerateSubTasksBindings,
) -> None:
    generate_sub_tasks_bindings.given(
        "子任务 Frontend 的 dependencies 包含不存在的子任务名 NonExistent"
    ).arrange_done().when("调用 generate_sub_tasks() 方法").then(
        "应抛出 ValueError 提示依赖的子任务名不存在"
    )


def test_first_subtask_ready_without_explicit_dependency(
    generate_sub_tasks_bindings: GenerateSubTasksBindings,
) -> None:
    generate_sub_tasks_bindings.given(
        "第一个子任务未设置 dependencies 且列表中存在后续子任务"
    ).arrange_done().when("调用 generate_sub_tasks() 方法").then(
        "第一个子任务的 dependencies 为空且状态为 READY"
    )


def test_two_phase_processing_with_name_to_id_mapping(
    generate_sub_tasks_bindings: GenerateSubTasksBindings,
) -> None:
    generate_sub_tasks_bindings.given(
        "包含多个 SubTaskInfo 的列表"
    ).arrange_done().when("调用 generate_sub_tasks() 方法").then(
        "第一阶段创建所有 Task 实例并建立 name 到 TaskId 的映射表，第二阶段解析 dependencies 中的 name 为对应 TaskId"
    )
