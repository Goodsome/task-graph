import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.unlink_issue_from_task import (
    UnlinkIssueFromTaskCommand,
    UnlinkIssueFromTaskResult,
)

container = Container()


def issue_unlink(cmd: UnlinkIssueFromTaskCommand) -> UnlinkIssueFromTaskResult:
    """Unlink issue from task"""
    use_case = container.unlink_issue_from_task_use_case()
    return use_case.execute(cmd)
