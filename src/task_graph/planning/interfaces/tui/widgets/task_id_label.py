"""可点击的 TaskID 标签组件。

点击后发送 NavigateToTask 消息，由上层处理页面跳转。
"""

from textual.message import Message
from textual.widgets import Static
from task_graph.planning.interfaces.tui.theme import short_id


class TaskIdLabel(Static):
    """可点击的 Task ID 标签，支持短 ID 展示与点击跳转。"""

    class NavigateToTask(Message):
        """请求跳转到任务详情的消息。"""

        def __init__(self, task_id: str) -> None:
            self.task_id = task_id
            super().__init__()

    DEFAULT_CSS = """
    TaskIdLabel {
        color: $accent;
        text-style: underline;
        width: auto;
        min-width: 10;
    }
    TaskIdLabel:hover {
        color: $accent-lighten-2;
        text-style: bold underline;
    }
    """

    def __init__(
        self,
        task_id: str,
        *,
        show_short: bool = True,
        **kwargs,
    ) -> None:
        self._task_id = task_id
        display_text = short_id(task_id) if show_short else task_id
        super().__init__(display_text, **kwargs)
        self.tooltip = task_id  # 悬停显示完整 ID

    def on_click(self) -> None:
        """点击时发送跳转消息。"""
        self.post_message(self.NavigateToTask(self._task_id))
