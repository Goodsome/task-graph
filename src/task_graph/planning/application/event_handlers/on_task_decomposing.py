from dataclasses import dataclass

from task_graph.planning.application.use_cases.decompose_task import (
    DecomposeTask,
    DecomposeTaskCommand,
)
from task_graph.planning.domain.events import TaskDecomposing


@dataclass
class OnTaskDecomposing:
    decompose_task: DecomposeTask

    def handle_decompose_task(self, event: TaskDecomposing) -> None:
        """Handle TaskDecomposing event by triggering the DecomposeTask use case."""
        cmd = DecomposeTaskCommand(task_id=event.task_id)
        self.decompose_task.execute(cmd)
