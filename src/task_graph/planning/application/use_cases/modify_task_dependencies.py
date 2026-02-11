from task_graph.planning.domain.ports.task_repository import TaskRepository
from dataclasses import dataclass, field

from task_graph.planning.domain.services import CycleDetectionService
from task_graph.planning.domain.value_objects import TaskId


from pydantic import BaseModel, Field

class ModifyTaskDependenciesCommand(BaseModel):

    task_id: str
    added_dependencies: list[str] = Field(default_factory=list)
    removed_dependencies: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class ModifyTaskDependenciesResult:

    success: bool
    error: str = ""


@dataclass
class ModifyTaskDependencies:
    """Modify a task's dependencies (add or remove)."""

    repository: TaskRepository
    cycle_detector: CycleDetectionService

    def execute(
        self, cmd: ModifyTaskDependenciesCommand
    ) -> ModifyTaskDependenciesResult:
        try:
            target_id = TaskId.reconstitute(cmd.task_id)
            task = self.repository.get(target_id)
            if not task:
                return ModifyTaskDependenciesResult(False, f"Task {cmd.task_id} not found")

            # 1. 处理移除
            for rem_id_str in cmd.removed_dependencies:
                rem_id = TaskId.reconstitute(rem_id_str)
                if rem_id in task.dependencies:
                    task.dependencies.remove(rem_id)
                    # 如果需要维护 dependents:
                    # dep_task = self.repository.get(rem_id)
                    # if dep_task: dep_task.dependents.remove(target_id); self.repository.save(dep_task)

            # 2. 处理新增
            for add_id_str in cmd.added_dependencies:
                add_id = TaskId.reconstitute(add_id_str)

                # 校验是否存在
                if not self.repository.get(add_id):
                    return ModifyTaskDependenciesResult(False, f"Dependency {add_id_str} not found")

                # 环路检测 (关键步骤)
                if self.cycle_detector.detect_cycle(target_id, add_id, self.repository):
                    return ModifyTaskDependenciesResult(False, f"Cycle detected when adding dependency {add_id_str}")

                task.dependencies.add(add_id)
                # maintenance logic for dependents side omitted for brevity

            # 3. 保存
            self.repository.save(task)
            return ModifyTaskDependenciesResult(True)

        except Exception as e:
            return ModifyTaskDependenciesResult(False, str(e))
