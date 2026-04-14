"""获取任务的详细上下文"""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from dependency_injector.wiring import Provide, inject

from task_graph.planning.application.use_cases.get_task_details import (
    GetTaskDetailsQuery,
    GetTaskDetails,
    GetTaskDetailsResult,
)

from task_graph.planning.interfaces.cli.app import planning_app

console = Console()


@inject
def _get_task(
    query: GetTaskDetailsQuery,
    use_case: GetTaskDetails = Provide["planning.get_task_details"],
) -> GetTaskDetailsResult:
    return use_case.execute(query)


@planning_app.command(name="get-task")
def get_task(
    task_id: Annotated[str, typer.Argument(..., help="任务ID")],
) -> None:
    """
    获取任务的详细上下文。
    """
    query = GetTaskDetailsQuery(task_id=task_id)
    result = _get_task(query)

    if not result.success:
        console.print(f"[red]错误: {result.error}[/red]")
        raise typer.Exit(1)

    task = result.task
    assert task is not None, "Task should not be None when result is successful"

    # 渲染任务详情
    console.print(Panel(f"[bold]{task.name}[/bold]", title=f"任务 {task_id}"))
    console.print(f"[cyan]项目:[/cyan] {task.project_id}")
    console.print(f"[cyan]状态:[/cyan] {task.status.value}")
    console.print(f"[cyan]层级:[/cyan] {task.scope_level.value}")
    console.print(
        f"[cyan]父任务ID:[/cyan] {str(task.parent_id) if task.parent_id else '-'}"
    )
    console.print(f"[cyan]工作量:[/cyan] {task.effort.value}")
    console.print(f"[cyan]价值:[/cyan] {task.base_value.value}")
    console.print(f"[cyan]完成逻辑:[/cyan] {task.completion_logic.value}")

    console.print("\n[cyan]描述:[/cyan]")
    console.print(task.description)

    if task.dependencies:
        console.print(
            f"\n[cyan]依赖:[/cyan] {', '.join(str(dep) for dep in task.dependencies)}"
        )

    # 被依赖需要额外查询，暂时移除（原dict中的dependents实际上不存在于Task模型中）
    # dependents = task.get("dependents", [])
    # if dependents:
    #     console.print(f"\n[cyan]被依赖:[/cyan] {', '.join(dependents)}")

    if task.output:
        console.print("\n[cyan]输出:[/cyan]")
        console.print(f"  摘要: {task.output.summary}")
        if task.output.artifacts:
            console.print(f"  产出: {', '.join(task.output.artifacts)}")
        if task.output.error:
            console.print(f"  [red]错误: {task.output.error}[/red]")
