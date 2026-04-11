from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId

logger = logging.getLogger(__name__)


class UnlinkIssueFromTaskCommand(BaseModel):
    issue_id: str
    task_id: str


class UnlinkIssueFromTaskResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class UnlinkIssueFromTask:
    """Unlink an issue from a task"""

    uow: UnitOfWork

    def execute(self, cmd: UnlinkIssueFromTaskCommand) -> UnlinkIssueFromTaskResult:
        try:
            with self.uow:
                # Parse issue ID
                issue_id = IssueId.reconstitute(cmd.issue_id)

                # Find issue
                issue = self.uow.issues.find_by_id(issue_id)
                if not issue:
                    return UnlinkIssueFromTaskResult(
                        success=False,
                        error=f"Issue {cmd.issue_id} not found"
                    )

                # Unlink from task
                issue.unlink_from_task(task_id=cmd.task_id)

                # Persist changes
                self.uow.issues.save(issue)
                logger.info(f"Issue {issue.id} unlinked from task {cmd.task_id}")

                # Collect and publish all domain events
                events = issue.collect_events()
                logger.debug(f"Collected {len(events)} events from issue aggregate")
                for event in events:
                    self.uow.event_bus.publish(event)

                # Commit transaction
                self.uow.commit()

                return UnlinkIssueFromTaskResult(success=True)
        except Exception as e:
            return UnlinkIssueFromTaskResult(
                success=False,
                error=str(e)
            )

