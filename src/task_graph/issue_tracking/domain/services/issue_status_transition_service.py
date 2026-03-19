from dataclasses import dataclass
from task_graph.issue_tracking.domain.enums import IssueStatus


@dataclass
class IssueStatusTransitionService:
    """Validates issue status transitions according to state machine rules"""

    def can_transition(
        self, current_status: IssueStatus, target_status: IssueStatus
    ) -> bool: ...

    def validate_transition(
        self, current_status: IssueStatus, target_status: IssueStatus
    ) -> None: ...
