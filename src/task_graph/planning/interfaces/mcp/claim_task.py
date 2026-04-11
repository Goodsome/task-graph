from task_graph.planning.application.use_cases.claim_task import (
    ClaimTask,
    ClaimTaskCommand,
    ClaimTaskResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _claim_task(
    cmd: ClaimTaskCommand, use_case: ClaimTask = Provide["planning.claim_task"]
) -> ClaimTaskResult:
    return use_case.execute(cmd)


def claim_task(cmd: ClaimTaskCommand) -> ClaimTaskResult:
    return _claim_task(cmd)
