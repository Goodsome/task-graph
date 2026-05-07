from dataclasses import dataclass, field
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId


@dataclass(frozen=True)
class DecomposeTaskCommand:
    """Command to decompose a task into sub-tasks."""
    task_id: str


@dataclass(frozen=True)
class DecomposeTaskResult:
    """Result of the DecomposeTask use case."""
    success: bool
    task_id: str
    sub_task_ids: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class DecomposeTask:
    """
    Decompose a task into sub-tasks.
    
    This use case:
    1. Retrieves the task by ID.
    2. Generates sub-tasks based on the task's output.
    3. Persists the new sub-tasks.
    4. Marks the original task as DELEGATED.
    5. Persists the original task.
    """
    uow: UnitOfWork[TaskRepository]

    def execute(self, cmd: DecomposeTaskCommand) -> DecomposeTaskResult:
        try:
            with self.uow:
                # 1. 获取任务
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)

                # 2. 生成子任务
                sub_tasks = task.generate_sub_tasks()
                
                # 3. 保存子任务
                for sub_task in sub_tasks:
                    self.uow.repository.add(sub_task)
                
                # 4. 标记原任务为 delegated
                task.mark_delegated()
                
                # 5. 保存原任务
                self.uow.repository.save(task)
                self.uow.commit()
                
                return DecomposeTaskResult(
                    success=True,
                    task_id=str(task.id),
                    sub_task_ids=[str(st.id) for st in sub_tasks]
                )
                
        except Exception as e:
            return DecomposeTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=str(e)
            )
