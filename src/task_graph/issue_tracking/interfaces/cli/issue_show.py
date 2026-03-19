import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.get_issue_details import (
    GetIssueDetailsQuery,
    GetIssueDetailsResult,
)

container = Container()


def issue_show(query: GetIssueDetailsQuery) -> GetIssueDetailsResult:
    """Show issue details"""
    use_case = container.get_issue_details_use_case()
    return use_case.execute(query)
