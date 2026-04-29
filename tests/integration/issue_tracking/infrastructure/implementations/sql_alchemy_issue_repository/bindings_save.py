from typing import Self
import pytest
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from tests.factories.issue_factory import IssueFactory
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.enums import IssueStatus
from task_graph.issue_tracking.domain.value_objects.label import Label
from task_graph.issue_tracking.infrastructure.adapters.sql_alchemy_issue_repository import (
    SqlAlchemyIssueRepository,
)


@dataclass
class SaveBindings:
    session: Session
    repository: SqlAlchemyIssueRepository = field(init=False)
    _arranged_issue: Issue | None = field(default=None, init=False)
    _retrieved_issue: Issue | None = field(default=None, init=False)

    def __post_init__(self: "SaveBindings") -> None:
        self.repository = SqlAlchemyIssueRepository(session=self.session)

    def given(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "传入一个未持久化的Issue聚合根实例":
                self._arrange_new_issue()
            case "传入一个已在数据库中存在的Issue聚合根实例":
                self._arrange_existing_issue()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self) -> "SaveBindings":
        return self

    def when(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "调用save方法":
                self._when_call_save()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "Issue实例被持久化到数据库，没有返回值":
                self._then_issue_persisted()
            case "数据库中对应的Issue记录被更新，没有返回值":
                self._then_issue_updated()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_new_issue(self) -> None:
        self._arranged_issue = IssueFactory.create()
        # 添加一些关联数据
        self._arranged_issue.add_label(Label.create(name="bug"))
        self._arranged_issue.add_comment("Initial comment", author="test_user")

    def _arrange_existing_issue(self) -> None:
        # 先保存一个Issue
        issue = IssueFactory.create()
        self.repository.save(issue)
        self.session.flush()

        from task_graph.issue_tracking.domain.value_objects.issue_title import IssueTitle
        from task_graph.issue_tracking.domain.value_objects.issue_description import IssueDescription
        # 修改Issue的一些属性
        issue.title = IssueTitle.create("Updated Title")
        issue.description = IssueDescription.create("Updated Description")
        issue.status = IssueStatus.IN_PROGRESS
        issue.add_comment("New comment after update", author="updater")
        issue.add_label(Label.create(name="in-progress"))

        self._arranged_issue = issue

    # ─────────────────────────── Act ────────────────────────────

    def _when_call_save(self) -> None:
        assert self._arranged_issue is not None
        self.repository.save(self._arranged_issue)
        self.session.flush()

    # ─────────────────────────── Assert ────────────────────────────

    def _then_issue_persisted(self) -> None:
        assert self._arranged_issue is not None
        # 从数据库查询回来
        self._retrieved_issue = self.repository.find_by_id(self._arranged_issue.id)
        assert self._retrieved_issue is not None
        # 全量深度比对所有属性，确保没有字段遗漏
        assert self._retrieved_issue.model_dump() == self._arranged_issue.model_dump()

    def _then_issue_updated(self) -> None:
        assert self._arranged_issue is not None
        # 从数据库查询回来
        self._retrieved_issue = self.repository.find_by_id(self._arranged_issue.id)
        assert self._retrieved_issue is not None
        # 全量深度比对所有属性，确保更新完全正确
        assert self._retrieved_issue.model_dump() == self._arranged_issue.model_dump()


@pytest.fixture
def save_bindings(db_session: Session) -> SaveBindings:
    return SaveBindings(session=db_session)
