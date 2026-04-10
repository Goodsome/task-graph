from fastmcp import FastMCP

from task_graph.bootstrap import create_container
# 导入各个独立的文件
from task_graph.issue_tracking.interfaces.mcp.create_issue import create_issue

def create_app():
    # 1. DI 容器初始化
    _ = create_container()

    mcp = FastMCP("TaskGraph")

    # 2. 手动将函数注册为 tool
    # FastMCP 支持显式注册，这样你不需要在子文件中写 @mcp.tool
    _ = mcp.add_tool(create_issue)

    return mcp


def main():
    mcp = create_app()
    mcp.run()

if __name__ == "__main__":
    main()