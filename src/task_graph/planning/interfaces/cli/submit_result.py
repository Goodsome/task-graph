"""提交任务执行结果"""
from typing import Optional

import typer
from rich.console import Console

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.submit_task_result import SubmitTaskResultCommand

container = Container()
console = Console()


def submit_result(
    task_id: str = typer.Argument(..., help="任务ID"),
    summary: str = typer.Option(..., "--summary", "-s", help="执行摘要"),
    artifacts: Optional[list[str]] = typer.Option(None, "--artifact", "-a", help="产出物路径 (可多次指定)"),
    error: Optional[str] = typer.Option(None, "--error", "-e", help="错误信息 (如果任务失败)"),
):
    """
    提交任务执行结果。

    包括摘要、产出物和可选的错误信息。
    """
    cmd = SubmitTaskResultCommand(
        task_id=task_id,
        summary=summary,
        artifacts=artifacts or [],
        error=error,
    )

    use_case = container.submit_task_result()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 结果已提交[/green]")
    else:
        console.print(f"[red]✗ 提交失败: {result.error}[/red]")
        raise typer.Exit(1)