"""Issue TUI 主题配置：颜色映射与样式常量。"""


# Issue 状态 → 颜色映射
ISSUE_STATUS_COLORS: dict[str, str] = {
    "reported": "dim white",
    "triaged": "yellow",
    "in_progress": "dodger_blue1",
    "resolved": "green",
    "closed": "dim",
}

# 严重度 → 颜色映射
SEVERITY_COLORS: dict[str, str] = {
    "critical": "red bold",
    "major": "dark_orange",
    "minor": "yellow",
    "low": "dim",
}

# Issue 类型 → 颜色映射
ISSUE_TYPE_COLORS: dict[str, str] = {
    "bug": "red",
    "feature": "green",
    "question": "cyan",
    "improvement": "magenta",
}


def styled_issue_status(status: str) -> str:
    """返回带颜色标记的 Issue 状态文本。"""
    color = ISSUE_STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def styled_severity(severity: str) -> str:
    """返回带颜色标记的严重度文本。"""
    color = SEVERITY_COLORS.get(severity, "white")
    return f"[{color}]{severity}[/{color}]"


def styled_issue_type(issue_type: str) -> str:
    """返回带颜色标记的 Issue 类型文本。"""
    color = ISSUE_TYPE_COLORS.get(issue_type, "white")
    return f"[{color}]{issue_type}[/{color}]"


def short_id(issue_id: str, length: int = 8) -> str:
    """截断 IssueID 用于列表显示。"""
    return issue_id[:length] if len(issue_id) > length else issue_id
