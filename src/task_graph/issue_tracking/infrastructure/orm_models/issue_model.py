from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import uuid
from task_graph.shared.infrastructure.orm import Base
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity


class IssueModel(Base):
    __tablename__: str = "issues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    type: Mapped[IssueType] = mapped_column(
        ENUM(IssueType, name="issue_type_enum"), nullable=False
    )
    severity: Mapped[Severity] = mapped_column(
        ENUM(Severity, name="issue_severity_enum"), nullable=False
    )
    status: Mapped[IssueStatus] = mapped_column(
        ENUM(IssueStatus, name="issue_status_enum"),
        nullable=False,
        default=IssueStatus.REPORTED,
    )

    # Submitter information
    submitter_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Array of labels (stored as JSONB for flexibility)
    labels: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Relationships
    comments: Mapped[list["IssueCommentModel"]] = relationship(
        "IssueCommentModel",
        back_populates="issue",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="IssueCommentModel.created_at",
    )

    task_links: Mapped[list["IssueTaskLinkModel"]] = relationship(
        "IssueTaskLinkModel",
        back_populates="issue",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __mapper_args__: dict[str, object] = {"version_id_col": version_id}


class IssueCommentModel(Base):
    __tablename__: str = "issue_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    issue: Mapped["IssueModel"] = relationship("IssueModel", back_populates="comments")


class IssueTaskLinkModel(Base):
    __tablename__: str = "issue_task_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False
    )
    # task_id 是跨领域引用，不设置外键约束，仅存储 UUID 字符串
    task_id: Mapped[str] = mapped_column(String(36), nullable=False)

    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    issue: Mapped["IssueModel"] = relationship(
        "IssueModel", back_populates="task_links"
    )

    __table_args__: tuple[UniqueConstraint] = (
        # 复合唯一约束，防止同一个 issue 和 task 重复关联
        UniqueConstraint("issue_id", "task_id", name="uq_issue_task_link"),
    )
