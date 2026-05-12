from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.application.dtos.close_issue_command import (
    CloseIssueCommand,
)
from task_graph.issue_tracking.application.dtos.close_issue_result import (
    CloseIssueResult,
)
from typing import Self

logger = logging.getLogger(__name__)


@dataclass
class CloseIssue:
    """Close an issue that is in RESOLVED status"""

    uow: UnitOfWork[IssueRepository]

    def execute(self: Self, cmd: CloseIssueCommand) -> CloseIssueResult:
        try:
            with self.uow:
                issue_id = IssueId.reconstitute(cmd.issue_id)
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return CloseIssueResult(
                        success=False, error=f"Issue {cmd.issue_id} not found"
                    )
                issue.close(resolution=cmd.resolution)
                self.uow.repository.save(issue)
                logger.info(f"Issue {issue.id} closed")
                self.uow.commit()
                return CloseIssueResult(success=True)
        except Exception as e:
            return CloseIssueResult(success=False, error=str(e))
