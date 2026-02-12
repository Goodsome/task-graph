from task_graph.planning.domain.aggregates.task import Task
from typing import Union, Optional
from task_graph.planning.domain.value_objects.task_id import TaskId
from uuid import UUID
from abc import abstractmethod, ABC
from task_graph.planning.domain.enums import TaskStatus, PlanningLevel


class TaskRepository(ABC):
    """Persistence interface for Tasks."""

    @abstractmethod
    def save(self, task: Task) -> None: ...

    @abstractmethod
    def get(self, task_id: TaskId) -> Optional[Task]: ...

    @abstractmethod
    def find_all_active(
        self,
        project_id: Optional[str] = None,
    ) -> list[Task]: ...

    @abstractmethod
    def find_all(
        self,
    ) -> list[Task]: ...

    @abstractmethod
    def find_dependents(self, task_id: TaskId) -> list[Task]: ...

    @abstractmethod
    def delete(self, task_id: TaskId) -> None: ...

    @abstractmethod
    def find_by_id(self, task_id: TaskId) -> Task | None: ...

    @abstractmethod
    def find_by_ids(self, task_ids: set[TaskId]) -> list[Task]: ...

    @abstractmethod
    def find_paged(
        self,
        status: Optional[TaskStatus],
        project_id: Optional[str],
        planning_level: Optional[PlanningLevel],
        search: Optional[str],
        page: int,
        page_size: int,
    ) -> tuple[list[Task], int]: ...
