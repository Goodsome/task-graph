"""分页查询任务列表"""
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.list_tasks import ListTasksQuery
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel

container = Container()
console = Console()


def list_tasks(
    page: int = typer.Option(1, "--page", "-p", help="页码"),
    page_size: int = typer.Option(10, "--size", "-s", help="每页数量"),
    project_id: Optional[str] = typer.Option(None, "--project", help="按项目筛选"),
    status: Optional[str] = typer.Option(None, "--status", help="按状态筛选"),
    scope_level: Optional[str] = typer.Option(None, "--level", help="按范围层级筛选"),
    search: Optional[str] = typer.Option(None, "--search", help="关键字搜索"),
):
    """
    分页查询任务列表。
    """
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status.lower())
        except ValueError:
            console.print(f"[red]错误: 无效的状态: {status}[/red]")
            console.print("可选值: pending, blocked, ready, in_progress, review, done, changes_requested, skipped, discarded")
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

    use_case = container.list_tasks()
    result = use_case.execute(query)

    if result.error:
        console.print(f"[red]错误: {result.error}[/red]")
        raise typer.Exit(1)

    # 渲染表格
    table = Table(title=f"任务列表 (第 {result.current_page}/{result.total_pages} 页, 共 {result.total_count} 条)")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("名称", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("层级", style="blue")
    table.add_column("父ID", style="magenta", no_wrap=True)
    table.add_column("工作量", justify="right")
    table.add_column("价值", justify="right")

    for task in result.tasks:
        table.add_row(
            task.get("id", ""),
            task.get("name", ""),
            task.get("status", ""),
            task.get("scope_level", ""),
            task.get("parent_id", "") or "-",
            str(task.get("effort", "")),
            str(task.get("base_value", "")),
        )

    console.print(table)