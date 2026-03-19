import typer
from task_graph.issue_tracking.container import Container
from task_graph.issue_tracking.application.use_cases.add_comment import (
    AddCommentCommand,
    AddCommentResult,
)

container = Container()


def issue_comment(cmd: AddCommentCommand) -> AddCommentResult:
    """Add comment to issue"""
    use_case = container.add_comment_use_case()
    return use_case.execute(cmd)
