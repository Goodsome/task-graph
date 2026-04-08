import math
from dataclasses import dataclass
from typing import Optional

from task_graph.planning.domain.enums import TaskStatus, ScopeLevel
from task_graph.planning.application.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ListTasksQuery:

    project_id: Optional[str] = None
    page: int = 1
    page_size: int = 10
    status: Optional[TaskStatus] = None
    scope_level: Optional[ScopeLevel] = None
    search: Optional[str] = ""


@dataclass(frozen=True)
class ListTasksResult:

    tasks: list[dict]
    total_count: int
    total_pages: int
    current_page: int
    error: Optional[str] = None


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
                    page_size=query.page_size
                )
                
                total_pages = (
                    math.ceil(total_count / query.page_size) if total_count > 0 else 1
                )
                
                tasks_data = [t.to_summary_dict() for t in paged_tasks]
                
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
