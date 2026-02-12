"""
Planning MCP Server - Exposes Planning Use Cases as MCP Tools.

This module provides an MCP (Model Context Protocol) server that wraps
the Planning context's use cases, making them accessible to LLM applications.
"""

import logging

logging.basicConfig(
    filename="C:\\Users\\86188\\code\\TaskGraph\\logs\\mcp_server.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logging.info("Starting MCP Server")

from mcp.server import FastMCP
from pydantic import BaseModel, Field
from typing import Optional

from task_graph.planning.container import PlanningContainer
from task_graph.planning.application.use_cases.create_task import (
    CreateTaskCommand,
    CreateTaskResult,
)
from task_graph.planning.application.use_cases.list_tasks import (
    ListTasksQuery,
    ListTasksResult,
)
from task_graph.planning.application.use_cases.get_task_details import (
    GetTaskDetailsQuery,
    GetTaskDetailsResult,
)
from task_graph.planning.application.use_cases.modify_task_dependencies import (
    ModifyTaskDependenciesCommand,
    ModifyTaskDependenciesResult,
)
from task_graph.planning.application.use_cases.revise_task_details import (
    ReviseTaskDetailsCommand,
    ReviseTaskDetailsResult,
)
from task_graph.planning.application.use_cases.suggest_next_action import (
    SuggestNextActionQuery,
    SuggestNextActionResult,
)
from task_graph.planning.application.use_cases.update_task_status import (
    UpdateTaskStatusCommand,
    UpdateTaskStatusResult,
)
from task_graph.planning.application.use_cases.submit_task_result import (
    SubmitTaskResultCommand,
    SubmitTaskResultResult,
)
from task_graph.planning.application.use_cases.claim_task import (
    ClaimTaskCommand,
    ClaimTaskResult,
)
from task_graph.planning.application.use_cases.review_task import (
    ReviewTaskCommand,
    ReviewTaskResult,
)
from task_graph.planning.domain.enums import CompletionLogic, PlanningLevel, TaskStatus

# Initialize MCP Server
mcp = FastMCP("Planning MCP Server")

# Initialize DI Container
_container: Optional[PlanningContainer] = None


def _get_container() -> PlanningContainer:
    """Lazy initialization of the DI container."""
    global _container
    if _container is None:
        _container = PlanningContainer()
    return _container


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool()
def create_task(
    project_id: str,
    name: str,
    description: str,
    effort: int,
    base_value: float,
    planning_level: str,
    completion_logic: str = "all",
    dependencies: list[str] | None = None,
) -> dict:
    """
    创建一个新的规划任务。

    Args:
        project_id: 项目标识符 (e.g. "TaskGraph", "CodingAgent")
        name: 简短的任务名称 (e.g. "Design Auth System")
        description: 详细的任务说明，对于 atomic 任务，应包含具体文件路径。
        effort: 基于斐波那契数列的工作量估算。Allowed values: [1, 2, 3, 5, 8, 13, 21, ...].
                1-3 for atomic tasks, 5-8 for feature tasks, 8-13 for architectural tasks.
        base_value: 业务价值评分 (1.0 - 10.0)，高价值任务会被优先建议。
        planning_level: 任务层级。Allowed values: ['architectural', 'feature', 'atomic'].
                        - architectural: 高层设计与决策。
                        - feature: 接口定义与 Schema 设计。
                        - atomic: 具体代码实现。
        completion_logic: 依赖完成逻辑。'all' (默认) = 等待所有依赖完成; 'any' = 任一依赖完成即可。
        dependencies: 前置任务的 task_id 列表。当前任务会在依赖任务全部完成后自动变为 READY。
    Returns:
        包含 success, task_id, error 的结果
    """
    container = _get_container()
    use_case = container.create_task()

    try:
        level = PlanningLevel(planning_level.lower())
    except ValueError:
        return {"success": False, "task_id": "", "error": f"Invalid planning_level: {planning_level}"}

    try:
        logic = CompletionLogic(completion_logic.lower())
    except ValueError:
        return {"success": False, "task_id": "", "error": f"Invalid completion_logic: {completion_logic}"}
    
    if dependencies is None:
        dependencies = []

    cmd = CreateTaskCommand(
        project_id=project_id,
        name=name,
        description=description,
        effort=effort,
        base_value=base_value,
        planning_level=level,
        completion_logic=logic,
        dependencies=dependencies,
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "task_id": result.task_id,
        "error": result.error,
    }


@mcp.tool()
def list_tasks(
    page: int = 1,
    page_size: int = 10,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    planning_level: Optional[str] = None,
    search: Optional[str] = None,
) -> dict:
    """
    分页查询任务列表。

    Args:
        page: 页码，从1开始
        page_size: 每页数量
        project_id: 按项目标识符筛选
        status: 按任务状态筛选 (pending, blocked, ready, in_progress, review, done, skipped, discarded)
        planning_level: 按规划层级筛选 (architectural, feature, atomic)
        search: 关键字搜索（匹配任务名称或描述）

    Returns:
        包含 tasks, total_count, total_pages, current_page, error 的结果
    """
    container = _get_container()
    use_case = container.list_tasks()

    # Convert string enums to actual Enum objects
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status.lower())
        except ValueError:
            return {"error": f"Invalid status: {status}"}

    level = None
    if planning_level:
        try:
            level = PlanningLevel(planning_level.lower())
        except ValueError:
            return {"error": f"Invalid planning_level: {planning_level}"}

    query = ListTasksQuery(
        page=page,
        page_size=page_size,
        project_id=project_id,
        status=task_status,
        planning_level=level,
        search=search
    )
    result = use_case.execute(query)

    return {
        "tasks": result.tasks,
        "total_count": result.total_count,
        "total_pages": result.total_pages,
        "current_page": result.current_page,
        "error": result.error,
    }


