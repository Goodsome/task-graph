"""领取一个处于 READY 状态的任务"""
from typing import Optional

import typer
from rich.console import Console

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.claim_task import ClaimTaskCommand

container = Container()
console = Console()


def claim_task(
    task_id: str = typer.Argument(..., help="任务ID"),
    executor_id: Optional[str] = typer.Option(None, "--executor", "-e", help="执行者标识"),
):
    """
    领取一个处于 READY 状态的任务。

    将任务状态从 READY 原子性地变更为 IN_PROGRESS。
    """
    cmd = ClaimTaskCommand(
        task_id=task_id,
        executor_id=executor_id or "",
    )

    use_case = container.claim_task()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 任务已领取[/green]")
        console.print(f"  Task ID: {result.task_id}")
    else:
        console.print(f"[red]✗ 领取失败: {result.error}[/red]")
        if result.error_code:
            console.print(f"  错误码: {result.error_code}")
        raise typer.Exit(1)