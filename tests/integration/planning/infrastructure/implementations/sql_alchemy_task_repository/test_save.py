from tests.integration.planning.infrastructure.implementations.sql_alchemy_task_repository.bindings_save import (
    SaveBindings,
    save_bindings,
)

_ = save_bindings


def test_save_persists_task_for_subsequent_retrieval(
    save_bindings: SaveBindings,
) -> None:
    save_bindings.given("a valid Task with a unique TaskId").arrange_done().when(
        "save is invoked with the Task"
    ).then("the Task can be retrieved from the repository by its TaskId")


def test_save_is_idempotent_for_existing_task(save_bindings: SaveBindings) -> None:
    save_bindings.given(
        "a Task already persisted in the repository"
    ).arrange_done().when("save is invoked again with the same Task").then(
        "no error is raised and the Task state remains unchanged"
    )


def test_save_preserves_task_dependencies(save_bindings: SaveBindings) -> None:
    save_bindings.given(
        "a Task with a non-empty set of dependencies"
    ).arrange_done().when("save is invoked with the Task").then(
        "the saved Task's dependencies are identical to the original set of TaskIds"
    )
