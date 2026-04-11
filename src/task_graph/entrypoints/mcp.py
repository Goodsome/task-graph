import logging
from fastmcp import FastMCP

from task_graph.bootstrap import create_container, setup_mcp_logging
# 导入issue_tracking的MCP工具
from task_graph.issue_tracking.interfaces.mcp.create_issue import create_issue
from task_graph.issue_tracking.interfaces.mcp.list_issues import list_issues
from task_graph.issue_tracking.interfaces.mcp.add_comment import add_comment
from task_graph.issue_tracking.interfaces.mcp.close_issue import close_issue
from task_graph.issue_tracking.interfaces.mcp.get_issue_details import get_issue_details
from task_graph.issue_tracking.interfaces.mcp.link_issue_to_task import link_issue_to_task
from task_graph.issue_tracking.interfaces.mcp.unlink_issue_from_task import unlink_issue_from_task
from task_graph.issue_tracking.interfaces.mcp.update_issue_metadata import update_issue_metadata
from task_graph.issue_tracking.interfaces.mcp.update_issue_status import update_issue_status

# 导入planning的MCP工具
from task_graph.planning.interfaces.mcp.create_task import create_task
from task_graph.planning.interfaces.mcp.list_tasks import list_tasks
from task_graph.planning.interfaces.mcp.claim_task import claim_task
from task_graph.planning.interfaces.mcp.update_task_status import update_task_status
from task_graph.planning.interfaces.mcp.delete_task import delete_task
from task_graph.planning.interfaces.mcp.get_task_details import get_task_details
from task_graph.planning.interfaces.mcp.modify_task_dependencies import modify_task_dependencies
from task_graph.planning.interfaces.mcp.review_task import review_task
from task_graph.planning.interfaces.mcp.submit_task_result import submit_task_result
from task_graph.planning.interfaces.mcp.suggest_next_action import suggest_next_action

def create_app():
    # 初始化日志
    logger = setup_mcp_logging()
    logger.info("Initializing TaskGraph MCP server")

    # 1. DI 容器初始化
    logger.info("Initializing DI container")
    _ = create_container()

    mcp = FastMCP("TaskGraph")

    # 2. 手动将函数注册为 tool
    # FastMCP 支持显式注册，这样你不需要在子文件中写 @mcp.tool
    # 注册issue_tracking工具
    _ = mcp.add_tool(create_issue)
    _ = mcp.add_tool(list_issues)
    _ = mcp.add_tool(add_comment)
    _ = mcp.add_tool(close_issue)
    _ = mcp.add_tool(get_issue_details)
    _ = mcp.add_tool(link_issue_to_task)
    _ = mcp.add_tool(unlink_issue_from_task)
    _ = mcp.add_tool(update_issue_metadata)
    _ = mcp.add_tool(update_issue_status)

    # 注册planning工具
    _ = mcp.add_tool(create_task)
    _ = mcp.add_tool(list_tasks)
    _ = mcp.add_tool(claim_task)
    _ = mcp.add_tool(update_task_status)
    _ = mcp.add_tool(delete_task)
    _ = mcp.add_tool(get_task_details)
    _ = mcp.add_tool(modify_task_dependencies)
    _ = mcp.add_tool(review_task)
    _ = mcp.add_tool(submit_task_result)
    _ = mcp.add_tool(suggest_next_action)

    logger.info("MCP server initialized successfully")
    return mcp


def main():
    logger = logging.getLogger("task_graph.mcp")
    try:
        mcp = create_app()
        logger.info("Starting MCP server")
        mcp.run()
    except Exception as e:
        logger.error(f"MCP server failed to start: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("MCP server stopped")

if __name__ == "__main__":
    main()