from dataclasses import dataclass
from task_graph.issue_tracking.domain.enums import IssueStatus

_VALID_TRANSITIONS: dict[IssueStatus, set[IssueStatus]] = {
    IssueStatus.REPORTED: {
        IssueStatus.TRIAGED,
        IssueStatus.IN_PROGRESS,
        IssueStatus.RESOLVED,
        IssueStatus.CLOSED
    },
    IssueStatus.TRIAGED: {
        IssueStatus.IN_PROGRESS,
        IssueStatus.RESOLVED,
        IssueStatus.CLOSED
    },
    IssueStatus.IN_PROGRESS: {
        IssueStatus.RESOLVED,
        IssueStatus.CLOSED
    },
    IssueStatus.RESOLVED: {
        IssueStatus.CLOSED,
        IssueStatus.IN_PROGRESS  # Reopen
    },
    IssueStatus.CLOSED: set()  # No transitions from closed
}

@dataclass
class IssueStatusTransitionService:
    """Validates issue status transitions according to state machine rules"""


    def can_transition(
        self, current_status: IssueStatus, target_status: IssueStatus
    ) -> bool:
        """Check if transition from current_status to target_status is allowed"""
        if current_status == target_status:
            return True
        return target_status in _VALID_TRANSITIONS.get(current_status, set())

    def validate_transition(
        self, current_status: IssueStatus, target_status: IssueStatus
    ) -> None:
        """Validate transition, raise ValueError if invalid"""
        if not self.can_transition(current_status, target_status):
            raise ValueError(
                f"Invalid status transition: {current_status.value} → {target_status.value}"
            )

