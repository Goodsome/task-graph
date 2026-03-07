from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.application.unit_of_work import UnitOfWork
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

    uow: UnitOfWork
    resolution_service: DependencyResolutionService

    def execute(self, cmd: UpdateTaskStatusCommand) -> UpdateTaskStatusResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)
                if not task:
                    return UpdateTaskStatusResult(False, [], f"Task {cmd.task_id} not found")

                try:
                    new_status_enum = TaskStatus(cmd.new_status.lower())
                except ValueError:
                    return UpdateTaskStatusResult(False, [], f"Invalid status: {cmd.new_status}")

                # 更新当前任务
                task._update_status(new_status_enum)
                self.uow.tasks.save(task)

                affected_ids = []
                modified_dependents = []

                # 连锁反应：如果任务完成了，检查它的下游任务是否可以被解锁
                if task.is_done():
                    # 使用 Repository 反向查找依赖我的任务
                    dependents = self.uow.tasks.find_dependents(task.id)

                    for dependent in dependents:
                        # 只有当前被阻塞或等待的任务才需要检查
                        if dependent.status in [TaskStatus.BLOCKED, TaskStatus.PENDING]:
                            # 调用领域服务判断是否仍被阻塞
                            is_blocked = self.resolution_service.evaluate_blocking_status(dependent, self.uow.tasks)

                            if not is_blocked:
                                # 解锁：PENDING/BLOCKED -> READY
                                dependent._update_status(TaskStatus.READY)
                                self.uow.tasks.save(dependent)
                                affected_ids.append(str(dependent.id.value))
                                modified_dependents.append(dependent)

                for event in task.collect_events():
                    self.uow.event_bus.publish(event)
                for dep in modified_dependents:
                    for event in dep.collect_events():
                        self.uow.event_bus.publish(event)

                self.uow.commit()

                return UpdateTaskStatusResult(True, affected_ids)

        except Exception as e:
            return UpdateTaskStatusResult(False, [], str(e))
        
