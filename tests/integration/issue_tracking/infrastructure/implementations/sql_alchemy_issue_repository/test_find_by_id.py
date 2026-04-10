from tests.integration.issue_tracking.infrastructure.implementations.sql_alchemy_issue_repository.bindings_find_by_id import (
    FindByIdBindings,
    find_by_id_bindings,
)

_ = find_by_id_bindings


def test_find_existing_issue_by_id(find_by_id_bindings: FindByIdBindings) -> None:
    find_by_id_bindings.given(
        "传入的issue_id对应的Issue在数据库中存在"
    ).arrange_done().when("调用find_by_id方法").then("返回对应的Issue聚合根实例")


def test_find_non_existent_issue_by_id(find_by_id_bindings: FindByIdBindings) -> None:
    find_by_id_bindings.given(
        "传入的issue_id对应的Issue在数据库中不存在"
    ).arrange_done().when("调用find_by_id方法").then("返回None")
