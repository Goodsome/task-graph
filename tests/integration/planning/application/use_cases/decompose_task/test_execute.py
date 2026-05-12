from tests.integration.planning.application.use_cases.decompose_task.bindings_execute import (
    ExecuteBindings,
    execute_bindings,
)

_ = execute_bindings


def test_explicit_dependency_persisted_with_correct_status(
    execute_bindings: ExecuteBindings,
) -> None:
    execute_bindings.given(
        "一个状态为 decomposing 的父任务存储在数据库中，其 output.sub_tasks 包含两个子任务定义且第二个子任务的 dependencies 包含第一个子任务的名称"
    ).arrange_done().when("执行 DecomposeTask 用例并提交事务").then(
        "从数据库查询应返回两个已创建的子任务，第一个子任务状态为 READY 且无依赖，第二个子任务状态为 BLOCKED 且其依赖列表包含第一个子任务的 TaskId"
    )

