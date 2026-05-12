from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.application.dtos.issue_summary_dto import IssueSummaryDTO
from task_graph.issue_tracking.application.dtos.list_issues_query import ListIssuesQuery
from typing import Self
from task_graph.issue_tracking.application.dtos.list_issues_result import (
    ListIssuesResult,
)


@dataclass
class ListIssues:
    """Paginated list of issues with filtering"""

    uow: UnitOfWork[IssueRepository]

    def execute(self: Self, query: ListIssuesQuery) -> ListIssuesResult:
        try:
            with self.uow:
                issues, total_count = self.uow.repository.find_paged(
                    limit=query.limit,
                    offset=query.offset,
                    status=query.status,
                    issue_type=query.type,
                    severity=query.severity,
                    labels=query.labels,
                    project_id=query.project_id,
                )
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
                    updated_at=issue.updated_at,
                )
                for issue in issues
            ]
            return ListIssuesResult(issues=issue_dtos, total_count=total_count)
        except Exception as e:
            return ListIssuesResult(issues=[], total_count=0, error=str(e))
