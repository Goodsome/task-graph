from enum import Enum


class IssueType(Enum):
    """Classification of issue types"""

    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    IMPROVEMENT = "improvement"


class Severity(Enum):
    """Severity level of an issue"""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    LOW = "low"


class IssueStatus(Enum):
    """Lifecycle state of an issue"""

    REPORTED = "reported"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
