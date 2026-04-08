from enum import Enum


class CompletionLogic(Enum):
    """Rules defining how a task is unlocked based on its dependencies."""

    ALL = "all"
    ANY = "any"


class TaskStatus(Enum):
    """The lifecycle state of a task."""

    PENDING = "pending"

    BLOCKED = "blocked"

    READY = "ready"

    IN_PROGRESS = "in_progress"

    REVIEW = "review"

    DONE = "done"

    CHANGES_REQUESTED = "changes_requested"

    SKIPPED = "skipped"

    DISCARDED = "discarded"


class PlanningLevel(Enum):
    """Defines the uncertainty and granularity of the task."""

    INITIATIVE = "initiative"

    MILESTONE = "milestone"

    ARCHITECTURAL = "architectural"

    FEATURE = "feature"

    ATOMIC = "atomic"


class RecurrenceType(Enum):

    ON_SUCCESS = "on_success"

    CRON = "cron"

    ON_FAILURE = "on_failure"


class ScopeLevel(Enum):
    """
    Defines the delegation level of the task, mapping directly to Agent roles and context boundaries.
    """
    PROJECT = "project"             # PM/系统架构师：负责跨上下文的需求路由与最终交付
    CONTEXT = "context"             # 领域专家：负责单一上下文内的业务分析与架构拆解
    ARCHITECTURAL = "architectural" # 技术负责人：负责特定代码分层的技术设计与原子任务派发
    ATOMIC = "atomic"               # 程序员：负责单一职责的代码落地
    

class ArchitectureLayer(Enum):
    """DDD architecture layers."""
    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    INTERFACES = "interfaces"
    CROSS_CUTTING = "cross_cutting" # 横切关注点，如日志、通用配置
    NONE = "none" # 适用于非代码层面的任务
