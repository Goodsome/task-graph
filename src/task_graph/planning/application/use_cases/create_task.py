from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field

from task_graph.planning.domain.aggregates import Task
from task_graph.planning.domain.enums import CompletionLogic, TaskStatus, ScopeLevel
from task_graph.planning.application.unit_of_work import UnitOfWork
from task_graph.planning.domain.value_objects import StoryPoint, ValueScore, TaskId

import logging

logger = logging.getLogger(__name__)

class CreateTaskCommand(BaseModel):
    """
    创建一个新的规划任务。
    用于 Agent (Planner) 将用户需求转化为具体的执行单元。
    """

    project_id: str
    name: str
    description: str
    effort: int
    base_value: float
    scope_level: ScopeLevel
    completion_logic: CompletionLogic = Field(default=CompletionLogic.ALL)
    dependencies: list[str] = Field(default_factory=list)
    parent_id: Optional[str] = Field(default=None)


@dataclass
class CreateTaskResult:

    success: bool
    task_id: str
    error: str


@dataclass
class CreateTask:
    """Create task"""

    uow: UnitOfWork

    def execute(self, cmd: CreateTaskCommand) -> CreateTaskResult:
        try:
            with self.uow:
                # 1. 转换 VOs
                effort_vo = StoryPoint.create(cmd.effort)
                value_vo = ValueScore.create(cmd.base_value)

                # 2. 处理依赖 (Primitives -> TaskId Set)
                dep_ids = set()
                existing_deps = []
                if cmd.dependencies:
                    for d_str in cmd.dependencies:
                        dep_ids.add(TaskId.model_validate(d_str))

                    # 3. 校验依赖是否存在
                    existing_deps = self.uow.tasks.find_by_ids(dep_ids)
                    found_ids = {t.id for t in existing_deps}

                    missing_ids = dep_ids - found_ids
                    if missing_ids:
                        missing_str = ", ".join([str(mid.value) for mid in missing_ids])
                        return CreateTaskResult(False, "", f"Dependencies not found: {missing_str}")

                # 4. 计算是否需要标记为 READY
                should_be_ready = True
                if dep_ids and not all(t.status == TaskStatus.DONE for t in existing_deps):
                    should_be_ready = False
                
                parent_id = None
                if cmd.parent_id:
                    parent_id = TaskId.reconstitute(cmd.parent_id)

                # 5. 创建实体 (默认状态 PENDING)
                new_task = Task.create(
                    project_id=cmd.project_id,
                    name=cmd.name,
                    description=cmd.description,
                    effort=effort_vo,
                    base_value=value_vo,
                    completion_logic=cmd.completion_logic,
                    dependencies=dep_ids,
                    scope_level=cmd.scope_level,
                    parent_id=parent_id,
                )

                # 如果条件满足，则标记为 READY（此方法会添加 TaskReadyEvent 到聚合根）
                if should_be_ready:
                    new_task.mark_ready()
                    logger.info(f"Task {new_task.id} marked as READY (dependencies satisfied or no dependencies)")

                # 6. 持久化
                self.uow.tasks.save(new_task)
                logger.info(f"Task {new_task.id} created with status {new_task.status.value}")

                events = new_task.collect_events()
                logger.debug(f"Collected {len(events)} events from aggregate")
                for event in events:
                    self.uow.event_bus.publish(event)

                self.uow.commit()

                return CreateTaskResult(True, str(new_task.id), error="")

        except Exception as e:
            logger.error(e)
            import traceback
            logger.error(traceback.format_exc())
            return CreateTaskResult(False, "", str(e))
