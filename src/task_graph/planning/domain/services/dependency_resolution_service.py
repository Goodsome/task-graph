from dataclasses import dataclass

from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.ports.task_repository import TaskRepository


@dataclass
class DependencyResolutionService:

    def evaluate_blocking_status(
            self, task: Task, repository: TaskRepository
    ) -> bool:
        """
        Evaluates whether a task is blocked based on its dependencies and completion logic.
        
        Returns:
            True if blocked (dependencies not satisfied).
            False if unblocked (ready to proceed).
        """
        if not task.dependencies:
            return False

        # 批量获取依赖任务对象
        dependencies = repository.find_by_ids(task.dependencies)
        return any(not d.is_done() for d in dependencies)
