from dependency_injector.wiring import Provide, inject
from task_graph.planning.application.use_cases.list_tasks import ListTasks
from task_graph.planning.application.dtos.list_tasks_result import ListTasksResult
from task_graph.planning.application.dtos.list_tasks_query import ListTasksQuery


@inject
def _list_tasks(
    query: ListTasksQuery, use_case: ListTasks = Provide["planning.list_tasks"]
) -> ListTasksResult:
    return use_case.execute(query)


def list_tasks(query: ListTasksQuery) -> ListTasksResult:
    return _list_tasks(query)
