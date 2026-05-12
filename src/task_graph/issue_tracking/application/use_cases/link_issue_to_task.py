from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.application.dtos.link_issue_to_task_command import (
    LinkIssueToTaskCommand,
)
from task_graph.issue_tracking.application.dtos.link_issue_to_task_result import (
    LinkIssueToTaskResult,
)
from typing import Self

logger = logging.getLogger(__name__)


@dataclass
class LinkIssueToTask:
    """Link an issue to a task from Planning context"""

    uow: UnitOfWork[IssueRepository]

    def execute(self: Self, cmd: LinkIssueToTaskCommand) -> LinkIssueToTaskResult:
        try:
            with self.uow:
                issue_id = IssueId.reconstitute(cmd.issue_id)
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return LinkIssueToTaskResult(
                        success=False, error=f"Issue {cmd.issue_id} not found"
                    )
                issue.link_to_task(task_id=cmd.task_id)
                self.uow.repository.save(issue)
                logger.info(f"Issue {issue.id} linked to task {cmd.task_id}")
                self.uow.commit()
                return LinkIssueToTaskResult(success=True)
        except Exception as e:
            return LinkIssueToTaskResult(success=False, error=str(e))
