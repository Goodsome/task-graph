from task_graph.planning.domain.enums import TaskStatus
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
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


_STATUS_TO_METHOD: dict[TaskStatus, str] = {
    TaskStatus.READY: "mark_ready",
    TaskStatus.IN_PROGRESS: "claim",
    TaskStatus.DONE: "mark_completed",
}


@dataclass
class UpdateTaskStatus:
    """Updates a task's status and triggers chain reactions for dependents."""

    uow: UnitOfWork[TaskRepository]
    resolution_service: DependencyResolutionService

    def execute(self, cmd: UpdateTaskStatusCommand) -> UpdateTaskStatusResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)

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
                self.uow.repository.save(task)

                affected_ids = []

                self.uow.commit()

                return UpdateTaskStatusResult(True, affected_ids)

        except Exception as e:
            return UpdateTaskStatusResult(False, [], str(e))
