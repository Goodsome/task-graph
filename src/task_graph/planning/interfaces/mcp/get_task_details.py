from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.get_task_details import (
    GetTaskDetails,
    GetTaskDetailsQuery,
    GetTaskDetailsResult,
)


@inject
def _get_task_details(
    query: GetTaskDetailsQuery,
    use_case: GetTaskDetails = Provide["planning.get_task_details"],
) -> GetTaskDetailsResult:
    return use_case.execute(query)


def get_task_details(query: GetTaskDetailsQuery) -> GetTaskDetailsResult:
    """Use case to get details of a specific task."""
    return _get_task_details(query)
