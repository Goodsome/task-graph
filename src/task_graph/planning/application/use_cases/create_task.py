from dataclasses import dataclass
from task_graph.planning.domain.aggregates import Task
from task_graph.planning.domain.enums import TaskStatus
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects import (
    ScopeContext,
    StoryPoint,
    TaskId,
    ValueScore,
)
import logging
from typing import Self
from task_graph.planning.application.dtos.create_task_result import CreateTaskResult
from task_graph.planning.application.dtos.create_task_command import CreateTaskCommand

logger = logging.getLogger(__name__)


@dataclass
class CreateTask:
    """Create task"""

    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, cmd: CreateTaskCommand) -> CreateTaskResult:
        try:
            with self.uow:
                effort_vo = StoryPoint.create(cmd.effort)
                value_vo = ValueScore.create(cmd.base_value)
                dep_ids: set[TaskId] = set()
                existing_deps = []
                if cmd.dependencies:
                    for d_str in cmd.dependencies:
                        dep_ids.add(TaskId.model_validate(d_str))
                    existing_deps = self.uow.repository.find_by_ids(dep_ids)
                    found_ids = {t.id for t in existing_deps}
                    missing_ids = dep_ids - found_ids
                    if missing_ids:
                        missing_str = ", ".join([str(mid.value) for mid in missing_ids])
                        return CreateTaskResult(
                            success=False, 
                            task_id="", 
                            error=f"Dependencies not found: {missing_str}",
                        )
                should_be_ready = True
                if dep_ids and (
                    not all((t.status == TaskStatus.DONE for t in existing_deps))
                ):
                    should_be_ready = False
                parent_id = None
                if cmd.parent_id:
                    parent_id = TaskId.reconstitute(cmd.parent_id)
                scope_context = None
                if (
                    cmd.bounded_context is not None
                    or cmd.architecture_layer is not None
                    or cmd.component_name is not None
                ):
                    scope_context = ScopeContext.create(
                        bounded_context=cmd.bounded_context,
                        architecture_layer=cmd.architecture_layer,
                        component_name=cmd.component_name,
                    )
                new_task = Task.create(
                    project_id=cmd.project_id,
                    name=cmd.name,
                    description=cmd.description,
                    effort=effort_vo,
                    base_value=value_vo,
                    dependencies=dep_ids,
                    scope_level=cmd.scope_level,
                    parent_id=parent_id,
                    scope_context=scope_context,
                    acceptance_criteria=cmd.acceptance_criteria,
                )
                if should_be_ready:
                    new_task.mark_ready()
                    logger.info(
                        f"Task {new_task.id} marked as READY (dependencies satisfied or no dependencies)"
                    )
                self.uow.repository.add(new_task)
                logger.info(
                    f"Task {new_task.id} created with status {new_task.status.value}"
                )
                self.uow.commit()
                return CreateTaskResult(
                    success=True, 
                    task_id=str(new_task.id), 
                    error=""
                )
        except Exception as e:
            logger.error(e)
            import traceback

            logger.error(traceback.format_exc())
            return CreateTaskResult(
                success=False, 
                task_id="", 
                error=str(e)
            )
