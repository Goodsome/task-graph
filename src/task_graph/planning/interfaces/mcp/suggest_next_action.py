from task_graph.planning.application.use_cases.suggest_next_action import (
    SuggestNextAction,
)
from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.dtos.suggest_next_action_result import (
    SuggestNextActionResult,
)
from task_graph.planning.application.dtos.suggest_next_action_query import (
    SuggestNextActionQuery,
)


@inject
def _suggest_next_action(
    query: SuggestNextActionQuery,
    use_case: SuggestNextAction = Provide["planning.suggest_next_action"],
) -> SuggestNextActionResult:
    return use_case.execute(query)


def suggest_next_action(query: SuggestNextActionQuery) -> SuggestNextActionResult:
    """Returns the highest priority tasks that are ready to execute."""
    return _suggest_next_action(query)
