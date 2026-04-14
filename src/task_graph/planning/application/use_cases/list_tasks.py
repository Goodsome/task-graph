import math
from dataclasses import dataclass

from task_graph.planning.domain.enums import TaskStatus, ScopeLevel
from task_graph.planning.application.ports.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ScopeContextSummary:
    """Summary of scope context for task listing"""

    bounded_context: str | None
    architecture_layer: str | None


@dataclass(frozen=True)
class SummaryTask:
    """Summary representation of a task for listing purposes"""

    id: str
    project_id: str
    name: str
    status: str
    scope_level: str
    scope_context: ScopeContextSummary | None
    parent_id: str | None
    effort: int
    base_value: float


@dataclass(frozen=True)
class ListTasksQuery:
    project_id: str | None = None
    page: int = 1
    page_size: int = 10
    status: TaskStatus | None = None
    scope_level: ScopeLevel | None = None
    search: str | None = ""


@dataclass(frozen=True)
class ListTasksResult:
    tasks: list[SummaryTask]
    total_count: int
    total_pages: int
    current_page: int
    error: str | None = None


@dataclass
class ListTasks:
    uow: UnitOfWork

    def execute(self, query: ListTasksQuery) -> ListTasksResult:

        try:
            with self.uow:
                paged_tasks, total_count = self.uow.tasks.find_paged(
                    status=query.status,
                    project_id=query.project_id,
                    scope_level=query.scope_level,
                    search=query.search,
                    page=query.page,
                    page_size=query.page_size,
                )

                total_pages = (
                    math.ceil(total_count / query.page_size) if total_count > 0 else 1
                )

                tasks_data: list[SummaryTask] = []
                for t in paged_tasks:
                    scope_context = None
                    if t.scope_context:
                        scope_context = ScopeContextSummary(
                            bounded_context=t.scope_context.bounded_context,
                            architecture_layer=t.scope_context.architecture_layer.value
                            if t.scope_context.architecture_layer
                            else None,
                        )

                    tasks_data.append(
                        SummaryTask(
                            id=str(t.id),
                            project_id=t.project_id,
                            name=t.name,
                            status=t.status.value,
                            scope_level=t.scope_level.value,
                            scope_context=scope_context,
                            parent_id=str(t.parent_id.value) if t.parent_id else None,
                            effort=t.effort.value,
                            base_value=t.base_value.value,
                        )
                    )

                return ListTasksResult(
                    tasks=tasks_data,
                    total_count=total_count,
                    total_pages=total_pages,
                    current_page=query.page,
                    error=None,
                )
        except Exception as e:
            return ListTasksResult(
                tasks=[],
                total_count=0,
                total_pages=0,
                current_page=query.page,
                error=str(e),
            )
