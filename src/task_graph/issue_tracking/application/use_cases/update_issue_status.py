from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging
from task_graph.issue_tracking.domain.enums import IssueStatus
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.services.issue_status_transition_service import (
    IssueStatusTransitionService,
)
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId

logger = logging.getLogger(__name__)


class UpdateIssueStatusCommand(BaseModel):
    issue_id: str
    new_status: IssueStatus
    changed_by: str


class UpdateIssueStatusResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class UpdateIssueStatus:
    """Update issue status with state machine validation"""

    uow: UnitOfWork
    status_transition_service: IssueStatusTransitionService

    def execute(self, cmd: UpdateIssueStatusCommand) -> UpdateIssueStatusResult:
        try:
            with self.uow:
                # Parse issue ID
                issue_id = IssueId.reconstitute(cmd.issue_id)

                # Find issue
                issue = self.uow.issues.find_by_id(issue_id)
                if not issue:
                    return UpdateIssueStatusResult(
                        success=False,
                        error=f"Issue {cmd.issue_id} not found"
                    )

                # Validate transition
                self.status_transition_service.validate_transition(
                    current_status=issue.status,
                    target_status=cmd.new_status
                )

                # Update status
                issue.change_status(
                    new_status=cmd.new_status,
                    changed_by=cmd.changed_by
                )

                # Persist changes
                self.uow.issues.save(issue)
                logger.info(f"Issue {issue.id} status changed to {cmd.new_status.value} by {cmd.changed_by}")

                # Collect and publish all domain events
                events = issue.collect_events()
                logger.debug(f"Collected {len(events)} events from issue aggregate")
                for event in events:
                    self.uow.event_bus.publish(event)

                # Commit transaction
                self.uow.commit()

                return UpdateIssueStatusResult(success=True)
        except Exception as e:
            return UpdateIssueStatusResult(
                success=False,
                error=str(e)
            )

