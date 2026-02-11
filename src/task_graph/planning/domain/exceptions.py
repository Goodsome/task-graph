class TaskNotClaimableError(Exception):
    """Raised when attempting to claim a task that is not in READY state."""
    pass


class IllegalStateTransitionError(Exception):
    """Raised when a task transition is invalid."""
    pass
