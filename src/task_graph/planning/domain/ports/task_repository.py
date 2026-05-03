from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId
from abc import abstractmethod, ABC
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel


class TaskRepository(ABC):
    """Persistence interface for Tasks."""

    @abstractmethod
    def collect_seen_tasks(self) -> set[Task]: ...

    @abstractmethod
    def save(self, task: Task) -> None: ...

    @abstractmethod
    def add(self, task: Task) -> None: ...

    @abstractmethod
    def get(self, task_id: TaskId) -> Task:
        ...

    @abstractmethod
    def find_all_active(
        self,
        project_id: str | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    def delete(self, task_id: TaskId) -> None: ...

    @abstractmethod
    def find_by_ids(self, task_ids: set[TaskId]) -> list[Task]: ...

    @abstractmethod
    def find_by_parent_id(self, parent_id: TaskId) -> list[Task]: ...
