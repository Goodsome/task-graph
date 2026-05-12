from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from dataclasses import dataclass
from task_graph.planning.domain.value_objects import TaskId
from task_graph.planning.domain.services.cycle_detection_service import (
    CycleDetectionService,
)
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.application.dtos.modify_task_dependencies_command import (
    ModifyTaskDependenciesCommand,
)
from task_graph.planning.application.dtos.modify_task_dependencies_result import (
    ModifyTaskDependenciesResult,
)
from typing import Self


@dataclass
class ModifyTaskDependencies:
    uow: UnitOfWork[TaskRepository]
    cycle_detector: CycleDetectionService
    dependency_resolver: DependencyResolutionService

    def execute(
        self: Self, cmd: ModifyTaskDependenciesCommand
    ) -> ModifyTaskDependenciesResult:
        try:
            with self.uow:
                target_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(target_id)
                for rem_id_str in cmd.removed_dependencies:
                    rem_id = TaskId.reconstitute(rem_id_str)
                    if rem_id in task.dependencies:
                        task.dependencies.remove(rem_id)
                for add_id_str in cmd.added_dependencies:
                    add_id = TaskId.reconstitute(add_id_str)
                    _ = self.uow.repository.get(add_id)
                    if self.cycle_detector.detect_cycle(
                        target_id, add_id, self.uow.repository
                    ):
                        return ModifyTaskDependenciesResult(
                            success=False,
                            error=f"Cycle detected when adding dependency {add_id_str}"
                        )
                    task.dependencies.add(add_id)
                is_blocked = self.dependency_resolver.evaluate_blocking_status(
                    task, self.uow.repository
                )
                if is_blocked:
                    if task.status == TaskStatus.READY:
                        task.mark_pending()
                elif task.status in (TaskStatus.PENDING, TaskStatus.BLOCKED):
                    task.mark_ready()
                self.uow.repository.save(task)
                self.uow.commit()
                return ModifyTaskDependenciesResult(success=True)
        except Exception as e:
            return ModifyTaskDependenciesResult(success=False,error=str(e))
