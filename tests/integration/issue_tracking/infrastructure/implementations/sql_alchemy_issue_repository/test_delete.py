from tests.integration.issue_tracking.infrastructure.implementations.sql_alchemy_issue_repository.bindings_delete import (
    DeleteBindings,
    delete_bindings,
)

_ = delete_bindings


def test_delete_existing_issue(delete_bindings: DeleteBindings) -> None:
    delete_bindings.given(
        "传入的issue_id对应的Issue在数据库中存在"
    ).arrange_done().when("调用delete方法").then("Issue被从数据库中删除，返回True")


def test_delete_non_existent_issue(delete_bindings: DeleteBindings) -> None:
    delete_bindings.given(
        "传入的issue_id对应的Issue在数据库中不存在"
    ).arrange_done().when("调用delete方法").then("数据库没有变化，返回False")
