from tests.integration.issue_tracking.infrastructure.implementations.sql_alchemy_issue_repository.bindings_count import (
    CountBindings,
    count_bindings,
)

_ = count_bindings


def test_count_all_issues(count_bindings: CountBindings) -> None:
    count_bindings.given("不传入任何过滤参数").arrange_done().when(
        "调用count方法"
    ).then("返回数据库中所有Issue的总数量")


def test_count_issues_with_filters(count_bindings: CountBindings) -> None:
    count_bindings.given("传入status或issue_type过滤参数").arrange_done().when(
        "调用count方法"
    ).then("返回符合过滤条件的Issue数量")
