from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.review_task import ReviewTask
from task_graph.planning.application.dtos.review_task_command import ReviewTaskCommand
from task_graph.planning.application.dtos.review_task_result import ReviewTaskResult


@inject
def _review_task(
    cmd: ReviewTaskCommand, use_case: ReviewTask = Provide["planning.review_task"]
) -> ReviewTaskResult:
    return use_case.execute(cmd)


def review_task(cmd: ReviewTaskCommand) -> ReviewTaskResult:
    return _review_task(cmd)
