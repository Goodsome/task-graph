from typing import Self
import pytest
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from tests.factories.issue_factory import IssueFactory
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.infrastructure.adapters.sql_alchemy_issue_repository import (
    SqlAlchemyIssueRepository,
)


@dataclass
class FindByIdBindings:
    session: Session
    repository: SqlAlchemyIssueRepository = field(init=False)
    _arranged_issue: Issue | None = field(default=None, init=False)
    _search_issue_id: IssueId | None = field(default=None, init=False)
    _result: Issue | None = field(default=None, init=False)

    def __post_init__(self: "FindByIdBindings") -> None:
        self.repository = SqlAlchemyIssueRepository(session=self.session)

    def given(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "传入的issue_id对应的Issue在数据库中存在":
                self._arrange_existing_issue()
            case "传入的issue_id对应的Issue在数据库中不存在":
                self._arrange_non_existent_issue_id()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self) -> "FindByIdBindings":
        return self

    def when(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "调用find_by_id方法":
                self._when_call_find_by_id()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "返回对应的Issue聚合根实例":
                self._then_return_correct_issue()
            case "返回None":
                self._then_return_none()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_existing_issue(self) -> None:
        from task_graph.issue_tracking.domain.value_objects.label import Label
        issue = IssueFactory.create()
        # 添加一些标签和评论测试关联关系
        issue.add_label(Label.create(name="bug"))
        issue.add_label(Label.create(name="high-priority"))
        issue.add_comment("This is a test comment", author="test_user")
        self.repository.save(issue)
        self._arranged_issue = issue
        self._search_issue_id = issue.id

    def _arrange_non_existent_issue_id(self) -> None:
        self._search_issue_id = IssueId.create()

    # ─────────────────────────── Act ────────────────────────────

    def _when_call_find_by_id(self) -> None:
        assert self._search_issue_id is not None
        self._result = self.repository.find_by_id(self._search_issue_id)

    # ─────────────────────────── Assert ────────────────────────────

    def _then_return_correct_issue(self) -> None:
        assert self._result is not None
        assert self._arranged_issue is not None
        # 全量深度比对所有属性，确保没有字段遗漏
        assert self._result.model_dump() == self._arranged_issue.model_dump()

    def _then_return_none(self) -> None:
        assert self._result is None


@pytest.fixture
def find_by_id_bindings(db_session: Session) -> FindByIdBindings:
    return FindByIdBindings(session=db_session)
