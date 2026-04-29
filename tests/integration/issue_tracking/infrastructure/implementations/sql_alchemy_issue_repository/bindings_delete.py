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
class DeleteBindings:
    session: Session
    repository: SqlAlchemyIssueRepository = field(init=False)
    _arranged_issue: Issue | None = field(default=None, init=False)
    _issue_id_to_delete: IssueId | None = field(default=None, init=False)
    _result: bool = field(default=False, init=False)

    def __post_init__(self: "DeleteBindings") -> None:
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

    def arrange_done(self) -> "DeleteBindings":
        return self

    def when(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "调用delete方法":
                self._when_call_delete()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "Issue被从数据库中删除，返回True":
                self._then_issue_deleted_return_true()
            case "数据库没有变化，返回False":
                self._then_no_change_return_false()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_existing_issue(self) -> None:
        issue = IssueFactory.create()
        self.repository.save(issue)
        self._arranged_issue = issue
        self._issue_id_to_delete = issue.id

    def _arrange_non_existent_issue_id(self) -> None:
        self._issue_id_to_delete = IssueId.create()

    # ─────────────────────────── Act ────────────────────────────

    def _when_call_delete(self) -> None:
        assert self._issue_id_to_delete is not None
        self._result = self.repository.delete(self._issue_id_to_delete)

    # ─────────────────────────── Assert ────────────────────────────

    def _then_issue_deleted_return_true(self) -> None:
        assert self._result is True
        # 验证数据库中确实不存在了
        assert self._issue_id_to_delete is not None
        deleted_issue = self.repository.find_by_id(self._issue_id_to_delete)
        assert deleted_issue is None

    def _then_no_change_return_false(self) -> None:
        assert self._result is False


@pytest.fixture
def delete_bindings(db_session: Session) -> DeleteBindings:
    return DeleteBindings(session=db_session)