@mcp.tool()
def get_task_details(task_id: str) -> dict:
    """
    获取任务的详细上下文。

    Args:
        task_id: 目标任务ID

    Returns:
        包含 success, task, error 的结果
    """
    container = _get_container()
    use_case = container.get_task_details()

    query = GetTaskDetailsQuery(task_id=task_id)
    result = use_case.execute(query)

    return {
        "success": result.success,
        "task": result.task,
        "error": result.error,
    }


@mcp.tool()
def modify_task_dependencies(
    task_id: str,
    added_dependencies: Optional[list[str]] = None,
    removed_dependencies: Optional[list[str]] = None,
) -> dict:
    """
    修改任务的依赖关系。

    Args:
        task_id: 目标任务ID
        added_dependencies: 要添加的依赖任务ID列表
        removed_dependencies: 要移除的依赖任务ID列表

    Returns:
        包含 success, error 的结果
    """
    container = _get_container()
    use_case = container.modify_task_dependencies()

    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id,
        added_dependencies=added_dependencies if added_dependencies else [],
        removed_dependencies=removed_dependencies if removed_dependencies else [],
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "error": result.error,
    }


@mcp.tool()
def revise_task_details(
    task_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    effort: Optional[int] = None,
    base_value: Optional[float] = None,
) -> dict:
    """
    修改任务的详细信息。

    Args:
        task_id: 目标任务ID
        name: 新的任务名称 (可选)
        description: 新的任务描述 (可选)
        effort: 新的工作量估算 (可选)
        base_value: 新的业务价值评分 (可选)

    Returns:
        包含 success, error 的结果
    """
    container = _get_container()
    use_case = container.revise_task_details()

    cmd = ReviseTaskDetailsCommand(
        task_id=task_id,
        name=name,
        description=description,
        effort=effort,
        base_value=base_value,
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "error": result.error,
    }


@mcp.tool()
def suggest_next_action(top_n: int = 3, project_id: Optional[str] = None) -> dict:
    """
    获取优先级最高的可执行任务建议。

    基于 ROI (价值/工作量) 计算优先级，可被执行的任务。

    Args:
        top_n: 返回的任务数量
        project_id: 按项目标识符筛选 (可选)

    Returns:
        包含 tasks 列表的结果，每个任务包含 id, name, description, status 等信息
    """
    container = _get_container()
    use_case = container.suggest_next_action()

    query = SuggestNextActionQuery(top_n=top_n, project_id=project_id)
    result = use_case.execute(query)

    tasks_data = []
    for task in result.tasks:
        tasks_data.append({
            "id": str(task.id),
            "name": task.name,
            "description": task.description,
            "status": task.status.value,
            "effort": task.effort.value,
            "base_value": task.base_value.value,
        })

    return {"tasks": tasks_data}


