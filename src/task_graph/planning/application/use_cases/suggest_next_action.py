from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.services.priority_analysis_service import (
    PriorityAnalysisService,
)
from dataclasses import dataclass
from task_graph.planning.application.ports.unit_of_work import UnitOfWork


from typing import Optional
from pydantic import BaseModel

class SuggestNextActionQuery(BaseModel):

    top_n: int
    project_id: Optional[str] = None


@dataclass(frozen=True)
class SuggestNextActionResult:

    tasks: list[Task]


@dataclass
class SuggestNextAction:
    """Returns the highest priority tasks that are ready to execute."""

    uow: UnitOfWork
    priority_service: PriorityAnalysisService

    def execute(self, query: SuggestNextActionQuery) -> SuggestNextActionResult:
        with self.uow:
            # 1. 计算全图优先级
            sorted_tasks = self.priority_service.calculate_priorities(self.uow.tasks, project_id=query.project_id)

            actionable_tasks = [
                t for t in sorted_tasks
                if t.is_claimable()
            ]

            # 3. 取 Top N
            top_tasks = actionable_tasks[:query.top_n]

            return SuggestNextActionResult(tasks=top_tasks)
