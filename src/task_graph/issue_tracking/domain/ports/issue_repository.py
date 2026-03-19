from __future__ import annotations

from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from abc import ABC, abstractmethod
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId


class IssueRepository(ABC):
    """Persistence interface for Issue aggregate"""

    @abstractmethod
    def save(self, issue: Issue) -> None: ...

    @abstractmethod
    def find_by_id(self, issue_id: IssueId) -> Issue | None: ...

    @abstractmethod
    def find_all(
        self,
        status: IssueStatus | None,
        issue_type: IssueType | None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
        limit: int = None,
        offset: int = None,
    ) -> list[Issue]: ...

    @abstractmethod
    def delete(self, issue_id: IssueId) -> bool: ...

    @abstractmethod
    def find_by_task_id(self, task_id: str) -> list[Issue]: ...

    @abstractmethod
    def count(
        self, status: IssueStatus | None = None, issue_type: IssueType | None = None
    ) -> int: ...