@mcp.tool()
def update_task_status(task_id: str, new_status: str) -> dict:
    """
    更新任务状态。

    当任务完成时，会自动检查并解锁依赖该任务的下游任务。

    Args:
        task_id: 目标任务ID
        new_status: 新状态 (pending, blocked, ready, in_progress, done, skipped, discarded)

    Returns:
        包含 success, affected_tasks (被解锁的任务ID列表), error 的结果
    """
    container = _get_container()
    use_case = container.update_task_status()

    cmd = UpdateTaskStatusCommand(
        task_id=task_id,
        new_status=new_status,
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "affected_tasks": result.affected_tasks,
        "error": result.error,
    }


@mcp.tool()
def submit_task_result(
    task_id: str,
    summary: str,
    artifacts: Optional[list[str]] = None,
    error: Optional[str] = None,
) -> dict:
    """
    提交任务执行结果。

    当任务执行者完成任务后，使用此工具提交执行结果，包括摘要、产出物和可选的错误信息。

    Args:
        task_id: 目标任务ID
        summary: 任务执行摘要，简述完成的工作内容
        artifacts: 产出物列表（文件路径或 Blueprint 路径）
        error: 可选的错误信息（如果任务执行失败）

    Returns:
        包含 success, error 的结果
    """
    container = _get_container()
    use_case = container.submit_task_result()

    cmd = SubmitTaskResultCommand(
        task_id=task_id,
        summary=summary,
        artifacts=artifacts if artifacts else [],
        error=error,
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "error": result.error,
    }


@mcp.tool()
def claim_task(
    task_id: str,
    executor_id: Optional[str] = None,
) -> dict:
    """
    领取一个处于 READY 状态的任务。

    将任务状态从 READY 原子性地（在业务逻辑层）变更为 IN_PROGRESS。

    Args:
        task_id: 目标任务ID
        executor_id: 可选：执行者标识（用于审计和追踪）

    Returns:
        包含 success, task_id, error, error_code 的结果
    """
    container = _get_container()
    use_case = container.claim_task()

    cmd = ClaimTaskCommand(
        task_id=task_id,
        executor_id=executor_id if executor_id else "",
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "task_id": result.task_id,
        "error": result.error,
        "error_code": result.error_code,
    }


@mcp.tool()
def review_task(
    task_id: str,
    approved: bool,
    feedback: str,
) -> dict:
    """
    审查任务并提供反馈。

    当任务处于 REVIEW 状态时，规划者使用此工具进行验收。
    如果 approved=True，任务将变为 DONE，并解锁后续任务。
    如果 approved=False，任务将变为 REJECTED。

    Args:
        task_id: 目标任务ID
        approved: 是否通过验收
        feedback: 详细的反馈意见

    Returns:
        包含 success, affected_tasks, error 的结果
    """
    container = _get_container()
    use_case = container.review_task()

    cmd = ReviewTaskCommand(
        task_id=task_id,
        approved=approved,
        feedback=feedback,
    )

    result = use_case.execute(cmd)
    return {
        "success": result.success,
        "affected_tasks": result.affected_tasks,
        "error": result.error,
    }


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """MCP Server entry point for standalone execution."""
    
    # Initialize database if configured
    container = _get_container()
    if hasattr(container, 'database'):
        try:
            # Check if database is actually instantiated (it's a singleton)
            # Accessing container.database() will create it if not created
            db = container.database()
            db.init_db()
        except Exception as e:
            # Log error but allow server to start? Or fail fast?
            # For now, we log and proceed, but in production, we might want to fail.
            # However, if config is missing, 'database' attribute won't exist.
            logging.error(f"Failed to initialize database: {e}")

    mcp.run()


if __name__ == "__main__":
    main()
