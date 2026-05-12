from task_graph.issue_tracking.application.use_cases.close_issue import CloseIssue
from dependency_injector.wiring import Provide, inject
from task_graph.issue_tracking.application.dtos.close_issue_command import (
    CloseIssueCommand,
)
from task_graph.issue_tracking.application.dtos.close_issue_result import (
    CloseIssueResult,
)


@inject
def _close_issue(
    cmd: CloseIssueCommand, use_case: CloseIssue = Provide["issue_tracking.close_issue"]
) -> CloseIssueResult:
    return use_case.execute(cmd)


def close_issue(cmd: CloseIssueCommand) -> CloseIssueResult:
    """Close an issue that is in RESOLVED status"""
    return _close_issue(cmd)
