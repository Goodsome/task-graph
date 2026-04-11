from task_graph.issue_tracking.application.use_cases.link_issue_to_task import (
    LinkIssueToTask,
    LinkIssueToTaskCommand,
    LinkIssueToTaskResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _link_issue_to_task(
    cmd: LinkIssueToTaskCommand,
    use_case: LinkIssueToTask = Provide["issue_tracking.link_issue_to_task"],
) -> LinkIssueToTaskResult:
    return use_case.execute(cmd)


def link_issue_to_task(cmd: LinkIssueToTaskCommand) -> LinkIssueToTaskResult:
    """Link an issue to a task from Planning context"""
    return _link_issue_to_task(cmd)
