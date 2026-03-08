from task_graph.planning.application.unit_of_work import UnitOfWork
from dataclasses import dataclass, field
from task_graph.planning.domain.services import CycleDetectionService
from task_graph.planning.domain.value_objects import TaskId
from pydantic import BaseModel, Field
from task_graph.planning.domain.services.cycle_detection_service import (
    CycleDetectionService,
)
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.enums import TaskStatus


@dataclass(frozen=True)
class ModifyTaskDependenciesCommand:

    task_id: str
    added_dependencies: list[str] = field(default_factory=list)
    removed_dependencies: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ModifyTaskDependenciesResult:

    success: bool
    error: str = field(default_factory=str)


@dataclass
class ModifyTaskDependencies:

    uow: UnitOfWork
    cycle_detector: CycleDetectionService
    dependency_resolver: DependencyResolutionService

    def execute(
        self, cmd: ModifyTaskDependenciesCommand
    ) -> ModifyTaskDependenciesResult:

        try:
            with self.uow:
                target_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(target_id)
                if not task:
                    return ModifyTaskDependenciesResult(
                        False, f"Task {cmd.task_id} not found"
                    )
                for rem_id_str in cmd.removed_dependencies:
                    rem_id = TaskId.reconstitute(rem_id_str)
                    if rem_id in task.dependencies:
                        task.dependencies.remove(rem_id)
                for add_id_str in cmd.added_dependencies:
                    add_id = TaskId.reconstitute(add_id_str)
                    if not self.uow.tasks.get(add_id):
                        return ModifyTaskDependenciesResult(
                            False, f"Dependency {add_id_str} not found"
                        )
                    if self.cycle_detector.detect_cycle(target_id, add_id, self.uow.tasks):
                        return ModifyTaskDependenciesResult(
                            False, f"Cycle detected when adding dependency {add_id_str}"
                        )
                    task.dependencies.add(add_id)
                
                # Recalculate status based on new dependencies
                is_blocked = self.dependency_resolver.evaluate_blocking_status(task, self.uow.tasks)
                if is_blocked:
                    if task.status == TaskStatus.READY:
                        task.mark_pending()
                else:
                    if task.status in (TaskStatus.PENDING, TaskStatus.BLOCKED):
                        task.mark_ready()

                self.uow.tasks.save(task)
                for event in task.collect_events():
                    self.uow.event_bus.publish(event)
                
                self.uow.commit()
                return ModifyTaskDependenciesResult(True)
        except Exception as e:
            return ModifyTaskDependenciesResult(False, str(e))
