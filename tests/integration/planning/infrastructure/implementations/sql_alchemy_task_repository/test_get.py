from tests.integration.planning.infrastructure.implementations.sql_alchemy_task_repository.bindings_get import (
    GetBindings,
    get_bindings,
)

_ = get_bindings


def test_get_returns_task_for_existing_id(get_bindings: GetBindings) -> None:
    get_bindings.given(
        "a Task with the given TaskId exists in the repository"
    ).arrange_done().when("get is invoked with that TaskId").then(
        "the complete Task is returned with all its attributes intact"
    )


def test_get_raises_not_found_for_nonexistent_id(get_bindings: GetBindings) -> None:
    get_bindings.given(
        "no Task with the given TaskId exists in the repository"
    ).arrange_done().when("get is invoked with that TaskId").then(
        "TaskNotFoundError is raised"
    )


def test_get_returns_fully_reconstituted_task(get_bindings: GetBindings) -> None:
    get_bindings.given(
        "a Task was previously saved with all attributes populated"
    ).arrange_done().when("get is invoked with the Task's TaskId").then(
        "the returned Task has identical attribute values including nested objects and value objects"
    )
