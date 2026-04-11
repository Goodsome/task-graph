from task_graph.issue_tracking.application.use_cases.close_issue import (
    CloseIssue,
    CloseIssueCommand,
    CloseIssueResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _close_issue(
    cmd: CloseIssueCommand, use_case: CloseIssue = Provide["issue_tracking.close_issue"]
) -> CloseIssueResult:
    return use_case.execute(cmd)


def close_issue(cmd: CloseIssueCommand) -> CloseIssueResult:
    """Close an issue that is in RESOLVED status"""
    return _close_issue(cmd)
