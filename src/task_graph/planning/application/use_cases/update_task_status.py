from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from dataclasses import dataclass

from task_graph.planning.domain.services import DependencyResolutionService
from task_graph.planning.domain.value_objects import TaskId
from task_graph.planning.domain.aggregates.task import Task


from pydantic import BaseModel

class UpdateTaskStatusCommand(BaseModel):

    task_id: str
    new_status: str


@dataclass(frozen=True)
class UpdateTaskStatusResult:

    success: bool
    affected_tasks: list[str]
    error: str = ""


_STATUS_TO_METHOD: dict[TaskStatus, str] = {
    TaskStatus.READY: "mark_ready",
    TaskStatus.IN_PROGRESS: "claim",
    TaskStatus.DONE: "mark_completed",
}


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

                # 通过行为方法映射表调用对应的领域方法
                method_name = _STATUS_TO_METHOD.get(new_status_enum)
                if method_name is None:
                    return UpdateTaskStatusResult(
                        False, [], f"Status '{cmd.new_status}' cannot be set directly via this use case"
                    )

                getattr(task, method_name)()
                self.uow.tasks.save(task)

                affected_ids = []
                modified_dependents = []

                # 连锁反应：如果任务完成了，检查它的下游任务是否可以被解锁
                if task.is_done():
                    modified_dependents = self._unlock_dependents(task)
                    affected_ids = [str(dep.id.value) for dep in modified_dependents]

                for event in task.collect_events():
                    self.uow.event_bus.publish(event)
                for dep in modified_dependents:
                    for event in dep.collect_events():
                        self.uow.event_bus.publish(event)

                self.uow.commit()

                return UpdateTaskStatusResult(True, affected_ids)

        except Exception as e:
            return UpdateTaskStatusResult(False, [], str(e))

    def _unlock_dependents(self, task: Task) -> list[Task]:
        """检查并解锁已满足依赖条件的下游任务。"""
        modified = []
        dependents = self.uow.tasks.find_dependents(task.id)

        for dependent in dependents:
            if dependent.status in (TaskStatus.BLOCKED, TaskStatus.PENDING):
                is_blocked = self.resolution_service.evaluate_blocking_status(
                    dependent, self.uow.tasks
                )
                if not is_blocked:
                    dependent.mark_ready()
                    self.uow.tasks.save(dependent)
                    modified.append(dependent)

        return modified
        
