from dependency_injector.wiring import Provide, inject
from task_graph.issue_tracking.application.use_cases.update_issue_status import (
    UpdateIssueStatus,
    UpdateIssueStatusCommand,
    UpdateIssueStatusResult,
)


@inject
def _update_issue_status(
    cmd: UpdateIssueStatusCommand,
    use_case: UpdateIssueStatus = Provide["issue_tracking.update_issue_status"],
) -> UpdateIssueStatusResult:
    return use_case.execute(cmd)


def update_issue_status(cmd: UpdateIssueStatusCommand) -> UpdateIssueStatusResult:
    """Update issue status with state machine validation"""
    return _update_issue_status(cmd)
