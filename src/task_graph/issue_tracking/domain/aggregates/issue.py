from __future__ import annotations
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.shared.models import Aggregate
from task_graph.issue_tracking.domain.value_objects.submitter import Submitter
from task_graph.issue_tracking.domain.value_objects.issue_description import (
    IssueDescription,
)
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from datetime import datetime
from task_graph.issue_tracking.domain.entities.comment import Comment
from task_graph.issue_tracking.domain.value_objects.issue_title import IssueTitle
from task_graph.issue_tracking.domain.value_objects.task_link import TaskLink
from task_graph.issue_tracking.domain.value_objects.label import Label
from typing import Any, Self, Union


class Issue(Aggregate):
    """Issue aggregate root managing the complete issue lifecycle"""

    id: IssueId
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

    @classmethod
    def create(
        cls: type[Self],
        title: str,
        description: str,
        type: IssueType,
        severity: Severity,
        submitter: Submitter,
    ) -> Self: ...

    def change_status(self, new_status: IssueStatus, changed_by: str) -> None: ...

    def close(self, resolution: str | None = None) -> None: ...

    def add_comment(self, content: str, author: str) -> Comment: ...

    def add_label(self, label: Label) -> None: ...

    def remove_label(self, label_name: str) -> None: ...

    def link_to_task(self, task_id: str) -> TaskLink: ...

    def unlink_from_task(self, task_id: str) -> None: ...

    def update_metadata(
        self, type: IssueType | None = None, severity: Severity | None = None
    ) -> None: ...

    def reconstitute(self) -> Self: ...

    def to_dict(self) -> dict: ...
