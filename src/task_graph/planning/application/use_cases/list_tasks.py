import math
from dataclasses import dataclass

from task_graph.planning.application.dtos.summary_task import SummaryTask
from task_graph.planning.application.ports.task_query_service import TaskQueryService
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel


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
    query_service: TaskQueryService

    def execute(self, query: ListTasksQuery) -> ListTasksResult:
        try:
            paged_tasks, total_count = self.query_service.find_paged(
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

            return ListTasksResult(
                tasks=paged_tasks,
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
