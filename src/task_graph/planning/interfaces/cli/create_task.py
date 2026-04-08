"""创建一个新的规划任务"""
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.create_task import CreateTaskCommand
from task_graph.planning.domain.enums import CompletionLogic, ScopeLevel

container = Container()
console = Console()


def create_task(
    project_id: str = typer.Option(..., "--project", "-p", help="项目标识符"),
    name: str = typer.Option(..., "--name", "-n", help="任务名称"),
    description: str = typer.Option(..., "--desc", "-d", help="任务描述"),
    effort: int = typer.Option(..., "--effort", "-e", help="工作量估算 (斐波那契数列: 1, 2, 3, 5, 8, 13...)"),
    base_value: float = typer.Option(..., "--value", "-v", help="业务价值评分 (1.0-10.0)"),
    scope_level: str = typer.Option(
        "atomic",
        "--level",
        "-l",
        help="任务范围层级: project, context, architectural, atomic",
    ),
    completion_logic: str = typer.Option(
        "all",
        "--logic",
        help="依赖完成逻辑: all (所有依赖完成), any (任一依赖完成)",
    ),
    dependencies: Optional[list[str]] = typer.Option(
        None,
        "--dep",
        help="前置任务ID (可多次指定)",
    ),
    parent_id: Optional[str] = typer.Option(
        None,
        "--parent",
        help="父任务ID",
    ),
):
    """
    创建一个新的规划任务。
    """
    try:
        level = ScopeLevel(scope_level.lower())
    except ValueError:
        console.print(f"[red]错误: 无效的 scope_level: {scope_level}[/red]")
        console.print("可选值: project, context, architectural, atomic")
        raise typer.Exit(1)

    try:
        logic = CompletionLogic(completion_logic.lower())
    except ValueError:
        console.print(f"[red]错误: 无效的 completion_logic: {completion_logic}[/red]")
        console.print("可选值: all, any")
        raise typer.Exit(1)

    cmd = CreateTaskCommand(
        project_id=project_id,
        name=name,
        description=description,
        effort=effort,
        base_value=base_value,
        scope_level=level,
        completion_logic=logic,
        dependencies=dependencies or [],
        parent_id=parent_id,
    )

    use_case = container.create_task()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 任务创建成功[/green]")
        console.print(f"  Task ID: {result.task_id}")
    else:
        console.print(f"[red]✗ 任务创建失败: {result.error}[/red]")
        raise typer.Exit(1)