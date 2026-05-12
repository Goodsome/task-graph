from task_graph.planning.application.use_cases.modify_task_dependencies import (
    ModifyTaskDependencies,
)
from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.dtos.modify_task_dependencies_command import (
    ModifyTaskDependenciesCommand,
)
from task_graph.planning.application.dtos.modify_task_dependencies_result import (
    ModifyTaskDependenciesResult,
)


@inject
def _modify_task_dependencies(
    cmd: ModifyTaskDependenciesCommand,
    use_case: ModifyTaskDependencies = Provide["planning.modify_task_dependencies"],
) -> ModifyTaskDependenciesResult:
    return use_case.execute(cmd)


def modify_task_dependencies(
    cmd: ModifyTaskDependenciesCommand,
) -> ModifyTaskDependenciesResult:
    return _modify_task_dependencies(cmd)
