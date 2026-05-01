from dataclasses import dataclass

from task_graph.planning.application.ports.task_query_service import TaskQueryService
from task_graph.planning.application.use_cases.complete_decomposition import (
    CompleteDecomposition,
    CompleteDecompositionCommand,
)
from task_graph.planning.application.use_cases.unlock_task import (
    UnlockTask,
    UnlockTaskCommand,
)
from task_graph.planning.domain.events import TaskCompleted
from task_graph.planning.domain.value_objects.task_id import TaskId


@dataclass
class OnTaskCompleted:
    complete_decomposition: CompleteDecomposition
    unlock_task: UnlockTask
    task_query_service: TaskQueryService

    def handle_complete_decomposition(self, event: TaskCompleted) -> None:
        cmd = CompleteDecompositionCommand(task_id=event.task_id)
        self.complete_decomposition.execute(cmd)

    def handle_unlock_task(self, event: TaskCompleted) -> None:
        task_id = TaskId.model_validate(event.task_id)
        dependents = self.task_query_service.find_dependents(task_id)

        for dependent in dependents:
            cmd = UnlockTaskCommand(task_id=dependent.id)
            self.unlock_task.execute(cmd)
