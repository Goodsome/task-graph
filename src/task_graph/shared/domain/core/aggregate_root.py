from pydantic import BaseModel, PrivateAttr, ConfigDict

from .domain_event import DomainEvent


class AggregateRoot(BaseModel):
    """聚合根基类 特征： 1. 继承 Entity 的所有特性 2. 管理领域事件的发布和收集 3. 确保聚合边界内的一致性"""
    
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    _domain_events: list[DomainEvent] = PrivateAttr(default_factory=list)

    def add_domain_event(self, event: DomainEvent) -> None:
        """添加领域事件
        Args:
            event: 要添加的领域事件实例
        Raises:
            TypeError: 如果 event 不是 DomainEvent 的实例
        """
        if not isinstance(event, DomainEvent):
            raise TypeError(f"Expected DomainEvent, got {type(event).__name__}")

        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        """收集并清空领域事件
        Returns:
            收集到的所有领域事件列表（副本）
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def clear_events(self) -> None:
        """清空领域事件"""
        self._domain_events.clear()

    def has_events(self) -> bool:
        """检查是否有未处理的领域事件

        Returns:
            如果有事件返回 True，否则返回 False
        """
        return len(self._domain_events) > 0
