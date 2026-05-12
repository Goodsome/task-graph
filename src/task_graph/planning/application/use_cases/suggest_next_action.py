from task_graph.planning.domain.services.priority_analysis_service import (
    PriorityAnalysisService,
)
from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from typing import Self
from task_graph.planning.application.dtos.suggest_next_action_result import (
    SuggestNextActionResult,
)
from task_graph.planning.application.dtos.suggest_next_action_query import (
    SuggestNextActionQuery,
)


@dataclass
class SuggestNextAction:
    """Returns the highest priority tasks that are ready to execute."""

    uow: UnitOfWork[TaskRepository]
    priority_service: PriorityAnalysisService

    def execute(self: Self, query: SuggestNextActionQuery) -> SuggestNextActionResult:
        with self.uow:
            sorted_tasks = self.priority_service.calculate_priorities(
                self.uow.repository, project_id=query.project_id
            )
            actionable_tasks = [t for t in sorted_tasks if t.is_claimable()]
            top_tasks = actionable_tasks[: query.top_n]
            return SuggestNextActionResult(tasks=top_tasks)
