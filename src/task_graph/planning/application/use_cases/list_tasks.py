import math
from dataclasses import dataclass
from typing import Optional

from task_graph.planning.domain.enums import PlanningLevel, TaskStatus
from task_graph.planning.domain.ports.task_repository import TaskRepository


@dataclass(frozen=True)
class ListTasksQuery:

    project_id: Optional[str] = None
    page: int = 1
    page_size: int = 10
    status: Optional[TaskStatus] = None
    planning_level: Optional[PlanningLevel] = None
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

    repository: TaskRepository

    def execute(self, query: ListTasksQuery) -> ListTasksResult:

        try:
            paged_tasks, total_count = self.repository.find_paged(
                status=query.status,
                project_id=query.project_id,
                planning_level=query.planning_level,
                search=query.search,
                page=query.page,
                page_size=query.page_size
            )
            
            total_pages = (
                math.ceil(total_count / query.page_size) if total_count > 0 else 1
            )
            
            tasks_data = [t.to_dict() for t in paged_tasks]
            
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
