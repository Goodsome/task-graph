from task_graph.issue_tracking.application.use_cases.add_comment import (
    AddComment,
    AddCommentCommand,
    AddCommentResult,
)
from dependency_injector.wiring import Provide, inject


@inject
def _add_comment(
    cmd: AddCommentCommand, use_case: AddComment = Provide["issue_tracking.add_comment"]
) -> AddCommentResult:
    return use_case.execute(cmd)


def add_comment(cmd: AddCommentCommand) -> AddCommentResult:
    """Add a comment to an issue"""
    return _add_comment(cmd)
