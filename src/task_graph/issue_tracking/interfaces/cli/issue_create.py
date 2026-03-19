import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.create_issue import (
    CreateIssueCommand,
    CreateIssueResult,
)

container = Container()


def issue_create(cmd: CreateIssueCommand) -> CreateIssueResult:
    """Create a new issue"""
    use_case = container.create_issue_use_case()
    return use_case.execute(cmd)
