"""审查任务并提供反馈"""
import typer
from rich.console import Console

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.review_task import ReviewTaskCommand

container = Container()
console = Console()


def review_task(
    task_id: str = typer.Argument(..., help="任务ID"),
    approved: bool = typer.Option(..., "--approved/--rejected", help="是否通过验收"),
    feedback: str = typer.Option(..., "--feedback", "-f", help="反馈意见"),
):
    """
    审查任务并提供反馈。

    如果 approved=True，任务将变为 DONE，并解锁后续任务。
    如果 approved=False，任务将变为 CHANGES_REQUESTED。
    """
    cmd = ReviewTaskCommand(
        task_id=task_id,
        approved=approved,
        feedback=feedback,
    )

    use_case = container.review_task()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 审查完成[/green]")
        if result.affected_tasks:
            console.print(f"  解锁的任务: {', '.join(result.affected_tasks)}")
    else:
        console.print(f"[red]✗ 审查失败: {result.error}[/red]")
        raise typer.Exit(1)