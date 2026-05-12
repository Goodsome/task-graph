from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from typing import Self
from task_graph.issue_tracking.application.dtos.get_issue_details_result import (
    GetIssueDetailsResult,
)
from task_graph.issue_tracking.application.dtos.get_issue_details_query import (
    GetIssueDetailsQuery,
)
from task_graph.issue_tracking.application.dtos.comment_dto import CommentDTO
from task_graph.issue_tracking.application.dtos.issue_details_dto import IssueDetailsDTO
from task_graph.issue_tracking.application.dtos.label_dto import LabelDTO
from task_graph.issue_tracking.application.dtos.submitter_dto import SubmitterDTO
from task_graph.issue_tracking.application.dtos.task_link_dto import TaskLinkDTO


@dataclass
class GetIssueDetails:
    """Get full issue details including comments and labels"""

    uow: UnitOfWork[IssueRepository]

    def execute(self: Self, query: GetIssueDetailsQuery) -> GetIssueDetailsResult:
        try:
            with self.uow:
                issue_id = IssueId.reconstitute(query.issue_id)
                issue = self.uow.repository.find_by_id(issue_id)
            if not issue:
                return GetIssueDetailsResult(
                    success=False, issue=None, error=f"Issue {query.issue_id} not found"
                )
            issue_dto = IssueDetailsDTO(
                id=str(issue.id),
                project_id=issue.project_id,
                title=issue.title.value,
                description=issue.description.value,
                type=issue.type,
                severity=issue.severity,
                status=issue.status,
                submitter=SubmitterDTO(name=issue.submitter.name),
                labels=[LabelDTO(name=l.name) for l in issue.labels],
                comments=[
                    CommentDTO(
                        id=str(c.id),
                        content=c.content,
                        author=c.author,
                        created_at=c.created_at,
                    )
                    for c in issue.comments
                ],
                task_links=[
                    TaskLinkDTO(task_id=str(tl.task_id), linked_at=tl.linked_at)
                    for tl in issue.task_links
                ],
                created_at=issue.created_at,
                updated_at=issue.updated_at,
            )
            return GetIssueDetailsResult(success=True, issue=issue_dto)
        except Exception as e:
            return GetIssueDetailsResult(success=False, issue=None, error=str(e))
