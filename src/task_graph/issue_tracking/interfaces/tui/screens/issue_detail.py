"""Issue 详情页面。

展示单个 Issue 的完整信息，包括评论、标签和关联 Task。
"""

from textual import on, work
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Static,
    Button,
    Rule,
)
from dependency_injector.wiring import Provide, inject

from task_graph.issue_tracking.application.use_cases.get_issue_details import (
    GetIssueDetails,
    GetIssueDetailsQuery,
    GetIssueDetailsResult,
    IssueDetailsDTO,
)
from task_graph.issue_tracking.application.use_cases.close_issue import (
    CloseIssue,
    CloseIssueCommand,
    CloseIssueResult,
)
from task_graph.issue_tracking.interfaces.tui.theme import (
    ISSUE_STATUS_COLORS,
    SEVERITY_COLORS,
    ISSUE_TYPE_COLORS,
)
from task_graph.planning.interfaces.tui.widgets.task_id_label import TaskIdLabel
from task_graph.planning.interfaces.tui.screens.confirm_dialog import ConfirmDialog


class IssueDetailScreen(Screen):
    """Issue 详情页面。"""

    BINDINGS = [
        ("escape", "go_back", "返回列表"),
        ("c", "close_issue", "关闭 Issue"),
        ("q", "quit", "退出"),
    ]

    DEFAULT_CSS = """
    IssueDetailScreen {
        layout: vertical;
    }

    #issue-detail-header {
        height: auto;
        padding: 1 2;
        background: $surface;
        dock: top;
        layout: horizontal;
    }

    #issue-btn-back {
        min-width: 14;
    }

    #issue-btn-close {
        min-width: 14;
        margin-left: 1;
    }

    #issue-detail-scroll {
        height: 1fr;
        padding: 1 2;
    }

    .issue-section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
    }

    .issue-field-row {
        height: auto;
        margin-bottom: 0;
    }

    .issue-field-label {
        width: 14;
        color: $text-muted;
        text-style: bold;
    }

    .issue-field-value {
        width: 1fr;
    }

    .issue-comment-block {
        margin-left: 2;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
    }

    .issue-comment-header {
        text-style: bold;
        color: $accent;
    }

    .issue-comment-body {
        margin-left: 2;
    }

    .issue-label-tag {
        width: auto;
        margin-right: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
    }

    .issue-labels-row {
        height: auto;
        layout: horizontal;
    }

    .issue-task-links-row {
        height: auto;
        layout: horizontal;
    }

    .issue-task-links-row TaskIdLabel {
        margin-right: 1;
    }

    #issue-detail-loading {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
        text-style: dim italic;
    }
    """

    def __init__(self, issue_id: str) -> None:
        super().__init__()
        self._issue_id = issue_id
        self._issue_detail: IssueDetailsDTO | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="issue-detail-header"):
            yield Button("◀ 返回列表", id="issue-btn-back", variant="default")
            yield Button("🔒 关闭 Issue", id="issue-btn-close", variant="error")
        yield Static("正在加载 Issue 详情...", id="issue-detail-loading")
        yield Footer()

    def on_mount(self) -> None:
        self._load_issue()

    @on(Button.Pressed, "#issue-btn-back")
    def _on_back(self) -> None:
        self.action_go_back()

    @on(Button.Pressed, "#issue-btn-close")
    def _on_close_pressed(self) -> None:
        self.action_close_issue()

    @on(TaskIdLabel.NavigateToTask)
    def _on_navigate_to_task(self, event: TaskIdLabel.NavigateToTask) -> None:
        """处理可点击 Task ID 的跳转请求。"""
        self.app.navigate_to_task(event.task_id)

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_close_issue(self) -> None:
        """关闭当前 Issue。"""
        if self._issue_detail and self._issue_detail.status.value == "closed":
            self.notify("该 Issue 已经是关闭状态", severity="warning")
            return

        def check_confirm(confirmed: bool) -> None:
            if confirmed:
                self._close_issue()

        self.app.push_screen(
            ConfirmDialog("确定要关闭这个 Issue 吗？"),
            check_confirm,
        )

    def action_quit(self) -> None:
        self.app.exit()

    @work(thread=True)
    @inject
    def _close_issue(
        self, use_case: CloseIssue = Provide["issue_tracking.close_issue"]
    ) -> None:
        """执行关闭 Issue 的 Use Case。"""
        cmd = CloseIssueCommand(issue_id=self._issue_id)
        result: CloseIssueResult = use_case.execute(cmd)

        if result.success:
            self.app.call_from_thread(self.notify, "Issue 已成功关闭", severity="information")
            self.app.call_from_thread(self.action_go_back)
        else:
            self.app.call_from_thread(
                self.notify, f"关闭失败: {result.error}", severity="error"
            )

    @work(thread=True)
    @inject
    def _load_issue(
        self, use_case: GetIssueDetails = Provide["issue_tracking.get_issue_details"]
    ) -> None:
        query = GetIssueDetailsQuery(issue_id=self._issue_id)
        result: GetIssueDetailsResult = use_case.execute(query)
        self.app.call_from_thread(self._render_issue, result)

    def _render_issue(self, result: GetIssueDetailsResult) -> None:
        """将 Issue 数据渲染到页面。"""
        # 移除 loading
        loading = self.query_one("#issue-detail-loading", Static)
        loading.remove()

        if not result.success or result.issue is None:
            error_msg = result.error or "未知错误"
            self.mount(
                Static(f"[red bold]加载失败:[/] {error_msg}", id="issue-detail-error"),
                after=self.query_one("#issue-detail-header"),
            )
            return

        issue = result.issue
        self._issue_detail = issue

        # 构建详情内容
        scroll = VerticalScroll(id="issue-detail-scroll")
        self.mount(scroll, after=self.query_one("#issue-detail-header"))

        # --- 基本信息 ---
        scroll.mount(Static("📋 基本信息", classes="issue-section-title"))
        scroll.mount(Rule())
        self._add_field(scroll, "ID", issue.id)
        self._add_field(scroll, "项目", issue.project_id)
        self._add_field(scroll, "标题", issue.title)

        # 类型（带颜色）
        type_color = ISSUE_TYPE_COLORS.get(issue.type.value, "white")
        self._add_field(
            scroll,
            "类型",
            f"[{type_color}]{issue.type.value}[/{type_color}]",
        )

        # 严重度（带颜色）
        severity_color = SEVERITY_COLORS.get(issue.severity.value, "white")
        self._add_field(
            scroll,
            "严重度",
            f"[{severity_color}]{issue.severity.value}[/{severity_color}]",
        )

        # 状态（带颜色）
        status_color = ISSUE_STATUS_COLORS.get(issue.status.value, "white")
        self._add_field(
            scroll,
            "状态",
            f"[{status_color}]{issue.status.value}[/{status_color}]",
        )

        self._add_field(scroll, "提交者", issue.submitter.name)
        self._add_field(scroll, "创建时间", issue.created_at.strftime("%Y-%m-%d %H:%M"))
        self._add_field(scroll, "更新时间", issue.updated_at.strftime("%Y-%m-%d %H:%M"))

        # --- 描述 ---
        scroll.mount(Static(""))
        scroll.mount(Static("📝 描述", classes="issue-section-title"))
        scroll.mount(Rule())
        scroll.mount(Static(issue.description))

        # --- 标签 ---
        if issue.labels:
            scroll.mount(Static(""))
            scroll.mount(Static("🏷️ 标签", classes="issue-section-title"))
            scroll.mount(Rule())
            labels_row = Horizontal(classes="issue-labels-row")
            scroll.mount(labels_row)
            for label in issue.labels:
                labels_row.mount(Static(f" {label.name} ", classes="issue-label-tag"))

        # --- 关联 Task ---
        if issue.task_links:
            scroll.mount(Static(""))
            scroll.mount(Static("🔗 关联 Task", classes="issue-section-title"))
            scroll.mount(Rule())
            links_row = Horizontal(classes="issue-task-links-row")
            scroll.mount(links_row)
            for link in issue.task_links:
                links_row.mount(TaskIdLabel(link.task_id, show_short=False))

        # --- 评论 ---
        if issue.comments:
            scroll.mount(Static(""))
            scroll.mount(Static(f"💬 评论 ({len(issue.comments)})", classes="issue-section-title"))
            scroll.mount(Rule())
            for comment in issue.comments:
                time_str = comment.created_at.strftime("%Y-%m-%d %H:%M")
                scroll.mount(
                    Static(
                        f"  [bold]{comment.author}[/bold] · [dim]{time_str}[/dim]",
                        classes="issue-comment-header",
                    )
                )
                scroll.mount(
                    Static(f"    {comment.content}", classes="issue-comment-body")
                )
                scroll.mount(Static(""))

    @staticmethod
    def _add_field(
        container: VerticalScroll, label: str, value: str
    ) -> None:
        """添加一个字段行（标签 + 值）。"""
        row = Horizontal(classes="issue-field-row")
        container.mount(row)
        row.mount(Static(label, classes="issue-field-label"))
        row.mount(Static(value, classes="issue-field-value"))
