"""Issue 列表页面。

展示分页 Issue 列表，支持按项目 ID、状态、类型、严重度过滤。
"""

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Button,
)
from rich.text import Text
from dependency_injector.wiring import Provide, inject

from task_graph.issue_tracking.application.use_cases.list_issues import (
    ListIssues,
    ListIssuesQuery,
    ListIssuesResult,
    IssueSummaryDTO,
)
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.issue_tracking.interfaces.tui.theme import (
    ISSUE_STATUS_COLORS,
    SEVERITY_COLORS,
    ISSUE_TYPE_COLORS,
    short_id,
)


# --- 过滤器选项 ---
_STATUS_OPTIONS: list[tuple[str, str]] = [
    (s.value, s.value) for s in IssueStatus
]

_TYPE_OPTIONS: list[tuple[str, str]] = [
    (t.value, t.value) for t in IssueType
]

_SEVERITY_OPTIONS: list[tuple[str, str]] = [
    (s.value, s.value) for s in Severity
]


class IssueListScreen(Screen):
    """Issue 列表主页面。"""

    BINDINGS = [
        ("q", "quit", "退出"),
        ("r", "refresh", "刷新"),
        ("slash", "focus_filter", "过滤"),
        ("t", "switch_tasks", "Tasks"),
    ]

    DEFAULT_CSS = """
    IssueListScreen {
        layout: vertical;
    }

    #issue-filter-bar {
        height: auto;
        padding: 1 2;
        background: $surface;
        dock: top;
    }

    #issue-filter-row {
        height: 3;
        width: 1fr;
    }

    #issue-filter-project {
        width: 28;
        margin-right: 1;
    }

    #issue-filter-status {
        width: 20;
        margin-right: 1;
    }

    #issue-filter-type {
        width: 20;
        margin-right: 1;
    }

    #issue-filter-severity {
        width: 20;
        margin-right: 1;
    }

    #issue-btn-refresh {
        width: 10;
        min-width: 10;
    }

    #issue-table {
        height: 1fr;
    }

    #issue-pagination-bar {
        height: 3;
        padding: 0 2;
        background: $surface;
        dock: bottom;
        layout: horizontal;
        align: center middle;
    }

    #issue-pagination-bar Label {
        margin: 0 2;
        width: auto;
    }

    #issue-pagination-bar Button {
        min-width: 10;
    }

    #issue-status-bar {
        height: 1;
        dock: bottom;
        background: $primary-background;
        color: $text-muted;
        padding: 0 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._current_page = 1
        self._page_size = 20
        self._total_pages = 1
        self._total_count = 0
        self._filter_project: str | None = None
        self._filter_status: IssueStatus | None = None
        self._filter_type: IssueType | None = None
        self._filter_severity: Severity | None = None
        self._issues: list[IssueSummaryDTO] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="issue-filter-bar"):
            with Horizontal(id="issue-filter-row"):
                yield Input(
                    placeholder="项目ID 过滤...",
                    id="issue-filter-project",
                )
                yield Select(
                    _STATUS_OPTIONS,
                    prompt="全部状态",
                    id="issue-filter-status",
                    allow_blank=True,
                )
                yield Select(
                    _TYPE_OPTIONS,
                    prompt="全部类型",
                    id="issue-filter-type",
                    allow_blank=True,
                )
                yield Select(
                    _SEVERITY_OPTIONS,
                    prompt="全部严重度",
                    id="issue-filter-severity",
                    allow_blank=True,
                )
                yield Button("刷新", id="issue-btn-refresh", variant="primary")

        yield DataTable(id="issue-table", cursor_type="row", zebra_stripes=True)

        with Horizontal(id="issue-pagination-bar"):
            yield Button("◀ 上一页", id="issue-btn-prev", variant="default")
            yield Label("", id="issue-page-info")
            yield Button("下一页 ▶", id="issue-btn-next", variant="default")

        yield Footer()

    def on_mount(self) -> None:
        """页面加载时初始化表格列和数据。"""
        table = self.query_one("#issue-table", DataTable)
        table.add_column("ID", width=10, key="id")
        table.add_column("项目", width=12, key="project")
        table.add_column("标题", key="title")  # 自动占满剩余宽度
        table.add_column("类型", width=14, key="type")
        table.add_column("严重度", width=12, key="severity")
        table.add_column("状态", width=14, key="status")
        table.add_column("提交者", width=12, key="submitter")
        table.add_column("评论", width=6, key="comments")
        table.add_column("关联", width=6, key="links")
        table.focus()
        self._load_data()

    def on_screen_resume(self) -> None:
        """当从详情页返回此页面时，自动刷新数据。"""
        self._load_data()

    # --- 过滤器事件 ---

    @on(Input.Changed, "#issue-filter-project")
    def _on_project_filter_changed(self, event: Input.Changed) -> None:
        self._filter_project = event.value.strip() or None
        self._current_page = 1
        self._load_data()

    @on(Select.Changed, "#issue-filter-status")
    def _on_status_filter_changed(self, event: Select.Changed) -> None:
        value = event.value
        self._filter_status = (
            IssueStatus(value)
            if value not in (Select.BLANK, Select.NULL)
            else None
        )
        self._current_page = 1
        self._load_data()

    @on(Select.Changed, "#issue-filter-type")
    def _on_type_filter_changed(self, event: Select.Changed) -> None:
        value = event.value
        self._filter_type = (
            IssueType(value)
            if value not in (Select.BLANK, Select.NULL)
            else None
        )
        self._current_page = 1
        self._load_data()

    @on(Select.Changed, "#issue-filter-severity")
    def _on_severity_filter_changed(self, event: Select.Changed) -> None:
        value = event.value
        self._filter_severity = (
            Severity(value)
            if value not in (Select.BLANK, Select.NULL)
            else None
        )
        self._current_page = 1
        self._load_data()

    # --- 分页事件 ---

    @on(Button.Pressed, "#issue-btn-prev")
    def _on_prev_page(self) -> None:
        if self._current_page > 1:
            self._current_page -= 1
            self._load_data()

    @on(Button.Pressed, "#issue-btn-next")
    def _on_next_page(self) -> None:
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._load_data()

    @on(Button.Pressed, "#issue-btn-refresh")
    def _on_refresh_button(self) -> None:
        self._load_data()

    # --- 表格行选中 ---

    @on(DataTable.RowSelected)
    def _on_row_selected(self, event: DataTable.RowSelected) -> None:
        """行被选中（Enter 或双击）时跳转到 Issue 详情。"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self._issues):
            issue = self._issues[row_index]
            self.app.navigate_to_issue(issue.id)

    # --- 快捷键 ---

    def action_refresh(self) -> None:
        self._load_data()

    def action_focus_filter(self) -> None:
        self.query_one("#issue-filter-project", Input).focus()

    def action_quit(self) -> None:
        self.app.exit()

    def action_switch_tasks(self) -> None:
        self.app.switch_to_tasks()

    # --- 数据加载 ---

    @work(thread=True)
    @inject
    def _load_data(
        self, use_case: ListIssues = Provide["issue_tracking.list_issues"]
    ) -> None:
        """从 use case 加载 Issue 数据（在工作线程中执行同步 DB 操作）。"""
        offset = (self._current_page - 1) * self._page_size
        query = ListIssuesQuery(
            project_id=self._filter_project,
            status=self._filter_status,
            type=self._filter_type,
            severity=self._filter_severity,
            limit=self._page_size,
            offset=offset,
        )
        result: ListIssuesResult = use_case.execute(query)

        # 切回主线程更新 UI
        self.app.call_from_thread(self._apply_result, result)

    def _apply_result(self, result: ListIssuesResult) -> None:
        """将查询结果应用到表格（必须在主线程调用）。"""
        if result.error:
            self.notify(f"加载失败: {result.error}", severity="error")
            return

        self._issues = result.issues
        self._total_count = result.total_count

        # 计算分页
        self._total_pages = max(
            1,
            (self._total_count + self._page_size - 1) // self._page_size,
        )
        if self._current_page > self._total_pages:
            self._current_page = self._total_pages

        # 刷新表格
        table = self.query_one("#issue-table", DataTable)
        table.clear()

        for issue in self._issues:
            status_color = ISSUE_STATUS_COLORS.get(issue.status.value, "white")
            type_color = ISSUE_TYPE_COLORS.get(issue.type.value, "white")
            severity_color = SEVERITY_COLORS.get(issue.severity.value, "white")

            table.add_row(
                short_id(issue.id),
                Text(issue.project_id),
                Text(issue.title),
                Text(issue.type.value, style=type_color),
                Text(issue.severity.value, style=severity_color),
                Text(issue.status.value, style=status_color),
                Text(issue.submitter_name),
                str(issue.comment_count),
                str(issue.task_link_count),
                key=issue.id,
            )

        # 更新分页信息
        page_label = self.query_one("#issue-page-info", Label)
        page_label.update(
            f"第 {self._current_page}/{self._total_pages} 页 · 共 {self._total_count} 条"
        )

        # 更新分页按钮状态
        self.query_one("#issue-btn-prev", Button).disabled = self._current_page <= 1
        self.query_one("#issue-btn-next", Button).disabled = (
            self._current_page >= self._total_pages
        )
