from enum import Enum
from typing import Any, Type
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class ValidatedEnum(Enum):
    """Base class for enums that can be validated from strings via Pydantic."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate_from_str(value: Any) -> ValidatedEnum:
            if isinstance(value, str):
                return cls(value)
            if isinstance(value, cls):
                return value
            raise TypeError(f"Cannot convert {type(value)} to {cls.__name__}")

        str_schema = core_schema.no_info_plain_validator_function(validate_from_str)
        return core_schema.json_or_python_schema(
            json_schema=str_schema,
            python_schema=str_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.value),
        )


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
    REVIEWING = "reviewing"
    DECOMPOSING = "decomposing"
    DONE = "done"
    CHANGES_REQUESTED = "changes_requested"
    SKIPPED = "skipped"
    DISCARDED = "discarded"


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
