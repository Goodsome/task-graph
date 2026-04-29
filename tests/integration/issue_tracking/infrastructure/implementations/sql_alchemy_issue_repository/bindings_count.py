from typing import Self
import pytest
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from tests.factories.issue_factory import IssueFactory
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.issue_tracking.infrastructure.adapters.sql_alchemy_issue_repository import (
    SqlAlchemyIssueRepository,
)


@dataclass
class CountBindings:
    session: Session
    repository: SqlAlchemyIssueRepository = field(init=False)
    _arranged_issues: list[Issue] = field(default_factory=list, init=False)
    _result: int = field(default=0, init=False)
    _filter_status: IssueStatus | None = field(default=None, init=False)
    _filter_issue_type: IssueType | None = field(default=None, init=False)

    def __post_init__(self: "CountBindings") -> None:
        self.repository = SqlAlchemyIssueRepository(session=self.session)

    def given(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "不传入任何过滤参数":
                self._arrange_multiple_issues()
            case "传入status或issue_type过滤参数":
                self._arrange_issues_with_different_attributes()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self) -> "CountBindings":
        return self

    def when(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "调用count方法":
                self._when_call_count()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "返回数据库中所有Issue的总数量":
                self._then_return_total_count()
            case "返回符合过滤条件的Issue数量":
                self._then_return_filtered_count()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_multiple_issues(self) -> None:
        # 创建3个不同的Issue
        for _ in range(3):
            issue = IssueFactory.build()
            self.repository.save(issue)
            self._arranged_issues.append(issue)

    def _arrange_issues_with_different_attributes(self) -> None:
        # 创建2个BUG类型的IN_PROGRESS状态Issue
        for _ in range(2):
            issue = IssueFactory.build(
                type=IssueType.BUG,
                severity=Severity.CRITICAL,
            )
            issue.status = IssueStatus.IN_PROGRESS
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        # 创建3个FEATURE类型的IN_PROGRESS状态Issue
        for _ in range(3):
            issue = IssueFactory.build(
                type=IssueType.FEATURE,
                severity=Severity.MAJOR,
            )
            issue.status = IssueStatus.IN_PROGRESS
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        # 设置过滤条件为BUG类型
        self._filter_issue_type = IssueType.BUG

    # ─────────────────────────── Act ────────────────────────────

    def _when_call_count(self) -> None:
        self._result = self.repository.count(
            status=self._filter_status,
            issue_type=self._filter_issue_type
        )

    # ─────────────────────────── Assert ────────────────────────────

    def _then_return_total_count(self) -> None:
        assert self._result == len(self._arranged_issues)

    def _then_return_filtered_count(self) -> None:
        # 应该只返回BUG类型的数量（2个）
        assert self._result == 2


@pytest.fixture
def count_bindings(db_session: Session) -> CountBindings:
    return CountBindings(session=db_session)
