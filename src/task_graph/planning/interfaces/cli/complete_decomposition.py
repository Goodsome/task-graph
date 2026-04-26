"""完成任务分解"""

from typing import Annotated

import typer
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from task_graph.planning.application.use_cases.complete_decomposition import (
    CompleteDecompositionCommand,
    CompleteDecomposition,
    CompleteDecompositionResult,
)
from task_graph.planning.interfaces.cli.app import planning_app

console = Console()


@inject
def _complete_decomposition(
    cmd: CompleteDecompositionCommand,
    use_case: CompleteDecomposition = Provide["planning.complete_decomposition"],
) -> CompleteDecompositionResult:
    return use_case.execute(cmd)


@planning_app.command(name="complete-decomposition")
def complete_decomposition(
    task_id: Annotated[str, typer.Argument(..., help="要完成任务分解的任务ID")],
) -> None:
    """
    完成任务分解。当任务处于 DECOMPOSING 状态且所有子任务都已完成时，
    将其标记为 DONE。
    """
    cmd = CompleteDecompositionCommand(task_id=task_id)
    result = _complete_decomposition(cmd)

    if result.status == "success":
        console.print("[green]✓ 任务分解已完成[/green]")
        console.print(f"  Task ID: {result.task_id}")
    elif result.status == "skipped":
        console.print(f"[yellow]⊘ 已跳过: {result.message}[/yellow]")
    else:
        console.print(f"[red]✗ 失败: {result.message}[/red]")
        raise typer.Exit(1)
