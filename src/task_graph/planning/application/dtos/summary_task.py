from dataclasses import dataclass


@dataclass(frozen=True)
class ScopeContextSummary:
    """Summary of scope context for task listing purposes."""

    bounded_context: str | None
    architecture_layer: str | None


@dataclass(frozen=True)
class SummaryTask:
    """Summary representation of a task for query-side read models."""

    id: str
    project_id: str
    name: str
    status: str
    scope_level: str
    scope_context: ScopeContextSummary | None
    parent_id: str | None
    effort: int
    base_value: float
