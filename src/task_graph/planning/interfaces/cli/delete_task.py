"""删除指定的任务"""
import typer
from rich.console import Console

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.delete_task import DeleteTaskCommand

container = Container()
console = Console()


def delete_task(
    task_id: str = typer.Argument(..., help="要删除的任务ID"),
):
    """
    删除指定的任务。
    """
    cmd = DeleteTaskCommand(task_id=task_id)

    use_case = container.delete_task()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 任务已删除[/green]")
    else:
        console.print(f"[red]✗ 删除失败: {result.error}[/red]")
        raise typer.Exit(1)