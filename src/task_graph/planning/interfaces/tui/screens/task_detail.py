"""任务详情页面。

展示单个任务的完整信息，支持可点击的 ID 跳转。
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

from task_graph.planning.application.use_cases.get_task_details import (
    GetTaskDetails,
    GetTaskDetailsQuery,
    GetTaskDetailsResult,
)
from task_graph.planning.application.use_cases.delete_task import (
    DeleteTask,
    DeleteTaskCommand,
    DeleteTaskResult,
)
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.interfaces.tui.theme import STATUS_COLORS, SCOPE_COLORS
from task_graph.planning.interfaces.tui.widgets.task_id_label import TaskIdLabel
from task_graph.planning.interfaces.tui.screens.confirm_dialog import ConfirmDialog


class TaskDetailScreen(Screen):
    """任务详情页面。"""

    BINDINGS = [
        ("escape", "go_back", "返回列表"),
        ("d", "delete_task", "删除任务"),
        ("q", "quit", "退出"),
    ]

    DEFAULT_CSS = """
    TaskDetailScreen {
        layout: vertical;
    }

    #detail-header {
        height: auto;
        padding: 1 2;
        background: $surface;
        dock: top;
        layout: horizontal;
    }

    #btn-back {
        min-width: 14;
    }

    #btn-delete {
        min-width: 14;
        margin-left: 1;
    }

    #detail-scroll {
        height: 1fr;
        padding: 1 2;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
    }

    .field-row {
        height: auto;
        margin-bottom: 0;
    }

    .field-label {
        width: 14;
        color: $text-muted;
        text-style: bold;
    }

    .field-value {
        width: 1fr;
    }

    .id-links-row {
        height: auto;
        layout: horizontal;
    }

    .id-links-row TaskIdLabel {
        margin-right: 1;
    }

    #detail-loading {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
        text-style: dim italic;
    }

    .criterion-block {
        margin-left: 2;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
    }

    .criterion-title {
        text-style: bold;
    }

    .criterion-field {
        margin-left: 2;
        color: $text-muted;
    }
    """

    def __init__(self, task_id: str) -> None:
        super().__init__()
        self._task_id = task_id
        self._task_detail: Task | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="detail-header"):
            yield Button("◀ 返回列表", id="btn-back", variant="default")
            yield Button("🗑️ 删除任务", id="btn-delete", variant="error")
        yield Static("正在加载任务详情...", id="detail-loading")
        yield Footer()

    def on_mount(self) -> None:
        self._load_task()

    @on(Button.Pressed, "#btn-back")
    def _on_back(self) -> None:
        self.action_go_back()

    @on(Button.Pressed, "#btn-delete")
    def _on_delete_pressed(self) -> None:
        self.action_delete_task()

    @on(TaskIdLabel.NavigateToTask)
    def _on_navigate_to_task(self, event: TaskIdLabel.NavigateToTask) -> None:
        """处理可点击 ID 的跳转请求。"""
        self.app.navigate_to_task(event.task_id)

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_delete_task(self) -> None:
        """删除当前任务。"""

        def check_confirm(confirmed: bool) -> None:
            if confirmed:
                self._delete_task()

        self.app.push_screen(
            ConfirmDialog("确定要删除这个任务吗？此操作无法撤销。"),
            check_confirm,
        )

    def action_quit(self) -> None:
        self.app.exit()

    @work(thread=True)
    @inject
    def _delete_task(
        self, use_case: DeleteTask = Provide["planning.delete_task"]
    ) -> None:
        """执行删除任务的 Use Case。"""
        cmd = DeleteTaskCommand(task_id=self._task_id)
        result: DeleteTaskResult = use_case.execute(cmd)

        if result.success:
            self.app.call_from_thread(self.notify, "任务已成功删除", severity="information")
            self.app.call_from_thread(self.action_go_back)
        else:
            self.app.call_from_thread(
                self.notify, f"删除失败: {result.error}", severity="error"
            )

    @work(thread=True)
    @inject
    def _load_task(
        self, use_case: GetTaskDetails = Provide["planning.get_task_details"]
    ) -> None:
        query = GetTaskDetailsQuery(task_id=self._task_id)
        result: GetTaskDetailsResult = use_case.execute(query)
        self.app.call_from_thread(self._render_task, result)

    def _render_task(self, result: GetTaskDetailsResult) -> None:
        """将任务数据渲染到页面。"""
        # 移除 loading
        loading = self.query_one("#detail-loading", Static)
        loading.remove()

        if not result.success or result.task is None:
            error_msg = result.error or "未知错误"
            self.mount(
                Static(f"[red bold]加载失败:[/] {error_msg}", id="detail-error"),
                after=self.query_one("#detail-header"),
            )
            return

        task = result.task
        self._task_detail = task

        # 构建详情内容
        scroll = VerticalScroll(id="detail-scroll")
        self.mount(scroll, after=self.query_one("#detail-header"))

        # --- 基本信息 ---
        scroll.mount(Static("📋 基本信息", classes="section-title"))
        scroll.mount(Rule())
        self._add_field(scroll, "ID", str(task.id))
        self._add_field(scroll, "名称", task.name)
        self._add_field(scroll, "项目", task.project_id)

        # 状态（带颜色）
        status_color = STATUS_COLORS.get(task.status.value, "white")
        self._add_field(
            scroll,
            "状态",
            f"[{status_color}]{task.status.value}[/{status_color}]",
        )

        # 层级（带颜色）
        scope_color = SCOPE_COLORS.get(task.scope_level.value, "white")
        self._add_field(
            scroll,
            "层级",
            f"[{scope_color}]{task.scope_level.value}[/{scope_color}]",
        )

        # 父任务 ID（可点击）
        if task.parent_id:
            parent_row = Horizontal(classes="field-row")
            scroll.mount(parent_row)
            parent_row.mount(Static("父任务", classes="field-label"))
            parent_row.mount(
                TaskIdLabel(str(task.parent_id), show_short=False)
            )
        else:
            self._add_field(scroll, "父任务", "-")

        self._add_field(scroll, "工作量", str(task.effort.value))
        self._add_field(scroll, "价值", str(task.base_value.value))
        self._add_field(scroll, "完成逻辑", task.completion_logic.value)

        # --- 范围上下文 ---
        if task.scope_context:
            scroll.mount(Static(""))
            scroll.mount(Static("🎯 范围上下文", classes="section-title"))
            scroll.mount(Rule())
            self._add_field(
                scroll,
                "所属领域",
                task.scope_context.bounded_context or "-",
            )
            self._add_field(
                scroll,
                "架构层级",
                task.scope_context.architecture_layer.value
                if task.scope_context.architecture_layer
                else "-",
            )
            if task.scope_context.component_name:
                self._add_field(
                    scroll, "组件名称", task.scope_context.component_name
                )

        # --- 重复策略 ---
        if task.recurrence:
            scroll.mount(Static(""))
            scroll.mount(Static("🔄 重复策略", classes="section-title"))
            scroll.mount(Rule())
            self._add_field(scroll, "重复类型", task.recurrence.type.value)
            self._add_field(
                scroll, "最大次数", str(task.recurrence.max_repetitions)
            )
            self._add_field(
                scroll, "当前迭代", str(task.recurrence.current_iteration)
            )

        # --- 描述 ---
        scroll.mount(Static(""))
        scroll.mount(Static("📝 描述", classes="section-title"))
        scroll.mount(Rule())
        scroll.mount(Static(task.description))

        # --- 依赖 ---
        if task.dependencies:
            scroll.mount(Static(""))
            scroll.mount(Static("🔗 依赖", classes="section-title"))
            scroll.mount(Rule())
            dep_row = Horizontal(classes="id-links-row")
            scroll.mount(dep_row)
            for dep_id in task.dependencies:
                dep_row.mount(TaskIdLabel(str(dep_id), show_short=False))

        # --- 验收标准 ---
        if task.acceptance_criteria:
            scroll.mount(Static(""))
            scroll.mount(Static("✅ 验收标准", classes="section-title"))
            scroll.mount(Rule())
            for i, scenario in enumerate(task.acceptance_criteria, 1):
                scroll.mount(
                    Static(f"  [bold]{i}. {scenario.name}[/bold]")
                )
                for step in scenario.steps:
                    scroll.mount(
                        Static(f"    [dim]{step.keyword.value}:[/dim] {step.text}")
                    )
                scroll.mount(Static(""))

        # --- 输出 ---
        if task.output:
            scroll.mount(Static(""))
            scroll.mount(Static("📤 输出", classes="section-title"))
            scroll.mount(Rule())
            self._add_field(scroll, "摘要", task.output.summary)
            if task.output.artifacts:
                self._add_field(
                    scroll,
                    "产出",
                    ", ".join(task.output.artifacts),
                )
            if task.output.error:
                self._add_field(
                    scroll, "错误", f"[red]{task.output.error}[/red]"
                )

            # 子任务
            if task.output.sub_tasks:
                scroll.mount(Static(""))
                scroll.mount(Static("📦 子任务规划", classes="section-title"))
                scroll.mount(Rule())
                for j, sub in enumerate(task.output.sub_tasks, 1):
                    scroll.mount(
                        Static(f"  [bold]{j}. {sub.name}[/bold]")
                    )
                    scroll.mount(
                        Static(f"    描述: {sub.description}")
                    )
                    scroll.mount(
                        Static(
                            f"    工作量: {sub.effort.value}  价值: {sub.base_value.value}"
                        )
                    )
                    if sub.acceptance_criteria:
                        for k, scenario in enumerate(sub.acceptance_criteria, 1):
                            scroll.mount(
                                Static(
                                    f"    [dim]验收 {k}:[/dim] {scenario.name}"
                                )
                            )
                            for step in scenario.steps:
                                scroll.mount(
                                    Static(
                                        f"      [dim]{step.keyword.value}:[/dim] {step.text}"
                                    )
                                )
                    scroll.mount(Static(""))

        # --- 审核反馈 ---
        if task.review_feedback:
            scroll.mount(Static(""))
            scroll.mount(Static("📝 审核反馈", classes="section-title"))
            scroll.mount(Rule())
            decision = task.review_feedback.decision
            decision_color = "green" if decision == "approved" else "yellow"
            self._add_field(
                scroll,
                "决定",
                f"[{decision_color}]{decision}[/{decision_color}]",
            )
            self._add_field(scroll, "意见", task.review_feedback.comment)

    @staticmethod
    def _add_field(
        container: VerticalScroll, label: str, value: str
    ) -> None:
        """添加一个字段行（标签 + 值）。"""
        row = Horizontal(classes="field-row")
        container.mount(row)
        row.mount(Static(label, classes="field-label"))
        row.mount(Static(value, classes="field-value"))
