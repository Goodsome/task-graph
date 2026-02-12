from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Table, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import List, Optional

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

# Association table for self-referential many-to-many relationship (DAG)
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', String(36), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('dependency_id', String(36), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
)

class TaskModel(Base):
    """SQLAlchemy model for Task aggregate."""
    __tablename__ = 'tasks'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    planning_level: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    completion_logic: Mapped[str] = mapped_column(String(32), nullable=False)
    effort: Mapped[int] = mapped_column(Integer, nullable=False)
    base_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Value Objects stored as JSON
    output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    review_feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Self-referential relationship for dependencies
    dependencies: Mapped[List["TaskModel"]] = relationship(
        'TaskModel',
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.dependency_id,
        backref='dependents',
        lazy='selectin'
    )
    
    __mapper_args__ = {
        "version_id_col": version_id
    }
