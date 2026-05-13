import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.delete_task import DeleteTask
from task_graph.planning.application.dtos.delete_task_result import DeleteTaskResult
from task_graph.planning.application.dtos.delete_task_command import DeleteTaskCommand

console = Console()


@inject
def _delete_task(
    cmd: DeleteTaskCommand,
    use_case: DeleteTask = Provide["planning_container.delete_task"],
) -> DeleteTaskResult:
    return use_case.execute(cmd)


def delete_task(task_id: Annotated[str, typer.Argument()]) -> DeleteTaskResult:
    """删除指定的任务。"""
    cmd = DeleteTaskCommand(task_id=task_id)
    result = _delete_task(cmd)
    if result.success:
        console.print("[green]✓ 任务已删除[/green]")
    else:
        console.print(f"[red]✗ 删除失败: {result.error}[/red]")
        raise typer.Exit(1)
    return result
