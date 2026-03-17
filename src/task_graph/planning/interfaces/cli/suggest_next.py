"""获取优先级最高的可执行任务建议"""
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from task_graph.planning.container import Container
from task_graph.planning.application.use_cases.suggest_next_action import SuggestNextActionQuery

container = Container()
console = Console()


def suggest_next(
    top_n: int = typer.Option(3, "--top", "-n", help="返回的任务数量"),
    project_id: Optional[str] = typer.Option(None, "--project", "-p", help="按项目筛选"),
):
    """
    获取优先级最高的可执行任务建议 (基于 ROI 计算)。
    """
    query = SuggestNextActionQuery(top_n=top_n, project_id=project_id)

    use_case = container.suggest_next_action()
    result = use_case.execute(query)

    if not result.tasks:
        console.print("[yellow]没有可执行的任务[/yellow]")
        return

    table = Table(title=f"推荐执行的任务 (Top {top_n})")
    table.add_column("排名", style="dim", justify="right")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("名称", style="green")
    table.add_column("ROI", style="yellow", justify="right")
    table.add_column("工作量", justify="right")
    table.add_column("价值", justify="right")

    for i, task in enumerate(result.tasks, 1):
        summary = task.to_summary_dict()
        roi = summary.get("base_value", 0) / max(summary.get("effort", 1), 1)
        table.add_row(
            str(i),
            str(task.id)[:8] + "...",
            summary.get("name", ""),
            f"{roi:.2f}",
            str(summary.get("effort", "")),
            str(summary.get("base_value", "")),
        )

    console.print(table)