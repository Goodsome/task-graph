"""创建一个新的规划任务"""

from typing import Annotated

import typer
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from task_graph.planning.application.use_cases.create_task import (
    CreateTaskCommand,
    CreateTask,
    CreateTaskResult,
)
from task_graph.planning.domain.enums import (
    CompletionLogic,
    ScopeLevel,
    ArchitectureLayer,
)
from task_graph.planning.interfaces.cli.app import planning_app

console = Console()


@inject
def _create_task(
    cmd: CreateTaskCommand, use_case: CreateTask = Provide["planning.create_task"]
) -> CreateTaskResult:
    return use_case.execute(cmd)


@planning_app.command(name="create-task")
def create_task(
    project_id: Annotated[str, typer.Argument(help="项目标识符")],
    name: Annotated[str, typer.Argument(help="任务名称")],
    description: Annotated[str, typer.Argument(help="任务描述")],
    effort: Annotated[
        int, typer.Argument(help="工作量估算 (斐波那契数列: 1, 2, 3, 5, 8, 13...)")
    ],
    base_value: Annotated[float, typer.Argument(help="业务价值评分 (1.0-10.0)")],
    scope_level: Annotated[
        str,
        typer.Option(
            "--level",
            "-l",
            help="任务范围层级: project, context, architecture, component",
        ),
    ] = "component",
    completion_logic: Annotated[
        str,
        typer.Option(
            "--logic", help="依赖完成逻辑: all (所有依赖完成), any (任一依赖完成)"
        ),
    ] = "all",
    dependencies: Annotated[
        list[str] | None, typer.Option("--dep", help="前置任务ID (可多次指定)")
    ] = None,
    parent_id: Annotated[str | None, typer.Option("--parent", help="父任务ID")] = None,
    bounded_context: Annotated[
        str | None, typer.Option("--bounded-context", "-b", help="所属限界上下文")
    ] = None,
    architecture_layer: Annotated[
        str | None, typer.Option("--architecture-layer", "-a", help="所属架构层")
    ] = None,
) -> None:
    """
    创建一个新的规划任务。
    """
    try:
        level = ScopeLevel(scope_level.lower())
    except ValueError:
        console.print(f"[red]错误: 无效的 scope_level: {scope_level}[/red]")
        console.print("可选值: project, context, architecture, component")
        raise typer.Exit(1)

    try:
        logic = CompletionLogic(completion_logic.lower())
    except ValueError:
        console.print(f"[red]错误: 无效的 completion_logic: {completion_logic}[/red]")
        console.print("可选值: all, any")
        raise typer.Exit(1)

    arch_layer = None
    if architecture_layer:
        try:
            arch_layer = ArchitectureLayer(architecture_layer.lower())
        except ValueError:
            console.print(
                f"[red]错误: 无效的 architecture_layer: {architecture_layer}[/red]"
            )
            console.print(
                "可选值: domain, application, infrastructure, interfaces, cross_cutting, none"
            )
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
        bounded_context=bounded_context,
        architecture_layer=arch_layer,
    )

    result = _create_task(cmd)

    if result.success:
        console.print("[green]✓ 任务创建成功[/green]")
        console.print(f"  Task ID: {result.task_id}")
    else:
        console.print(f"[red]✗ 任务创建失败: {result.error}[/red]")
        raise typer.Exit(1)
