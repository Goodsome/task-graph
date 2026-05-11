from abc import ABC, abstractmethod

from task_graph.planning.application.dtos.summary_task import SummaryTask
from task_graph.planning.domain.enums import ScopeLevel, TaskStatus
from task_graph.planning.domain.value_objects.task_id import TaskId


class TaskQueryService(ABC):
    """Read-only query interface for tasks (CQRS query side).

    Implementations must return lightweight DTOs rather than full domain
    aggregates to avoid loading unnecessary data and coupling queries to
    the domain model.
    """

    @abstractmethod
    def find_paged(
        self,
        page: int,
        page_size: int,
        status: TaskStatus | None,
        project_id: str | None,
        scope_level: ScopeLevel | None,
        search: str | None,
    ) -> tuple[list[SummaryTask], int]:
        """Return a paginated list of task summaries and the total count."""
        ...

    @abstractmethod
    def find_dependents(self, task_id: TaskId) -> list[SummaryTask]:
        """Return summaries of all tasks that directly depend on *task_id*."""
        ...
