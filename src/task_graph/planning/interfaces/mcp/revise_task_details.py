from task_graph.planning.application.use_cases.revise_task_details import (
    ReviseTaskDetails,
    ReviseTaskDetailsCommand,
    ReviseTaskDetailsResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _revise_task_details(
    cmd: ReviseTaskDetailsCommand,
    use_case: ReviseTaskDetails = Provide["planning.revise_task_details"],
) -> ReviseTaskDetailsResult:
    return use_case.execute(cmd)


def revise_task_details(cmd: ReviseTaskDetailsCommand) -> ReviseTaskDetailsResult:
    """update task details"""
    return _revise_task_details(cmd)
