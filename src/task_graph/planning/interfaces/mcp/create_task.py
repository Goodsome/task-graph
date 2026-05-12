from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.create_task import CreateTask
from task_graph.planning.application.dtos.create_task_result import CreateTaskResult
from task_graph.planning.application.dtos.create_task_command import CreateTaskCommand


@inject
def _create_task(
    cmd: CreateTaskCommand, use_case: CreateTask = Provide["planning.create_task"]
) -> CreateTaskResult:
    return use_case.execute(cmd)


def create_task(cmd: CreateTaskCommand) -> CreateTaskResult:
    """Create task"""
    return _create_task(cmd)
