import math
from dataclasses import dataclass
from task_graph.planning.application.ports.task_query_service import TaskQueryService
from typing import Self
from task_graph.planning.application.dtos.list_tasks_result import ListTasksResult
from task_graph.planning.application.dtos.list_tasks_query import ListTasksQuery


@dataclass
class ListTasks:
    query_service: TaskQueryService

    def execute(self: Self, query: ListTasksQuery) -> ListTasksResult:
        try:
            paged_tasks, total_count = self.query_service.find_paged(
                status=query.status,
                project_id=query.project_id,
                scope_level=query.scope_level,
                search=query.search,
                page=query.page,
                page_size=query.page_size,
                exclude_status=query.exclude_status,
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
