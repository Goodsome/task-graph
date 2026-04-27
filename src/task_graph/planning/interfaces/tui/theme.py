"""TUI 主题配置：颜色映射与样式常量。"""


# 任务状态 → 颜色映射
STATUS_COLORS: dict[str, str] = {
    "pending": "dim white",
    "blocked": "red",
    "ready": "green",
    "in_progress": "dodger_blue1",
    "reviewing": "dark_orange",
    "decomposing": "medium_purple",
    "done": "green bold",
    "changes_requested": "yellow",
    "skipped": "dim",
    "discarded": "dim italic",
}

# 层级 → 颜色映射
SCOPE_COLORS: dict[str, str] = {
    "project": "bright_cyan",
    "context": "bright_magenta",
    "architectural": "bright_yellow",
    "component": "bright_green",
}


def styled_status(status: str) -> str:
    """返回带颜色标记的状态文本。"""
    color = STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def styled_scope(scope_level: str) -> str:
    """返回带颜色标记的层级文本。"""
    color = SCOPE_COLORS.get(scope_level, "white")
    return f"[{color}]{scope_level}[/{color}]"


def short_id(task_id: str, length: int = 8) -> str:
    """截断 TaskID 用于列表显示。"""
    return task_id[:length] if len(task_id) > length else task_id
