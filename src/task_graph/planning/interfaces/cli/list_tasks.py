"""分页查询任务列表"""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from task_graph.planning.application.use_cases.list_tasks import (
    ListTasksQuery,
    ListTasks,
    ListTasksResult,
)
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel
from dependency_injector.wiring import Provide, inject

from task_graph.planning.interfaces.cli.app import planning_app

console = Console()


@inject
def _list_tasks(
    query: ListTasksQuery, use_case: ListTasks = Provide["planning.list_tasks"]
) -> ListTasksResult:
    return use_case.execute(query)


@planning_app.command(name="list-tasks")
def list_tasks(
    page: Annotated[int, typer.Option("--page", "-p", help="页码")] = 1,
    page_size: Annotated[int, typer.Option("--size", "-s", help="每页数量")] = 10,
    project_id: Annotated[
        str | None, typer.Option("--project", help="按项目筛选")
    ] = None,
    status: Annotated[str | None, typer.Option("--status", help="按状态筛选")] = None,
    scope_level: Annotated[
        str | None, typer.Option("--level", help="按范围层级筛选")
    ] = None,
    search: Annotated[str | None, typer.Option("--search", help="关键字搜索")] = None,
) -> None:
    """
    分页查询任务列表。
    """
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status.lower())
        except ValueError:
            console.print(f"[red]错误: 无效的状态: {status}[/red]")
            console.print(
                "可选值: pending, blocked, ready, in_progress, review, done, changes_requested, skipped, discarded"
            )
            raise typer.Exit(1)

    level = None
    if scope_level:
        try:
            level = ScopeLevel(scope_level.lower())
        except ValueError:
            console.print(f"[red]错误: 无效的层级: {scope_level}[/red]")
            console.print("可选值: project, context, architectural, atomic")
            raise typer.Exit(1)

    query = ListTasksQuery(
        page=page,
        page_size=page_size,
        project_id=project_id,
        status=task_status,
        scope_level=level,
        search=search or "",
    )

    result = _list_tasks(query)

    if result.error:
        console.print(f"[red]错误: {result.error}[/red]")
        raise typer.Exit(1)

    # 渲染表格
    table = Table(
        title=f"任务列表 (第 {result.current_page}/{result.total_pages} 页, 共 {result.total_count} 条)"
    )
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("名称", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("层级", style="blue")
    table.add_column("父ID", style="magenta", no_wrap=True)
    table.add_column("工作量", justify="right")
    table.add_column("价值", justify="right")

    for task in result.tasks:
        table.add_row(
            task.id,
            task.name,
            task.status,
            task.scope_level,
            task.parent_id or "-",
            str(task.effort),
            str(task.base_value),
        )

    console.print(table)
