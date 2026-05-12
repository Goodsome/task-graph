from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.services.issue_status_transition_service import (
    IssueStatusTransitionService,
)
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.application.dtos.update_issue_status_command import (
    UpdateIssueStatusCommand,
)
from typing import Self
from task_graph.issue_tracking.application.dtos.update_issue_status_result import (
    UpdateIssueStatusResult,
)

logger = logging.getLogger(__name__)


@dataclass
class UpdateIssueStatus:
    """Update issue status with state machine validation"""

    uow: UnitOfWork[IssueRepository]
    status_transition_service: IssueStatusTransitionService

    def execute(self: Self, cmd: UpdateIssueStatusCommand) -> UpdateIssueStatusResult:
        try:
            with self.uow:
                issue_id = IssueId.reconstitute(cmd.issue_id)
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return UpdateIssueStatusResult(
                        success=False, error=f"Issue {cmd.issue_id} not found"
                    )
                self.status_transition_service.validate_transition(
                    current_status=issue.status, target_status=cmd.new_status
                )
                issue.change_status(
                    new_status=cmd.new_status, changed_by=cmd.changed_by
                )
                self.uow.repository.save(issue)
                logger.info(
                    f"Issue {issue.id} status changed to {cmd.new_status.value} by {cmd.changed_by}"
                )
                self.uow.commit()
                return UpdateIssueStatusResult(success=True)
        except Exception as e:
            return UpdateIssueStatusResult(success=False, error=str(e))
