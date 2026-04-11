from task_graph.issue_tracking.application.use_cases.update_issue_metadata import (
    UpdateIssueMetadata,
    UpdateIssueMetadataCommand,
    UpdateIssueMetadataResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _update_issue_metadata(
    cmd: UpdateIssueMetadataCommand,
    use_case: UpdateIssueMetadata = Provide["issue_tracking.update_issue_metadata"],
) -> UpdateIssueMetadataResult:
    return use_case.execute(cmd)


def update_issue_metadata(cmd: UpdateIssueMetadataCommand) -> UpdateIssueMetadataResult:
    """Update issue metadata like type, severity, and labels"""
    return _update_issue_metadata(cmd)
