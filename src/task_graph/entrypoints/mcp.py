import logging
from fastmcp import FastMCP

from task_graph.bootstrap import create_container, setup_mcp_logging
# 导入各模块统一暴露的工具列表
from task_graph.issue_tracking.interfaces.mcp import ISSUE_TOOLS
from task_graph.planning.interfaces.mcp import PLANNING_TOOLS

def create_app():
    # 初始化日志
    logger = setup_mcp_logging()
    logger.info("Initializing TaskGraph MCP server")

    # 1. DI 容器初始化
    logger.info("Initializing DI container")

    mcp = FastMCP("TaskGraph")

    # 2. 手动将函数注册为 tool
    # FastMCP 支持显式注册，这样你不需要在子文件中写 @mcp.tool
    # 注册issue_tracking工具
    for tool in ISSUE_TOOLS:
        _ = mcp.add_tool(tool)

    # 注册planning工具
    for tool in PLANNING_TOOLS:
        _ = mcp.add_tool(tool)

    logger.info(f"Registered {len(ISSUE_TOOLS)} issue tracking tools, {len(PLANNING_TOOLS)} planning tools, total {len(ISSUE_TOOLS) + len(PLANNING_TOOLS)} tools")

    logger.info("MCP server initialized successfully")
    return mcp


def main():
    logger = logging.getLogger("task_graph.mcp")
    container = None
    try:
        container = create_container()
        mcp = create_app()
        logger.info("Starting MCP server")
        mcp.run()
    except Exception as e:
        logger.error(f"MCP server failed to start: {str(e)}", exc_info=True)
        raise
    finally:
        if container is not None:
            container.shutdown()
        logger.info("MCP server stopped")

if __name__ == "__main__":
    main()