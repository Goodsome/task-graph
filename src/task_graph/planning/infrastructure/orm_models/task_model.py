from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Table, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from datetime import datetime, timezone
from typing import List, Optional
import uuid
from task_graph.shared.infrastructure.orm import Base

# 保留这个表！它是图数据的核心
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('dependency_id', UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
)

class TaskModel(Base):
    __tablename__ = 'tasks'

    # 1. 使用原生 UUID，性能比 String(36) 更好
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 2. 如果状态是固定的，可以使用 Enum (可选，依然用 String 也可以)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    scope_level: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    scope_context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    completion_logic: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=True)

    # 父子层级关系
    children: Mapped[List["TaskModel"]] = relationship(
        "TaskModel",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )

    effort: Mapped[int] = mapped_column(Integer, nullable=False)
    base_value: Mapped[float] = mapped_column(Float, nullable=False)

    # 3. 关键优化：使用 JSONB 而不是 JSON
    # JSONB 是二进制存储，支持索引。你可以直接查询 "WHERE output->'artifacts' ? 'file.py'"
    output: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    review_feedback: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # 时间戳处理保持不变
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # 关系保持不变
    dependencies: Mapped[List["TaskModel"]] = relationship(
        'TaskModel',
        secondary=task_dependencies,
        primaryjoin="TaskModel.id == task_dependencies.c.task_id",
        secondaryjoin="TaskModel.id == task_dependencies.c.dependency_id",
        backref='dependents',
        lazy='selectin' # 既然是图，通常需要加载依赖，selectin 性能较好
    )

    __mapper_args__ = {
        "version_id_col": version_id
    }