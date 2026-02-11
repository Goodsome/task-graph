from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from dataclasses import dataclass


@dataclass
class CycleDetectionService:
    """Ensures the planning graph remains a DAG."""

    def detect_cycle(
            self,
            target_task_id: TaskId,
            new_dependency_id: TaskId,
            repository: TaskRepository,
    ) -> bool:
        """
        Detects if adding a dependency (target -> new_dependency) would create a cycle.
        
        Logic:
            If we are adding a dependency where 'target' depends on 'new_dependency',
            a cycle exists if 'target' is already an ancestor of 'new_dependency'.
            We traverse up from 'new_dependency' to see if we can reach 'target'.
        """
        # 如果自依赖，直接返回 True
        if target_task_id == new_dependency_id:
            return True

        visited = set()
        stack = [new_dependency_id]

        while stack:
            current_id = stack.pop()

            if current_id == target_task_id:
                return True

            if current_id in visited:
                continue
            visited.add(current_id)

            # 获取当前任务以检查其依赖
            # 注意：这里需要处理 Repository 可能返回 None 的情况（虽然在事务中通常应存在）
            task = repository.get(current_id)
            if task:
                # 将当前任务的所有依赖加入搜索栈，继续向上回溯
                for dep_id in task.dependencies:
                    stack.append(dep_id)

        return False