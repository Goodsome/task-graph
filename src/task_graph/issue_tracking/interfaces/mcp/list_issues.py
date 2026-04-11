from task_graph.issue_tracking.application.use_cases.list_issues import (
    ListIssues,
    ListIssuesQuery,
    ListIssuesResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _list_issues(
    query: ListIssuesQuery,
    use_case: ListIssues = Provide["issue_tracking.list_issues"],
) -> ListIssuesResult:
    return use_case.execute(query)


def list_issues(query: ListIssuesQuery) -> ListIssuesResult:
    return _list_issues(query)
