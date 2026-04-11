import logging
from fastmcp import FastMCP

from task_graph.bootstrap import create_container, setup_mcp_logging
# 导入各个独立的文件
from task_graph.issue_tracking.interfaces.mcp.create_issue import create_issue

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
    logger.info("Registering MCP tools: create_issue")
    _ = mcp.add_tool(create_issue)

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