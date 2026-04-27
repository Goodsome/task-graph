"""Task-Graph 交互式终端界面主应用。

使用 Textual 框架构建，作为 task-graph CLI 的默认入口。
"""

from textual.app import App

from task_graph.planning.interfaces.tui.screens.task_list import TaskListScreen
from task_graph.planning.interfaces.tui.screens.task_detail import TaskDetailScreen


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


def run_tui() -> None:
    """启动 TUI 应用的入口函数。"""
    app = TaskGraphApp()
    app.run()
