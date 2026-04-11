from pydantic import BaseModel, Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity
from dataclasses import dataclass
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.submitter import Submitter
import logging


logger = logging.getLogger(__name__)


class CreateIssueCommand(BaseModel):
    title: str
    description: str
    type: IssueType
    severity: Severity
    submitter_name: str


class CreateIssueResult(BaseModel):
    success: bool
    issue_id: str
    error: str = Field(default="")


@dataclass
class CreateIssue:
    """Create a new issue with initial status NEW"""

    uow: UnitOfWork

    def execute(self, cmd: CreateIssueCommand) -> CreateIssueResult:
        try:
            with self.uow:
                # Create submitter value object
                submitter = Submitter.create(
                    name=cmd.submitter_name,
                )

                # Create issue aggregate (automatically adds IssueCreatedEvent)
                issue = Issue.create(
                    title=cmd.title,
                    description=cmd.description,
                    issue_type=cmd.type,
                    severity=cmd.severity,
                    submitter=submitter,
                )

                # Persist issue
                self.uow.issues.save(issue)
                logger.info(f"Issue {issue.id} created with status {issue.status.value}")

                # Collect and publish all domain events
                events = issue.collect_events()
                logger.debug(f"Collected {len(events)} events from issue aggregate")
                for event in events:
                    self.uow.event_bus.publish(event)

                # Commit transaction
                self.uow.commit()

                return CreateIssueResult(success=True, issue_id=str(issue.id))
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return CreateIssueResult(success=False, issue_id="", error=str(e))
