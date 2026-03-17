"""修改任务的详细信息"""
from typing import Optional

import typer
from rich.console import Console

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.revise_task_details import ReviseTaskDetailsCommand

container = Container()
console = Console()


def revise_task(
    task_id: str = typer.Argument(..., help="任务ID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="新名称"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="新描述"),
    effort: Optional[int] = typer.Option(None, "--effort", "-e", help="新工作量"),
    base_value: Optional[float] = typer.Option(None, "--value", "-v", help="新价值评分"),
):
    """
    修改任务的详细信息。

    只需指定要修改的字段，其他字段保持不变。
    """
    cmd = ReviseTaskDetailsCommand(
        task_id=task_id,
        name=name,
        description=description,
        effort=effort,
        base_value=base_value,
    )

    use_case = container.revise_task_details()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 任务已更新[/green]")
    else:
        console.print(f"[red]✗ 更新失败: {result.error}[/red]")
        raise typer.Exit(1)