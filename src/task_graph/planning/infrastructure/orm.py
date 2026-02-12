from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Table, JSON, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

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

    id = Column(String(36), primary_key=True)
    project_id = Column(String(64), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(32), index=True, nullable=False)
    planning_level = Column(String(32), index=True, nullable=False)
    completion_logic = Column(String(32), nullable=False)
    effort = Column(Integer, nullable=False)
    base_value = Column(Float, nullable=False)
    
    # Value Objects stored as JSON
    output = Column(JSON, nullable=True)
    review_feedback = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    version_id = Column(Integer, nullable=False, default=1)

    # Self-referential relationship for dependencies
    dependencies = relationship(
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
