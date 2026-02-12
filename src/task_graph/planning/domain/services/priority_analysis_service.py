from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


@dataclass
class PriorityAnalysisService:
    """Calculates dynamic priority (ROI) for all tasks."""

    def calculate_priorities(self, repository: TaskRepository, project_id: Optional[str] = None) -> list[Task]:
        """
        Orchestrates the calculation of Dynamic Priority for all active tasks.
        
        Algorithm:
        1. Load Graph: Fetch all active tasks.
        2. Forward Propagation: Calculate Effective Effort (Cost to implement).
           - For OR nodes, takes the path of least resistance (Min).
        3. Backward Propagation: Calculate Accumulated Value (Business Value).
           - Value flows from Dependents back to Dependencies.
        4. Score: ROI = Accumulated Value / Effective Effort.
        """
        active_tasks = repository.find_all_active(project_id=project_id)
        task_map: Dict[TaskId, Task] = {t.id: t for t in active_tasks}

        # 构建反向依赖图 (In-memory Dependents Map) 用于价值回溯
        # map: task_id -> list of tasks that depend on it
        dependents_map: Dict[TaskId, List[TaskId]] = {tid: [] for tid in task_map}
        for task in active_tasks:
            for dep_id in task.dependencies:
                if dep_id in dependents_map:
                    dependents_map[dep_id].append(task.id)

        # Memoization Caches
        effort_cache: Dict[TaskId, float] = {}
        value_cache: Dict[TaskId, float] = {}

        # --- 2. Forward Propagation (Effective Effort) ---
        def get_effective_effort(tid: TaskId) -> float:
            if tid in effort_cache:
                return effort_cache[tid]

            task = task_map.get(tid)
            # 如果依赖的任务不在 active 列表中（意味着已 DONE 或 DISCARDED），
            # 视为该依赖节点的剩余 Effort 为 0。
            if not task:
                return 0.0

            dep_efforts = [get_effective_effort(d_id) for d_id in task.dependencies]

            context_effort = 0.0
            if dep_efforts:
                if task.completion_logic.value == "AND":
                    # 必须完成所有前置
                    context_effort = sum(dep_efforts)
                else: # OR
                    # 智能选择阻力最小的路径
                    context_effort = min(dep_efforts)

            # Node Effort = Self Effort + Dependencies Effort
            total_effort = task.effort.value + context_effort
            effort_cache[tid] = total_effort
            return total_effort

        # --- 3. Backward Propagation (Accumulated Value) ---
        def get_accumulated_value(tid: TaskId) -> float:
            if tid in value_cache:
                return value_cache[tid]

            task = task_map.get(tid)
            if not task:
                return 0.0

            # 递归获取所有下游任务（依赖我的人）的价值
            # Value(T) = BaseValue(T) + Sum(AccumulatedValue(Dependents))
            dependent_ids = dependents_map.get(tid, [])
            downstream_value = sum(get_accumulated_value(d_id) for d_id in dependent_ids)

            total_value = task.base_value.value + downstream_value
            value_cache[tid] = total_value
            return total_value

        # --- 4. Scoring & Sorting ---
        scored_tasks = []
        for task in active_tasks:
            eff = get_effective_effort(task.id)
            val = get_accumulated_value(task.id)

            # 避免除以零（极少情况，但需防护）
            if eff <= 0.001:
                eff = 0.001

            roi = val / eff

            # 我们不修改实体属性，而是利用 Python 的动态特性或封装 Tuple 返回
            # 这里为了演示，假设我们可以在运行时附加属性，或者直接用 Tuple 排序
            # 为了符合 Type Hint 返回 List[Task]，我们按顺序重排列表
            scored_tasks.append((roi, task))

        # 降序排列 (ROI 高的在前)
        scored_tasks.sort(key=lambda x: x[0], reverse=True)

        return [t for _, t in scored_tasks]