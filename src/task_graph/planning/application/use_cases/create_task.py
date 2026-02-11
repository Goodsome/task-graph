from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from task_graph.planning.domain.aggregates import Task
from task_graph.planning.domain.enums import CompletionLogic, PlanningLevel, TaskStatus
from task_graph.planning.domain.ports.task_repository import TaskRepository
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
    planning_level: PlanningLevel
    completion_logic: CompletionLogic = Field(default=CompletionLogic.ALL)
    dependencies: list[str] = Field(default_factory=list)


@dataclass
class CreateTaskResult:

    success: bool
    task_id: str
    error: str


@dataclass
class CreateTask:
    """Create task"""

    repository: TaskRepository

    def execute(self, cmd: CreateTaskCommand) -> CreateTaskResult:
        try:
            # 1. 转换 VOs
            effort_vo = StoryPoint.create(cmd.effort)
            value_vo = ValueScore.create(cmd.base_value)

            logic_enum = cmd.completion_logic

            # 2. 处理依赖 (Primitives -> TaskId Set)
            dep_ids = set()
            existing_deps = []
            if cmd.dependencies:
                for d_str in cmd.dependencies:
                    dep_ids.add(TaskId.reconstitute(d_str))

                # 3. 校验依赖是否存在
                existing_deps = self.repository.find_by_ids(dep_ids)
                found_ids = {t.id for t in existing_deps}

                missing_ids = dep_ids - found_ids
                if missing_ids:
                    missing_str = ", ".join([str(mid.value) for mid in missing_ids])
                    return CreateTaskResult(False, "", f"Dependencies not found: {missing_str}")

            # 4. 计算初始状态
            initial_status = None
            if dep_ids:
                if logic_enum == CompletionLogic.ALL:
                    if all(t.status == TaskStatus.DONE for t in existing_deps):
                        initial_status = TaskStatus.READY
                elif logic_enum == CompletionLogic.ANY:
                    if any(t.status == TaskStatus.DONE for t in existing_deps):
                        initial_status = TaskStatus.READY
            else:
                initial_status = TaskStatus.READY

            # 5. 创建实体
            new_task = Task.create(
                project_id=cmd.project_id,
                name=cmd.name,
                description=cmd.description,
                effort=effort_vo,
                base_value=value_vo,
                completion_logic=logic_enum,
                dependencies=dep_ids,
                planning_level=cmd.planning_level,
                status=initial_status,
            )

            # 6. 持久化
            self.repository.save(new_task)

            return CreateTaskResult(True, str(new_task.id), error="")

        except Exception as e:
            logger.error(e)
            import traceback
            logger.error(traceback.format_exc())
            return CreateTaskResult(False, "", str(e))
