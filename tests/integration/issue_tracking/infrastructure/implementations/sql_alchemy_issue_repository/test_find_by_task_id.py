from tests.integration.issue_tracking.infrastructure.implementations.sql_alchemy_issue_repository.bindings_find_by_task_id import (
    FindByTaskIdBindings,
    find_by_task_id_bindings,
)

_ = find_by_task_id_bindings


def test_find_issues_linked_to_task(
    find_by_task_id_bindings: FindByTaskIdBindings,
) -> None:
    find_by_task_id_bindings.given("传入有效的task_id").arrange_done().when(
        "调用find_by_task_id方法"
    ).then("返回所有与该task_id关联的Issue列表")


def test_find_issues_no_linked_to_task(
    find_by_task_id_bindings: FindByTaskIdBindings,
) -> None:
    find_by_task_id_bindings.given(
        "传入的task_id没有关联任何Issue"
    ).arrange_done().when("调用find_by_task_id方法").then("返回空列表")
