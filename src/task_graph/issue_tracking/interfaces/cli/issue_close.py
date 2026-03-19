import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.close_issue import (
    CloseIssueCommand,
    CloseIssueResult,
)

container = Container()


def issue_close(cmd: CloseIssueCommand) -> CloseIssueResult:
    """Close an issue"""
    use_case = container.close_issue_use_case()
    return use_case.execute(cmd)
