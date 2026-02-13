from enum import Enum


class CompletionLogic(Enum):
    """Rules defining how a task is unlocked based on its dependencies."""

    ALL = "all"
    ANY = "any"


class TaskStatus(Enum):
    """The lifecycle state of a task."""

    PENDING = "pending"

    BLOCKED = "blocked"

    READY = "ready"

    IN_PROGRESS = "in_progress"

    REVIEW = "review"

    DONE = "done"

    CHANGES_REQUESTED = "changes_requested"

    SKIPPED = "skipped"

    DISCARDED = "discarded"


class PlanningLevel(Enum):
    """Defines the uncertainty and granularity of the task."""

    INITIATIVE = "initiative"

    MILESTONE = "milestone"

    ARCHITECTURAL = "architectural"

    FEATURE = "feature"

    ATOMIC = "atomic"


class RecurrenceType(Enum):

    ON_SUCCESS = "on_success"

    CRON = "cron"

    ON_FAILURE = "on_failure"
