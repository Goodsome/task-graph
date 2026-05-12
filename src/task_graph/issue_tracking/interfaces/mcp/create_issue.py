from task_graph.issue_tracking.application.use_cases.create_issue import CreateIssue
from dependency_injector.wiring import Provide, inject
from task_graph.issue_tracking.application.dtos.create_issue_command import (
    CreateIssueCommand,
)
from task_graph.issue_tracking.application.dtos.create_issue_result import (
    CreateIssueResult,
)


@inject
def _create_issue(
    cmd: CreateIssueCommand,
    use_case: CreateIssue = Provide["issue_tracking.create_issue"],
) -> CreateIssueResult:
    return use_case.execute(cmd)


def create_issue(cmd: CreateIssueCommand) -> CreateIssueResult:
    """Create a new issue with initial status NEW"""
    return _create_issue(cmd)
