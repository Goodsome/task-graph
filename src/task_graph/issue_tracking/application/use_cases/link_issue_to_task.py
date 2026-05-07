from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId

logger = logging.getLogger(__name__)
class LinkIssueToTaskCommand(BaseModel):
    issue_id: str
    task_id: str
class LinkIssueToTaskResult(BaseModel):
    success: bool
    error: str = Field(default="")
@dataclass
class LinkIssueToTask:
    """Link an issue to a task from Planning context"""

    uow: UnitOfWork[IssueRepository]

    def execute(self, cmd: LinkIssueToTaskCommand) -> LinkIssueToTaskResult:
        try:
            with self.uow:
                # Parse issue ID
                issue_id = IssueId.reconstitute(cmd.issue_id)

                # Find issue
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return LinkIssueToTaskResult(
                        success=False,
                        error=f"Issue {cmd.issue_id} not found"
                    )

                # Link to task
                issue.link_to_task(task_id=cmd.task_id)

                # Persist changes
                self.uow.repository.save(issue)
                logger.info(f"Issue {issue.id} linked to task {cmd.task_id}")
                # Commit transaction
                self.uow.commit()

                return LinkIssueToTaskResult(success=True)
        except Exception as e:
            return LinkIssueToTaskResult(
                success=False,
                error=str(e)
            )
