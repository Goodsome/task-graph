from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.services.priority_analysis_service import (
    PriorityAnalysisService,
)
from dataclasses import dataclass
from task_graph.planning.domain.ports.task_repository import TaskRepository


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

    repository: TaskRepository
    priority_service: PriorityAnalysisService

    def execute(self, query: SuggestNextActionQuery) -> SuggestNextActionResult:
        # 1. 计算全图优先级
        sorted_tasks = self.priority_service.calculate_priorities(self.repository, project_id=query.project_id)

        # 2. 过滤：只推荐 READY 或 IN_PROGRESS 的任务
        # 我们通常建议用户处理已经准备好 (READY) 或正在进行 (IN_PROGRESS) 的任务
        actionable_tasks = [
            t for t in sorted_tasks
            if t.status in (TaskStatus.READY, TaskStatus.IN_PROGRESS)
        ]

        # 3. 取 Top N
        top_tasks = actionable_tasks[:query.top_n]

        return SuggestNextActionResult(tasks=top_tasks)
