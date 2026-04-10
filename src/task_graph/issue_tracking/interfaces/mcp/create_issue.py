from task_graph.issue_tracking.application.use_cases.create_issue import (
    CreateIssue,
    CreateIssueCommand,
    CreateIssueResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _create_issue(
    cmd: CreateIssueCommand,
    use_case: CreateIssue = Provide["issue_tracking.create_issue"],
) -> CreateIssueResult:
    return use_case.execute(cmd)


def create_issue(cmd: CreateIssueCommand) -> CreateIssueResult:
    return _create_issue(cmd)
