from pydantic import BaseModel, Field
from dataclasses import dataclass
from datetime import datetime
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity


class GetIssueDetailsQuery(BaseModel):
    issue_id: str


class CommentDTO(BaseModel):
    id: str
    content: str
    author: str
    created_at: datetime


class LabelDTO(BaseModel):
    name: str
    color: str | None


class TaskLinkDTO(BaseModel):
    task_id: str
    linked_at: datetime


class SubmitterDTO(BaseModel):
    name: str
    email: str
    external_id: str | None


class IssueDetailsDTO(BaseModel):
    id: str
    title: str
    description: str
    type: IssueType
    severity: Severity
    status: IssueStatus
    submitter: SubmitterDTO
    labels: list[LabelDTO]
    comments: list[CommentDTO]
    task_links: list[TaskLinkDTO]
    created_at: datetime
    updated_at: datetime


class GetIssueDetailsResult(BaseModel):
    success: bool
    issue: IssueDetailsDTO | None = Field(default=None)
    error: str = Field(default="")


@dataclass
class GetIssueDetails:
    """Get full issue details including comments and labels"""

    issue_repository: IssueRepository

    def execute(self, query: GetIssueDetailsQuery) -> GetIssueDetailsResult:
        try:
            # Parse issue ID
            issue_id = IssueId.reconstitute(query.issue_id)

            # Find issue
            issue = self.issue_repository.find_by_id(issue_id)
            if not issue:
                return GetIssueDetailsResult(
                    success=False,
                    issue=None,
                    error=f"Issue {query.issue_id} not found"
                )

            # Convert to DTO
            issue_dto = IssueDetailsDTO(
                id=str(issue.id),
                title=issue.title.value,
                description=issue.description.value,
                type=issue.type,
                severity=issue.severity,
                status=issue.status,
                submitter=SubmitterDTO(
                    name=issue.submitter.name,
                    email=issue.submitter.email,
                    external_id=issue.submitter.external_id
                ),
                labels=[
                    LabelDTO(name=l.name, color=l.color)
                    for l in issue.labels
                ],
                comments=[
                    CommentDTO(
                        id=str(c.id),
                        content=c.content,
                        author=c.author,
                        created_at=c.created_at
                    )
                    for c in issue.comments
                ],
                task_links=[
                    TaskLinkDTO(
                        task_id=str(tl.task_id),
                        linked_at=tl.linked_at
                    )
                    for tl in issue.task_links
                ],
                created_at=issue.created_at,
                updated_at=issue.updated_at
            )

            return GetIssueDetailsResult(
                success=True,
                issue=issue_dto
            )
        except Exception as e:
            return GetIssueDetailsResult(
                success=False,
                issue=None,
                error=str(e)
            )

