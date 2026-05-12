from task_graph.issue_tracking.application.use_cases.update_issue_metadata import (
    UpdateIssueMetadata,
)
from dependency_injector.wiring import Provide, inject
from task_graph.issue_tracking.application.dtos.update_issue_metadata_command import (
    UpdateIssueMetadataCommand,
)
from task_graph.issue_tracking.application.dtos.update_issue_metadata_result import (
    UpdateIssueMetadataResult,
)


@inject
def _update_issue_metadata(
    cmd: UpdateIssueMetadataCommand,
    use_case: UpdateIssueMetadata = Provide["issue_tracking.update_issue_metadata"],
) -> UpdateIssueMetadataResult:
    return use_case.execute(cmd)


def update_issue_metadata(cmd: UpdateIssueMetadataCommand) -> UpdateIssueMetadataResult:
    """Update issue metadata like type, severity, and labels"""
    return _update_issue_metadata(cmd)
