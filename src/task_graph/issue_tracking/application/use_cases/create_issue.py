from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.submitter import Submitter
import logging
from task_graph.issue_tracking.application.dtos.create_issue_command import (
    CreateIssueCommand,
)
from typing import Self
from task_graph.issue_tracking.application.dtos.create_issue_result import (
    CreateIssueResult,
)

logger = logging.getLogger(__name__)


@dataclass
class CreateIssue:
    """Create a new issue with initial status NEW"""

    uow: UnitOfWork[IssueRepository]

    def execute(self: Self, cmd: CreateIssueCommand) -> CreateIssueResult:
        try:
            with self.uow:
                submitter = Submitter.create(name=cmd.submitter_name)
                issue = Issue.create(
                    project_id=cmd.project_id,
                    title=cmd.title,
                    description=cmd.description,
                    issue_type=cmd.type,
                    severity=cmd.severity,
                    submitter=submitter,
                )
                self.uow.repository.save(issue)
                logger.info(
                    f"Issue {issue.id} created with status {issue.status.value}"
                )
                self.uow.commit()
                return CreateIssueResult(success=True, issue_id=str(issue.id))
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return CreateIssueResult(success=False, issue_id="", error=str(e))
