"""修改任务的依赖关系"""
from typing import Optional

import typer
from rich.console import Console

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.modify_task_dependencies import ModifyTaskDependenciesCommand

container = Container()
console = Console()


def modify_deps(
    task_id: str = typer.Argument(..., help="任务ID"),
    add: Optional[list[str]] = typer.Option(None, "--add", "-a", help="添加依赖 (可多次指定)"),
    remove: Optional[list[str]] = typer.Option(None, "--remove", "-r", help="移除依赖 (可多次指定)"),
):
    """
    修改任务的依赖关系。

    支持添加和移除依赖，会自动进行循环检测。
    """
    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id,
        added_dependencies=add or [],
        removed_dependencies=remove or [],
    )

    use_case = container.modify_task_dependencies()
    result = use_case.execute(cmd)

    if result.success:
        console.print(f"[green]✓ 依赖关系已更新[/green]")
    else:
        console.print(f"[red]✗ 更新失败: {result.error}[/red]")
        raise typer.Exit(1)