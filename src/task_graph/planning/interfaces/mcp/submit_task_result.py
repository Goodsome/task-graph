from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.submit_task_result import (
    SubmitTaskResult,
)
from task_graph.planning.application.dtos.submit_task_result_command import (
    SubmitTaskResultCommand,
)
from task_graph.planning.application.dtos.submit_task_result_result import (
    SubmitTaskResultResult,
)


@inject
def _submit_task_result(
    cmd: SubmitTaskResultCommand,
    use_case: SubmitTaskResult = Provide["planning.submit_task_result"],
) -> SubmitTaskResultResult:
    return use_case.execute(cmd)


def submit_task_result(cmd: SubmitTaskResultCommand) -> SubmitTaskResultResult:
    """Submit task execution result with artifacts and optional error. Updates task.output."""
    return _submit_task_result(cmd)
