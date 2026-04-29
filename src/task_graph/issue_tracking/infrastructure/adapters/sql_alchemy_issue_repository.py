from __future__ import annotations
from typing import Self, cast
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.infrastructure.orm_models.issue_model import (
    IssueModel,
    IssueCommentModel,
    IssueTaskLinkModel,
)
from dataclasses import dataclass


@dataclass
class SqlAlchemyIssueRepository(IssueRepository):
    """SQLAlchemy implementation of IssueRepository"""

    session: Session

    def save(self: Self, issue: Issue) -> None:
        """Save or update an issue aggregate"""
        model = self._to_model(issue)
        self.session.add(model)
        self.session.flush()

    def find_by_id(self: Self, issue_id: IssueId) -> Issue | None:
        """Find an issue by its ID"""
        stmt = select(IssueModel).options(
            joinedload(IssueModel.comments),
            joinedload(IssueModel.task_links)
        ).where(IssueModel.id == issue_id.value)

        model = self.session.execute(stmt).unique().scalar_one_or_none()
        return self._to_domain(model) if model else None

    def find_all(
        self: Self,
        limit: int,
        offset: int,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
        project_id: str | None = None,
    ) -> list[Issue]:
        """Find all issues with optional filters"""
        stmt = select(IssueModel).options(
            joinedload(IssueModel.comments),
            joinedload(IssueModel.task_links)
        ).order_by(IssueModel.created_at.desc())

        if status is not None:
            stmt = stmt.where(IssueModel.status == status)
        if issue_type is not None:
            stmt = stmt.where(IssueModel.type == issue_type)
        if severity is not None:
            stmt = stmt.where(IssueModel.severity == severity)
        if labels is not None and len(labels) > 0:
            stmt = stmt.where(IssueModel.labels.contains(labels))
        if project_id is not None:
            stmt = stmt.where(IssueModel.project_id == project_id)

        stmt = stmt.limit(limit).offset(offset)
        models = self.session.execute(stmt).unique().scalars().all()

        return [self._to_domain(model) for model in models]

    def delete(self: Self, issue_id: IssueId) -> bool:
        """Delete an issue by ID"""
        model = self.session.get(IssueModel, issue_id.value)
        if model:
            self.session.delete(model)
            self.session.flush()
            return True
        return False

    def find_by_task_id(self: Self, task_id: str) -> list[Issue]:
        """Find all issues linked to a specific task ID"""
        stmt = select(IssueModel).join(IssueTaskLinkModel).where(
            IssueTaskLinkModel.task_id == task_id
        ).options(
            joinedload(IssueModel.comments),
            joinedload(IssueModel.task_links)
        )

        models = self.session.execute(stmt).unique().scalars().all()
        return [self._to_domain(model) for model in models]

    def count(
        self: Self,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
        project_id: str | None = None,
    ) -> int:
        """Count issues with optional filters"""
        stmt = select(func.count(IssueModel.id))

        if status is not None:
            stmt = stmt.where(IssueModel.status == status)
        if issue_type is not None:
            stmt = stmt.where(IssueModel.type == issue_type)
        if severity is not None:
            stmt = stmt.where(IssueModel.severity == severity)
        if labels is not None and len(labels) > 0:
            stmt = stmt.where(IssueModel.labels.contains(labels))
        if project_id is not None:
            stmt = stmt.where(IssueModel.project_id == project_id)

        return cast(int, self.session.scalar(stmt))

    def find_paged(
        self: Self,
        limit: int,
        offset: int,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        severity: Severity | None = None,
        labels: list[str] | None = None,
        project_id: str | None = None,
    ) -> tuple[list[Issue], int]:
        """
        Find paginated issues with filtering and return both the list and total count.
        This ensures consistency between the returned list and count by using the same filters.
        """
        # First get the total count with all filters
        total_count = self.count(
            status=status,
            issue_type=issue_type,
            severity=severity,
            labels=labels,
            project_id=project_id
        )

        # Then get the paginated list
        issues = self.find_all(
            limit=limit,
            offset=offset,
            status=status,
            issue_type=issue_type,
            severity=severity,
            labels=labels,
            project_id=project_id
        )

        return issues, total_count

    def _to_domain(self: Self, model: IssueModel) -> Issue:
        """Convert ORM model to domain aggregate"""
        # 构建 labels: IssueModel.labels 是 List[str]，直接映射
        labels = [label for label in model.labels]

        data = {
            "id": model.id,
            "project_id": model.project_id,
            "title": model.title,
            "description": model.description,
            "type": model.type,
            "severity": model.severity,
            "status": model.status,
            "submitter": {"name": model.submitter_name},
            "labels": labels,
            "comments": model.comments,
            "task_links": model.task_links,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
        return Issue.model_validate(data)

    def _to_model(self: Self, issue: Issue) -> IssueModel:
        """Convert domain aggregate to ORM model"""
        model = self.session.get(IssueModel, issue.id.value)

        if not model:
            model = IssueModel(id=issue.id.value)

        model.project_id = issue.project_id
        model.title = issue.title.value
        model.description = issue.description.value
        model.type = issue.type
        model.severity = issue.severity
        model.status = issue.status
        model.submitter_name = issue.submitter.name
        model.labels = [label.name for label in issue.labels]
        model.created_at = issue.created_at
        model.updated_at = issue.updated_at

        # Update comments
        existing_comment_ids = {str(c.id) for c in model.comments}
        for comment in issue.comments:
            if str(comment.id.value) not in existing_comment_ids:
                model.comments.append(IssueCommentModel(
                    id=comment.id.value,
                    content=comment.content,
                    author=comment.author,
                    created_at=comment.created_at
                ))

        # Update task links
        existing_task_ids = {tl.task_id for tl in model.task_links}
        for task_link in issue.task_links:
            task_id_str = str(task_link.task_id)
            if task_id_str not in existing_task_ids:
                model.task_links.append(IssueTaskLinkModel(
                    task_id=task_id_str,
                    linked_at=task_link.linked_at
                ))

        # Remove deleted task links
        current_task_ids = {str(tl.task_id) for tl in issue.task_links}
        model.task_links = [tl for tl in model.task_links if tl.task_id in current_task_ids]

        return model
