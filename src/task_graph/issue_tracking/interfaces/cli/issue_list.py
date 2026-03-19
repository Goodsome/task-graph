import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.list_issues import (
    ListIssuesQuery,
    ListIssuesResult,
)

container = Container()


def issue_list(query: ListIssuesQuery) -> ListIssuesResult:
    """List issues with filtering"""
    use_case = container.list_issues_use_case()
    return use_case.execute(query)
