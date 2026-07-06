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
    scope_level: Annotated[ScopeLevel, typer.Argument()],
    dependencies: Annotated[list[str] | None, typer.Option("--dependencies", "-d")] = None,
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
) -> None:
    """创建一个新的规划任务。"""
    cmd = CreateTaskCommand(
        project_id=project_id,
        name=name,
        description=description,
        effort=1,
        base_value=1,
        scope_level=scope_level,
        dependencies=dependencies or [],
        parent_id=parent_id,
        bounded_context=bounded_context,
        architecture_layer=architecture_layer,
        component_name=component_name,
    )
    result = _create_task(cmd)
    if result.success:
        console.print("[green]✓ 任务创建成功[/green]")
        console.print(f"  Task ID: {result.task_id}")
    else:
        console.print(f"[red]✗ 任务创建失败: {result.error}[/red]")
        raise typer.Exit(1)
