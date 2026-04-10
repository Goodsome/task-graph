from tests.integration.issue_tracking.infrastructure.implementations.sql_alchemy_issue_repository.bindings_save import (
    SaveBindings,
    save_bindings,
)

_ = save_bindings


def test_save_new_issue(save_bindings: SaveBindings) -> None:
    save_bindings.given("传入一个未持久化的Issue聚合根实例").arrange_done().when(
        "调用save方法"
    ).then("Issue实例被持久化到数据库，没有返回值")


def test_update_existing_issue(save_bindings: SaveBindings) -> None:
    save_bindings.given(
        "传入一个已在数据库中存在的Issue聚合根实例"
    ).arrange_done().when("调用save方法").then(
        "数据库中对应的Issue记录被更新，没有返回值"
    )
