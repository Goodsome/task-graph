import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.create_task import CreateTask
from task_graph.planning.domain.enums import (
    ArchitectureLayer,
    ScopeLevel,
)
from task_graph.planning.application.dtos.create_task_result import CreateTaskResult
from task_graph.planning.domain.value_objects.scenario import Scenario
from task_graph.planning.application.dtos.create_task_command import CreateTaskCommand

console = Console()


@inject
def _create_task(
    cmd: CreateTaskCommand,
    use_case: CreateTask = Provide["planning_container.create_task"],
) -> CreateTaskResult:
    return use_case.execute(cmd)


def create_task(
    project_id: Annotated[str, typer.Argument()],
    name: Annotated[str, typer.Argument()],
    description: Annotated[str, typer.Argument()],
    effort: Annotated[int, typer.Argument()],
    base_value: Annotated[float, typer.Argument()],
    scope_level: Annotated[ScopeLevel, typer.Argument()],
    dependencies: Annotated[list[str], typer.Option("--dependencies", "-d")] = "list",
    parent_id: Annotated[str | None, typer.Option("--parent-id", "-pi")] = None,
    bounded_context: Annotated[
        str | None, typer.Option("--bounded-context", "-bc")
    ] = None,
    architecture_layer: Annotated[
        ArchitectureLayer | None, typer.Option("--architecture-layer", "-al")
    ] = None,
    component_name: Annotated[
        str | None, typer.Option("--component-name", "-cn")
    ] = None,
    acceptance_criteria: Annotated[
        list[Scenario], typer.Option("--acceptance-criteria", "-ac")
    ] = "list",
) -> CreateTaskResult:
    """创建一个新的规划任务。"""
    try:
        level = ScopeLevel(scope_level.lower())
    except ValueError:
        console.print(f"[red]错误: 无效的 scope_level: {scope_level}[/red]")
        console.print("可选值: project, context, architecture, component")
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
