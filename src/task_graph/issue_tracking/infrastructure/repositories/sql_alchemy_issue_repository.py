from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from dataclasses import dataclass

# TODO: Define IssueModel in orm.py
IssueModel = Any


@dataclass
class SqlAlchemyIssueRepository(IssueRepository):
    """SQLAlchemy implementation of IssueRepository"""

    session: Session

    def save(self, issue: Issue) -> None: ...

    def find_by_id(self, issue_id: IssueId) -> Issue | None: ...

    def find_all(
        self,
        limit: int,
        offset: int,
        status: IssueStatus | None,
        issue_type: IssueType | None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
    ) -> list[Issue]: ...

    def delete(self, issue_id: IssueId) -> bool: ...

    def find_by_task_id(self, task_id: str) -> list[Issue]: ...

    def count(
        self, status: IssueStatus | None = None, issue_type: IssueType | None = None
    ) -> int: ...

    def _to_domain(self, model: IssueModel) -> Issue: ...

    def _to_model(self, issue: Issue, session: Session) -> IssueModel: ...
