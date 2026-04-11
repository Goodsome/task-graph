from task_graph.planning.application.use_cases.suggest_next_action import (
    SuggestNextAction,
    SuggestNextActionQuery,
    SuggestNextActionResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _suggest_next_action(
    query: SuggestNextActionQuery,
    use_case: SuggestNextAction = Provide["planning.suggest_next_action"],
) -> SuggestNextActionResult:
    return use_case.execute(query)


def suggest_next_action(query: SuggestNextActionQuery) -> SuggestNextActionResult:
    """Returns the highest priority tasks that are ready to execute."""
    return _suggest_next_action(query)
