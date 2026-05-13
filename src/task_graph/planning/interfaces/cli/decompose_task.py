import typer
from task_graph.planning.application.use_cases.decompose_task import DecomposeTask
from dependency_injector.wiring import Provide, inject
from typing import Annotated
from task_graph.planning.application.dtos.decompose_task_command import (
    DecomposeTaskCommand,
)
from task_graph.planning.application.dtos.decompose_task_result import (
    DecomposeTaskResult,
)

from .app import planning_app


@inject
def _decompose_task(
    cmd: DecomposeTaskCommand,
    use_case: DecomposeTask = Provide["planning.decompose_task"],
) -> DecomposeTaskResult:
    return use_case.execute(cmd)


@planning_app.command(name="decompose-task")
def decompose_task(
    task_id: Annotated[str, typer.Argument()],
) -> DecomposeTaskResult:
    cmd = DecomposeTaskCommand(
        task_id=task_id
    )
    return _decompose_task(
        cmd=cmd
    )
