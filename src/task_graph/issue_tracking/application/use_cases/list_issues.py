from pydantic import BaseModel, Field
from datetime import datetime
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from dataclasses import dataclass
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork


class IssueSummaryDTO(BaseModel):
    id: str
    project_id: str
    title: str
    type: IssueType
    severity: Severity
    status: IssueStatus
    submitter_name: str
    comment_count: int
    label_count: int
    task_link_count: int
    created_at: datetime
    updated_at: datetime


class ListIssuesQuery(BaseModel):
    status: IssueStatus | None = Field(default=None)
    type: IssueType | None = Field(default=None)
    severity: Severity | None = Field(default=None)
    labels: list[str] | None = Field(default=None)
    project_id: str | None = Field(default=None)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ListIssuesResult(BaseModel):
    issues: list[IssueSummaryDTO]
    total_count: int
    error: str = Field(default="")


@dataclass
class ListIssues:
    """Paginated list of issues with filtering"""

    uow: UnitOfWork

    def execute(self, query: ListIssuesQuery) -> ListIssuesResult:
        try:
            with self.uow:
                # Get paginated issues and total count with the same filters
                issues, total_count = self.uow.issues.find_paged(
                    limit=query.limit,
                    offset=query.offset,
                    status=query.status,
                    issue_type=query.type,
                    severity=query.severity,
                    labels=query.labels,
                    project_id=query.project_id
                )

            # Convert to DTOs
            issue_dtos = [
                IssueSummaryDTO(
                    id=str(issue.id),
                    project_id=issue.project_id,
                    title=issue.title.value,
                    type=issue.type,
                    severity=issue.severity,
                    status=issue.status,
                    submitter_name=issue.submitter.name,
                    comment_count=len(issue.comments),
                    label_count=len(issue.labels),
                    task_link_count=len(issue.task_links),
                    created_at=issue.created_at,
                    updated_at=issue.updated_at
                )
                for issue in issues
            ]

            return ListIssuesResult(
                issues=issue_dtos,
                total_count=total_count
            )
        except Exception as e:
            return ListIssuesResult(
                issues=[],
                total_count=0,
                error=str(e)
            )

