from pydantic import BaseModel, Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity
from dataclasses import dataclass
import logging
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.domain.value_objects.label import Label

logger = logging.getLogger(__name__)


class UpdateIssueMetadataCommand(BaseModel):
    issue_id: str
    type: IssueType | None = Field(default=None)
    severity: Severity | None = Field(default=None)
    add_labels: list[str] | None = Field(default=None)
    remove_labels: list[str] | None = Field(default=None)


class UpdateIssueMetadataResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class UpdateIssueMetadata:
    """Update issue metadata like type, severity, and labels"""

    uow: UnitOfWork

    def execute(self, cmd: UpdateIssueMetadataCommand) -> UpdateIssueMetadataResult:
        try:
            with self.uow:
                # Parse issue ID
                issue_id = IssueId.reconstitute(cmd.issue_id)

                # Find issue
                issue = self.uow.issues.find_by_id(issue_id)
                if not issue:
                    return UpdateIssueMetadataResult(
                        success=False,
                        error=f"Issue {cmd.issue_id} not found"
                    )

                # Update type and severity
                issue.update_metadata(
                    issue_type=cmd.type,
                    severity=cmd.severity
                )

                # Add labels
                if cmd.add_labels:
                    for label_name in cmd.add_labels:
                        label = Label.create(name=label_name)
                        issue.add_label(label)

                # Remove labels
                if cmd.remove_labels:
                    for label_name in cmd.remove_labels:
                        issue.remove_label(label_name)

                # Persist changes
                self.uow.issues.save(issue)
                logger.info(f"Issue {issue.id} metadata updated")

                # Collect and publish all domain events
                events = issue.collect_events()
                logger.debug(f"Collected {len(events)} events from issue aggregate")
                for event in events:
                    self.uow.event_bus.publish(event)

                # Commit transaction
                self.uow.commit()

                return UpdateIssueMetadataResult(success=True)
        except Exception as e:
            return UpdateIssueMetadataResult(
                success=False,
                error=str(e)
            )

