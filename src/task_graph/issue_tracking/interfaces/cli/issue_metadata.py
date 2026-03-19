import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.update_issue_metadata import (
    UpdateIssueMetadataCommand,
    UpdateIssueMetadataResult,
)

container = Container()


def issue_metadata(cmd: UpdateIssueMetadataCommand) -> UpdateIssueMetadataResult:
    """Update issue metadata"""
    use_case = container.update_issue_metadata_use_case()
    return use_case.execute(cmd)
