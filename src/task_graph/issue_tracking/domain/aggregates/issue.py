from __future__ import annotations
from datetime import datetime, timezone
from typing import Self, override

from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.issue_tracking.domain.entities.comment import Comment
from task_graph.issue_tracking.domain.value_objects.submitter import Submitter
from task_graph.issue_tracking.domain.value_objects.issue_description import (
    IssueDescription,
)
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.domain.value_objects.issue_title import IssueTitle
from task_graph.issue_tracking.domain.value_objects.task_link import TaskLink
from task_graph.issue_tracking.domain.value_objects.label import Label
from task_graph.shared.domain.core.aggregate_root import AggregateRoot
from task_graph.issue_tracking.domain.events import (
    IssueCreated,
    IssueStatusChanged,
    IssueClosed,
    IssueCommentAdded,
)


class Issue(AggregateRoot):
    """Issue aggregate root managing the complete issue lifecycle"""

    id: IssueId
    project_id: str
    title: IssueTitle
    description: IssueDescription
    type: IssueType
    severity: Severity
    status: IssueStatus
    submitter: Submitter
    labels: list[Label]
    comments: list[Comment]
    task_links: list[TaskLink]
    created_at: datetime
    updated_at: datetime

    @override
    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create(
        cls: type[Self],
        project_id: str,
        title: str,
        description: str,
        issue_type: IssueType,
        severity: Severity,
        submitter: Submitter,
    ) -> Self:
        """Create a new Issue aggregate"""
        now = datetime.now(timezone.utc)
        issue_id = IssueId.create()
        issue = cls(
            id=issue_id,
            project_id=project_id,
            title=IssueTitle.create(title),
            description=IssueDescription.create(description),
            type=issue_type,
            severity=severity,
            status=IssueStatus.REPORTED,
            submitter=submitter,
            labels=[],
            comments=[],
            task_links=[],
            created_at=now,
            updated_at=now,
        )
        # Add created event
        issue.add_domain_event(IssueCreated(
            issue_id=str(issue_id),
            project_id=project_id,
            title=title,
            type=issue_type,
            severity=severity,
            submitter_name=submitter.name,
        ))
        return issue

    def change_status(self: Self, new_status: IssueStatus, changed_by: str) -> None:
        """Change issue status with audit trail"""
        if self.status == new_status:
            return
        old_status = self.status
        # Add status change comment
        self.add_comment(f"Status changed from {self.status.value} to {new_status.value}", author=changed_by)
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        # Add status changed event
        self.add_domain_event(IssueStatusChanged(
            issue_id=str(self.id),
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        ))

    def close(self: Self, resolution: str | None = None) -> None:
        """Close the issue with optional resolution note"""
        if self.status == IssueStatus.CLOSED:
            return
        self.status = IssueStatus.CLOSED
        if resolution:
            # Add resolution as a system comment
            self.add_comment(f"Resolution: {resolution}", author="system")
        self.updated_at = datetime.now(timezone.utc)
        # Add closed event
        self.add_domain_event(IssueClosed(
            issue_id=str(self.id),
            resolution=resolution,
        ))

    def add_comment(self: Self, content: str, author: str) -> Comment:
        """Add a comment to the issue"""
        comment = Comment.create(content=content, author=author)
        self.comments.append(comment)
        self.updated_at = datetime.now(timezone.utc)
        # Add comment added event
        self.add_domain_event(IssueCommentAdded(
            issue_id=str(self.id),
            comment_id=str(comment.id),
            author=author,
            content=content,
        ))
        return comment

    def add_label(self: Self, label: Label) -> None:
        """Add a label to the issue (duplicates ignored)"""
        if label not in self.labels:
            self.labels.append(label)
            self.updated_at = datetime.now(timezone.utc)

    def remove_label(self: Self, label_name: str) -> None:
        """Remove a label from the issue by name"""
        self.labels = [l for l in self.labels if l.name != label_name]
        self.updated_at = datetime.now(timezone.utc)

    def link_to_task(self: Self, task_id: str) -> TaskLink:
        """Link this issue to a planning task"""
        # Check for existing link
        existing = next((tl for tl in self.task_links if tl.task_id == task_id), None)
        if existing:
            return existing

        task_link = TaskLink.create(task_id=task_id)
        self.task_links.append(task_link)
        self.updated_at = datetime.now(timezone.utc)
        return task_link

    def unlink_from_task(self: Self, task_id: str) -> None:
        """Remove link to a planning task"""
        self.task_links = [tl for tl in self.task_links if tl.task_id != task_id]
        self.updated_at = datetime.now(timezone.utc)

    def update_metadata(
        self: Self, issue_type: IssueType | None = None, severity: Severity | None = None
    ) -> None:
        """Update issue type and/or severity"""
        if issue_type is not None:
            self.type = issue_type
        if severity is not None:
            self.severity = severity
        if issue_type is not None or severity is not None:
            self.updated_at = datetime.now(timezone.utc)
