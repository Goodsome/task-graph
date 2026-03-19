import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.update_issue_status import (
    UpdateIssueStatusCommand,
    UpdateIssueStatusResult,
)

container = Container()


def issue_status(cmd: UpdateIssueStatusCommand) -> UpdateIssueStatusResult:
    """Update issue status"""
    use_case = container.update_issue_status_use_case()
    return use_case.execute(cmd)
