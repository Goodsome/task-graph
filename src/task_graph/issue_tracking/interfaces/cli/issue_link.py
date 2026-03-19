import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.link_issue_to_task import (
    LinkIssueToTaskCommand,
    LinkIssueToTaskResult,
)

container = Container()


def issue_link(cmd: LinkIssueToTaskCommand) -> LinkIssueToTaskResult:
    """Link issue to task"""
    use_case = container.link_issue_to_task_use_case()
    return use_case.execute(cmd)
