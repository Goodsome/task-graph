from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.domain.value_objects.label import Label
from task_graph.issue_tracking.application.dtos.update_issue_metadata_command import (
    UpdateIssueMetadataCommand,
)
from typing import Self
from task_graph.issue_tracking.application.dtos.update_issue_metadata_result import (
    UpdateIssueMetadataResult,
)

logger = logging.getLogger(__name__)


@dataclass
class UpdateIssueMetadata:
    """Update issue metadata like type, severity, and labels"""

    uow: UnitOfWork[IssueRepository]

    def execute(
        self: Self, cmd: UpdateIssueMetadataCommand
    ) -> UpdateIssueMetadataResult:
        try:
            with self.uow:
                issue_id = IssueId.reconstitute(cmd.issue_id)
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return UpdateIssueMetadataResult(
                        success=False, error=f"Issue {cmd.issue_id} not found"
                    )
                issue.update_metadata(issue_type=cmd.type, severity=cmd.severity)
                if cmd.add_labels:
                    for label_name in cmd.add_labels:
                        label = Label.create(name=label_name)
                        issue.add_label(label)
                if cmd.remove_labels:
                    for label_name in cmd.remove_labels:
                        issue.remove_label(label_name)
                self.uow.repository.save(issue)
                logger.info(f"Issue {issue.id} metadata updated")
                self.uow.commit()
                return UpdateIssueMetadataResult(success=True)
        except Exception as e:
            return UpdateIssueMetadataResult(success=False, error=str(e))
