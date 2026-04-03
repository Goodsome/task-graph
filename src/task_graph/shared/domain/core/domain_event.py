from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class DomainEvent(BaseModel):
    """领域事件基类 所有领域事件必须： 1. 不可变（frozen=True） 2. 包含唯一标识和时间戳 3. 使用 UTC 时区 4. 携带事件类型标识"""

    event_id: UUID = Field(default_factory=uuid4, description="事件唯一标识")
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="事件发生时间（UTC）",
    )
    event_type: str = Field(
        default="",
        description="事件类型标识",
    )
    version: int = Field(default=1, description="事件版本")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    def __init__(self, **data):
        # 自动设置 event_type 为类名（如果未提供）
        if "event_type" not in data or not data["event_type"]:
            data["event_type"] = self.__class__.__name__
        super().__init__(**data)
