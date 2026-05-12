from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.update_task_status import (
    UpdateTaskStatus,
)
from task_graph.planning.application.dtos.update_task_status_result import (
    UpdateTaskStatusResult,
)
from task_graph.planning.application.dtos.update_task_status_command import (
    UpdateTaskStatusCommand,
)


@inject
def _update_task_status(
    cmd: UpdateTaskStatusCommand,
    use_case: UpdateTaskStatus = Provide["planning.update_task_status"],
) -> UpdateTaskStatusResult:
    return use_case.execute(cmd)


def update_task_status(cmd: UpdateTaskStatusCommand) -> UpdateTaskStatusResult:
    """Updates a task's status and triggers chain reactions for dependents."""
    return _update_task_status(cmd)
