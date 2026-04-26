from dependency_injector.wiring import Provide, inject

from task_graph.planning.application.use_cases.complete_decomposition import (
    CompleteDecomposition,
    CompleteDecompositionCommand,
    CompleteDecompositionResult,
)


@inject
def _complete_decomposition(
    cmd: CompleteDecompositionCommand,
    use_case: CompleteDecomposition = Provide["planning.complete_decomposition"],
) -> CompleteDecompositionResult:
    return use_case.execute(cmd)


def complete_decomposition(cmd: CompleteDecompositionCommand) -> CompleteDecompositionResult:
    """Complete a task decomposition if all subtasks are done."""
    return _complete_decomposition(cmd)
