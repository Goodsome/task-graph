from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Set, Any, Dict

import yaml

from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus, PlanningLevel
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId

import logging

logger = logging.getLogger(__name__)


@dataclass
class YamlTaskRepository(TaskRepository):
    """
    Persistence adapter that stores tasks in a YAML file.
    Follows the structure:
    project: ...
    tasks:
      - id: ...
        name: ...
    """
    file_path: str = "C:\\Users\\86188\\code\\plan.yaml"
    # Simple in-memory cache to reduce file IO for repeated reads in same session
    _cache: Dict[str, Task] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure the file exists with a valid skeleton."""
        self.path = Path(self.file_path)
        if not self.path.exists():
            self._write_yaml({
                "project": "CodingAgent",
                "version": "3.2",
                "tasks": []
            })

    # --- Public Interface Implementation ---

    def save(self, task: Task) -> None:
        """Persists a task. Updates if exists, appends if new."""
        data = self._read_yaml()
        tasks_data = data.get("tasks", [])

        task_primitive = self._serialize_task(task)
        task_id_str = str(task.id.value)

        # Check for update or insert
        index = -1
        for i, t in enumerate(tasks_data):
            if t.get("id") == task_id_str:
                index = i
                break

        if index >= 0:
            tasks_data[index] = task_primitive
        else:
            tasks_data.append(task_primitive)

        data["tasks"] = tasks_data
        self._write_yaml(data)

        # Update cache
        self._cache[task_id_str] = task

    def get(self, task_id: TaskId) -> Optional[Task]:
        tid_str = str(task_id.value)
        if tid_str in self._cache:
            return self._cache[tid_str]

        # Scan file
        tasks = self._load_all_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def find_by_id(self, task_id: TaskId) -> Task | None:
        return self.get(task_id)

    def find_all_active(self) -> list[Task]:
        """Returns all tasks except those marked DONE or DISCARDED."""
        all_tasks = self._load_all_tasks()
        return [
            t for t in all_tasks
            if t.status not in (TaskStatus.DONE, TaskStatus.DISCARDED)
        ]

    def find_all(self) -> list[Task]:
        return self._load_all_tasks()

    def find_dependents(self, task_id: TaskId) -> list[Task]:
        """Finds all tasks that depend on the given task_id."""
        all_tasks = self._load_all_tasks()
        dependents = []
        target_id_str = str(task_id.value)
        for t in all_tasks:
            # Match by string value to be robust against type differences (TaskId vs string UUID)
            if any(str(d) == target_id_str for d in t.dependencies):
                dependents.append(t)
        return dependents

    def find_paged(
        self,
        status: Optional[TaskStatus] = None,
        planning_level: Optional[PlanningLevel] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Task], int]:
        """Finds tasks with filtering and pagination."""
        all_tasks = self._load_all_tasks()
        
        filtered_tasks = all_tasks
        
        # 1. Filter by status
        if status:
            filtered_tasks = [t for t in filtered_tasks if t.status == status]
            
        # 2. Filter by planning level
        if planning_level:
            filtered_tasks = [t for t in filtered_tasks if t.planning_level == planning_level]
            
        # 3. Filter by search keyword
        if search and search.strip():
            keyword = search.lower()
            filtered_tasks = [
                t for t in filtered_tasks 
                if keyword in t.name.lower() or keyword in t.description.lower()
            ]
            
        total_count = len(filtered_tasks)
        
        # 4. Pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paged_tasks = filtered_tasks[start_index:end_index]
        
        return paged_tasks, total_count

    def find_by_ids(self, task_ids: Set[TaskId]) -> list[Task]:
        if not task_ids:
            return []

        all_tasks = self._load_all_tasks()
        target_str_ids = {str(tid.value) for tid in task_ids}

        return [t for t in all_tasks if str(t.id.value) in target_str_ids]

    def delete(self, task_id: TaskId) -> None:
        data = self._read_yaml()
        tasks_data = data.get("tasks", [])

        target_str = str(task_id.value)
        new_tasks_data = [t for t in tasks_data if t.get("id") != target_str]

        if len(new_tasks_data) != len(tasks_data):
            data["tasks"] = new_tasks_data
            self._write_yaml(data)
            if target_str in self._cache:
                del self._cache[target_str]

    # --- Private Helpers (Serialization & IO) ---

    def _read_yaml(self) -> Dict[str, Any]:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                return content if content else {"tasks": []}
        except Exception:
            return {"tasks": []}

    def _write_yaml(self, data: Dict[str, Any]) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            # allow_unicode=True ensures Chinese characters are readable
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    def _load_all_tasks(self) -> List[Task]:
        """Reads disk, deserializes all tasks, and refreshes cache."""
        data = self._read_yaml()
        raw_list = data.get("tasks", [])
        domain_tasks = []

        for raw in raw_list:
            try:
                task = self._deserialize_task(raw)
                domain_tasks.append(task)
                self._cache[str(task.id.value)] = task
            except Exception as e:
                # Robustness: Skip malformed tasks but log warning (print for CLI)
                print(f"[WARN] Failed to load task {raw.get('id', 'unknown')}: {e}")
                continue

        return domain_tasks

    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Domain Object -> Python Primitive Dict"""
        return task.to_dict()

    def _deserialize_task(self, raw: Dict[str, Any]) -> Task:
        """Python Primitive Dict -> Domain Object"""
        t = Task.reconstitute(
            task_id=raw["id"],
            name=raw["name"],
            description=raw.get("description", ""),
            status=raw["status"],
            effort=raw.get("effort", 1),
            base_value=raw.get("base_value", 0.0),
            completion_logic=raw["completion_logic"],
            dependencies=set(raw.get("dependencies", [])),
            planning_level=raw["planning_level"],
            output=raw["output"],
        )

        return t