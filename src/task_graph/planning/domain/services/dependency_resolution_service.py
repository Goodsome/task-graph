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

        logic = task.completion_logic.value  # "all" or "any"

        if logic == "all":
            # ALL Logic: 只要有一个依赖没完成，就被阻塞 (True)
            # 即：Blocked if ANY dependency is NOT DONE.
            return any(not d.is_done() for d in dependencies)

        elif logic == "any":
            # ANY Logic: 只有当所有依赖都没完成时，才被阻塞 (True)
            # 即：Blocked if ALL dependencies are NOT DONE.
            # 只要有一个是 DONE，就不阻塞。
            return all(not d.is_done() for d in dependencies)

        return True  # Should not reach here