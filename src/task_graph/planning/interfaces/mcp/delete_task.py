from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.delete_task import DeleteTask
from task_graph.planning.application.dtos.delete_task_result import DeleteTaskResult
from task_graph.planning.application.dtos.delete_task_command import DeleteTaskCommand


@inject
def _delete_task(
    cmd: DeleteTaskCommand, use_case: DeleteTask = Provide["planning.delete_task"]
) -> DeleteTaskResult:
    return use_case.execute(cmd)


def delete_task(cmd: DeleteTaskCommand) -> DeleteTaskResult:
    return _delete_task(cmd)
