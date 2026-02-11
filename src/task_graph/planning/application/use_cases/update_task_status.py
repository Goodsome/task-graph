from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.ports.task_repository import TaskRepository
from dataclasses import dataclass

from task_graph.planning.domain.services import DependencyResolutionService
from task_graph.planning.domain.value_objects import TaskId


from pydantic import BaseModel

class UpdateTaskStatusCommand(BaseModel):

    task_id: str
    new_status: str


@dataclass(frozen=True)
class UpdateTaskStatusResult:

    success: bool
    affected_tasks: list[str]
    error: str = ""


@dataclass
class UpdateTaskStatus:
    """Updates a task's status and triggers chain reactions for dependents."""

    repository: TaskRepository
    resolution_service: DependencyResolutionService

    def execute(self, cmd: UpdateTaskStatusCommand) -> UpdateTaskStatusResult:
        try:
            task_id = TaskId.reconstitute(cmd.task_id)
            task = self.repository.get(task_id)
            if not task:
                return UpdateTaskStatusResult(False, [], f"Task {cmd.task_id} not found")

            try:
                new_status_enum = TaskStatus(cmd.new_status.lower())
            except ValueError:
                return UpdateTaskStatusResult(False, [], f"Invalid status: {cmd.new_status}")

            # 更新当前任务
            task.status = new_status_enum
            self.repository.save(task)

            affected_ids = []

            # 连锁反应：如果任务完成了，检查它的下游任务是否可以被解锁
            if task.is_done():
                # 使用 Repository 反向查找依赖我的任务
                dependents = self.repository.find_dependents(task.id)

                for dependent in dependents:
                    # 只有当前被阻塞或等待的任务才需要检查
                    if dependent.status in [TaskStatus.BLOCKED, TaskStatus.PENDING]:
                        # 调用领域服务判断是否仍被阻塞
                        is_blocked = self.resolution_service.evaluate_blocking_status(dependent, self.repository)

                        if not is_blocked:
                            # 解锁：PENDING/BLOCKED -> READY
                            dependent.status = TaskStatus.READY
                            self.repository.save(dependent)
                            affected_ids.append(str(dependent.id.value))

            return UpdateTaskStatusResult(True, affected_ids)

        except Exception as e:
            return UpdateTaskStatusResult(False, [], str(e))
        
