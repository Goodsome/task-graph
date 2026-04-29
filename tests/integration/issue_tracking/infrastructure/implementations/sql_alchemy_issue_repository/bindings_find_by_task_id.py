from typing import Self
import pytest
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from uuid import uuid4

from tests.factories.issue_factory import IssueFactory
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.infrastructure.adapters.sql_alchemy_issue_repository import (
    SqlAlchemyIssueRepository,
)


@dataclass
class FindByTaskIdBindings:
    session: Session
    repository: SqlAlchemyIssueRepository = field(init=False)
    _task_id: str | None = field(default=None, init=False)
    _arranged_issues: list[Issue] = field(default_factory=list, init=False)
    _result: list[Issue] = field(default_factory=list, init=False)

    def __post_init__(self: "FindByTaskIdBindings") -> None:
        self.repository = SqlAlchemyIssueRepository(session=self.session)

    def given(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "传入有效的task_id":
                self._arrange_issues_linked_to_task()
            case "传入的task_id没有关联任何Issue":
                self._arrange_task_without_linked_issues()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self) -> "FindByTaskIdBindings":
        return self

    def when(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "调用find_by_task_id方法":
                self._when_call_find_by_task_id()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "返回所有与该task_id关联的Issue列表":
                self._then_return_linked_issues()
            case "返回空列表":
                self._then_return_empty_list()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_issues_linked_to_task(self) -> None:
        self._task_id = str(uuid4())

        # 创建2个关联到这个task_id的Issue
        for _ in range(2):
            issue = IssueFactory.create()
            issue.link_to_task(self._task_id)
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        # 创建3个不关联的Issue
        for _ in range(3):
            issue = IssueFactory.create()
            self.repository.save(issue)
            self._arranged_issues.append(issue)

    def _arrange_task_without_linked_issues(self) -> None:
        self._task_id = str(uuid4())

        # 创建一些Issue但不关联到这个task_id
        for _ in range(5):
            issue = IssueFactory.create()
            self.repository.save(issue)
            self._arranged_issues.append(issue)

    # ─────────────────────────── Act ────────────────────────────

    def _when_call_find_by_task_id(self) -> None:
        assert self._task_id is not None
        self._result = self.repository.find_by_task_id(self._task_id)

    # ─────────────────────────── Assert ────────────────────────────

    def _then_return_linked_issues(self) -> None:
        assert len(self._result) == 2
        assert all(self._task_id in [str(tl.task_id) for tl in issue.task_links] for issue in self._result)

    def _then_return_empty_list(self) -> None:
        assert len(self._result) == 0


@pytest.fixture
def find_by_task_id_bindings(db_session: Session) -> FindByTaskIdBindings:
    return FindByTaskIdBindings(session=db_session)
