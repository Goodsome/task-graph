from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId
from abc import ABC, abstractmethod
from task_graph.shared.domain.ports.repository import Repository


class TaskRepository(Repository[Task, TaskId], ABC):
    """Persistence interface for Tasks."""

    @abstractmethod
    def find_all_active(
        self,
        project_id: str | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    def find_by_ids(self, task_ids: set[TaskId]) -> list[Task]: ...

    @abstractmethod
    def find_by_parent_id(self, parent_id: TaskId) -> list[Task]: ...
