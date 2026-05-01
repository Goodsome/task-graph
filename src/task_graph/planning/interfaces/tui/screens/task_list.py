"""任务列表页面。

展示分页任务列表，支持按项目ID、状态、层级过滤。
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
    Static,
    Button,
)
from rich.text import Text
from dependency_injector.wiring import Provide, inject

from task_graph.planning.application.dtos.summary_task import SummaryTaskDto
from task_graph.planning.application.use_cases.list_tasks import (
    ListTasks,
    ListTasksQuery,
    ListTasksResult,
)
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel
from task_graph.planning.interfaces.tui.theme import (
    STATUS_COLORS,
    SCOPE_COLORS,
    short_id,
)


# --- 过滤器选项 ---
_STATUS_OPTIONS: list[tuple[str, str]] = [
    (s.value, s.value) for s in TaskStatus
]

_SCOPE_OPTIONS: list[tuple[str, str]] = [
    (s.value, s.value) for s in ScopeLevel
]


class TaskListScreen(Screen):
    """任务列表主页面。"""

    BINDINGS = [
        ("q", "quit", "退出"),
        ("r", "refresh", "刷新"),
        ("slash", "focus_filter", "过滤"),
    ]

    DEFAULT_CSS = """
    TaskListScreen {
        layout: vertical;
    }

    #filter-bar {
        height: auto;
        padding: 1 2;
        background: $surface;
        dock: top;
    }

    #filter-row {
        height: 3;
        width: 1fr;
    }

    #filter-project {
        width: 30;
        margin-right: 1;
    }

    #filter-status {
        width: 24;
        margin-right: 1;
    }

    #filter-scope {
        width: 24;
        margin-right: 1;
    }

    #btn-refresh {
        width: 10;
        min-width: 10;
    }

    #task-table {
        height: 1fr;
    }

    #pagination-bar {
        height: 3;
        padding: 0 2;
        background: $surface;
        dock: bottom;
        layout: horizontal;
        align: center middle;
    }

    #pagination-bar Label {
        margin: 0 2;
        width: auto;
    }

    #pagination-bar Button {
        min-width: 10;
    }

    #status-bar {
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
        self._filter_status: TaskStatus | None = None
        self._filter_scope: ScopeLevel | None = None
        self._tasks: list[SummaryTaskDto] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="filter-bar"):
            with Horizontal(id="filter-row"):
                yield Input(
                    placeholder="项目ID 过滤...",
                    id="filter-project",
                )
                yield Select(
                    _STATUS_OPTIONS,
                    prompt="全部状态",
                    id="filter-status",
                    allow_blank=True,
                )
                yield Select(
                    _SCOPE_OPTIONS,
                    prompt="全部层级",
                    id="filter-scope",
                    allow_blank=True,
                )
                yield Button("刷新", id="btn-refresh", variant="primary")

        yield DataTable(id="task-table", cursor_type="row", zebra_stripes=True)

        with Horizontal(id="pagination-bar"):
            yield Button("◀ 上一页", id="btn-prev", variant="default")
            yield Label("", id="page-info")
            yield Button("下一页 ▶", id="btn-next", variant="default")

        yield Footer()

    def on_mount(self) -> None:
        """页面加载时初始化表格列和数据。"""
        table = self.query_one("#task-table", DataTable)
        table.add_column("ID", width=10, key="id")
        table.add_column("项目", width=12, key="project")
        table.add_column("名称", key="name")  # 自动占满剩余宽度
        table.add_column("状态", width=18, key="status")
        table.add_column("层级", width=15, key="scope")
        table.add_column("父任务", width=10, key="parent")
        table.add_column("工作量", width=8, key="effort")
        table.add_column("价值", width=8, key="value")
        self._load_data()

    # --- 过滤器事件 ---

    @on(Input.Changed, "#filter-project")
    def _on_project_filter_changed(self, event: Input.Changed) -> None:
        self._filter_project = event.value.strip() or None
        self._current_page = 1
        self._load_data()

    @on(Select.Changed, "#filter-status")
    def _on_status_filter_changed(self, event: Select.Changed) -> None:
        value = event.value
        self._filter_status = TaskStatus(value) if value not in (Select.BLANK, Select.NULL) else None
        self._current_page = 1
        self._load_data()

    @on(Select.Changed, "#filter-scope")
    def _on_scope_filter_changed(self, event: Select.Changed) -> None:
        value = event.value
        self._filter_scope = ScopeLevel(value) if value not in (Select.BLANK, Select.NULL) else None
        self._current_page = 1
        self._load_data()

    # --- 分页事件 ---

    @on(Button.Pressed, "#btn-prev")
    def _on_prev_page(self) -> None:
        if self._current_page > 1:
            self._current_page -= 1
            self._load_data()

    @on(Button.Pressed, "#btn-next")
    def _on_next_page(self) -> None:
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._load_data()

    @on(Button.Pressed, "#btn-refresh")
    def _on_refresh_button(self) -> None:
        self._load_data()

    # --- 表格行选中 ---

    @on(DataTable.RowSelected)
    def _on_row_selected(self, event: DataTable.RowSelected) -> None:
        """行被选中（Enter 或双击）时跳转到详情。"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self._tasks):
            task = self._tasks[row_index]
            self.app.navigate_to_task(task.id)

    # --- 快捷键 ---

    def action_refresh(self) -> None:
        self._load_data()

    def action_focus_filter(self) -> None:
        self.query_one("#filter-project", Input).focus()

    def action_quit(self) -> None:
        self.app.exit()

    # --- 数据加载 ---

    @work(thread=True)
    @inject
    def _load_data(
        self, use_case: ListTasks = Provide["planning.list_tasks"]
    ) -> None:
        """从 use case 加载任务数据（在工作线程中执行同步 DB 操作）。"""
        query = ListTasksQuery(
            project_id=self._filter_project,
            status=self._filter_status,
            scope_level=self._filter_scope,
            page=self._current_page,
            page_size=self._page_size,
        )
        result: ListTasksResult = use_case.execute(query)

        # 切回主线程更新 UI
        self.app.call_from_thread(self._apply_result, result)

    def _apply_result(self, result: ListTasksResult) -> None:
        """将查询结果应用到表格（必须在主线程调用）。"""
        if result.error:
            self.notify(f"加载失败: {result.error}", severity="error")
            return

        self._tasks = result.tasks
        self._total_count = result.total_count
        self._total_pages = result.total_pages
        self._current_page = result.current_page

        # 刷新表格
        table = self.query_one("#task-table", DataTable)
        table.clear()

        for task in self._tasks:
            status_color = STATUS_COLORS.get(task.status, "white")
            scope_color = SCOPE_COLORS.get(task.scope_level, "white")

            table.add_row(
                short_id(task.id),
                task.project_id,
                Text(task.name),
                f"[{status_color}]{task.status}[/{status_color}]",
                f"[{scope_color}]{task.scope_level}[/{scope_color}]",
                short_id(task.parent_id) if task.parent_id else "-",
                str(task.effort),
                str(task.base_value),
                key=task.id,
            )

        # 更新分页信息
        page_label = self.query_one("#page-info", Label)
        page_label.update(
            f"第 {self._current_page}/{self._total_pages} 页 · 共 {self._total_count} 条"
        )

        # 更新分页按钮状态
        self.query_one("#btn-prev", Button).disabled = self._current_page <= 1
        self.query_one("#btn-next", Button).disabled = (
            self._current_page >= self._total_pages
        )
