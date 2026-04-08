"""获取任务的详细上下文"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.get_task_details import GetTaskDetailsQuery

container = Container()
console = Console()


def get_task(
    task_id: str = typer.Argument(..., help="任务ID"),
):
    """
    获取任务的详细上下文。
    """
    query = GetTaskDetailsQuery(task_id=task_id)

    use_case = container.get_task_details()
    result = use_case.execute(query)

    if not result.success:
        console.print(f"[red]错误: {result.error}[/red]")
        raise typer.Exit(1)

    task = result.task

    # 渲染任务详情
    console.print(Panel(f"[bold]{task.get('name', '')}[/bold]", title=f"任务 {task_id}"))
    console.print(f"[cyan]项目:[/cyan] {task.get('project_id', '')}")
    console.print(f"[cyan]状态:[/cyan] {task.get('status', '')}")
    console.print(f"[cyan]层级:[/cyan] {task.get('scope_level', '')}")
    console.print(f"[cyan]父任务ID:[/cyan] {task.get('parent_id', '') or '-'}")
    console.print(f"[cyan]工作量:[/cyan] {task.get('effort', '')}")
    console.print(f"[cyan]价值:[/cyan] {task.get('base_value', '')}")
    console.print(f"[cyan]完成逻辑:[/cyan] {task.get('completion_logic', '')}")

    console.print(f"\n[cyan]描述:[/cyan]")
    console.print(task.get('description', ''))

    deps = task.get('dependencies', [])
    if deps:
        console.print(f"\n[cyan]依赖:[/cyan] {', '.join(deps)}")

    dependents = task.get('dependents', [])
    if dependents:
        console.print(f"\n[cyan]被依赖:[/cyan] {', '.join(dependents)}")

    output = task.get('output')
    if output:
        console.print(f"\n[cyan]输出:[/cyan]")
        console.print(f"  摘要: {output.get('summary', '')}")
        if output.get('artifacts'):
            console.print(f"  产出: {', '.join(output.get('artifacts', []))}")
        if output.get('error'):
            console.print(f"  [red]错误: {output.get('error')}[/red]")