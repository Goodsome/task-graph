"""Task-Graph 交互式终端界面主应用。

使用 Textual 框架构建，作为 task-graph CLI 的默认入口。
支持 Task 和 Issue 两个视图之间切换。
"""

from textual.app import App

from task_graph.planning.interfaces.tui.screens.task_list import TaskListScreen
from task_graph.planning.interfaces.tui.screens.task_detail import TaskDetailScreen
from task_graph.issue_tracking.interfaces.tui.screens.issue_list import IssueListScreen
from task_graph.issue_tracking.interfaces.tui.screens.issue_detail import IssueDetailScreen


class TaskGraphApp(App):
    """Task-Graph 交互式终端应用。"""

    TITLE = "TaskGraph"
    SUB_TITLE = "交互式任务管理"

    CSS = """
    Screen {
        background: $background;
    }
    """

    def on_mount(self) -> None:
        """启动时推入任务列表页面。"""
        self.push_screen(TaskListScreen())

    def navigate_to_task(self, task_id: str) -> None:
        """导航到任务详情页面。

        Args:
            task_id: 要查看的任务 ID
        """
        self.push_screen(TaskDetailScreen(task_id))

    def navigate_to_issue(self, issue_id: str) -> None:
        """导航到 Issue 详情页面。

        Args:
            issue_id: 要查看的 Issue ID
        """
        self.push_screen(IssueDetailScreen(issue_id))

    def switch_to_tasks(self) -> None:
        """切换到 Task 列表视图（替换当前 Screen）。"""
        self.switch_screen(TaskListScreen())

    def switch_to_issues(self) -> None:
        """切换到 Issue 列表视图（替换当前 Screen）。"""
        self.switch_screen(IssueListScreen())


def run_tui() -> None:
    """启动 TUI 应用的入口函数。"""
    app = TaskGraphApp()
    app.run()
