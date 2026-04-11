from task_graph.issue_tracking.application.use_cases.unlink_issue_from_task import (
    UnlinkIssueFromTask,
    UnlinkIssueFromTaskCommand,
    UnlinkIssueFromTaskResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _unlink_issue_from_task(
    cmd: UnlinkIssueFromTaskCommand,
    use_case: UnlinkIssueFromTask = Provide["issue_tracking.unlink_issue_from_task"],
) -> UnlinkIssueFromTaskResult:
    return use_case.execute(cmd)


def unlink_issue_from_task(
    cmd: UnlinkIssueFromTaskCommand,
) -> UnlinkIssueFromTaskResult:
    """Unlink an issue from a task"""
    return _unlink_issue_from_task(cmd)
