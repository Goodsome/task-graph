from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from abc import ABC, abstractmethod
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.shared.domain.ports.repository import Repository


class IssueRepository(Repository[Issue, IssueId], ABC):
    """Persistence interface for Issue aggregate"""

    @abstractmethod
    def find_by_id(self, issue_id: IssueId) -> Issue | None: ...

    @abstractmethod
    def find_all(
        self,
        limit: int,
        offset: int,
        status: IssueStatus | None,
        issue_type: IssueType | None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
        project_id: str | None = None,
    ) -> list[Issue]: ...

    @abstractmethod
    def find_by_task_id(self, task_id: str) -> list[Issue]: ...

    @abstractmethod
    def count(
        self, status: IssueStatus | None = None, issue_type: IssueType | None = None
    ) -> int: ...

    @abstractmethod
    def find_paged(
        self,
        limit: int,
        offset: int,
        status: IssueStatus | None,
        issue_type: IssueType | None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
        project_id: str | None = None,
    ) -> tuple[list[Issue], int]:
        """
        Find paginated issues with filtering and return both the list and total count.
        This ensures consistency between the returned list and count by using the same filters.
        """
        ...
