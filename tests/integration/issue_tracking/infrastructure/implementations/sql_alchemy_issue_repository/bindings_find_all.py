from typing import Self
import pytest
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from tests.factories.issue_factory import IssueFactory
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from task_graph.issue_tracking.domain.value_objects.label import Label
from task_graph.issue_tracking.infrastructure.adapters.sql_alchemy_issue_repository import (
    SqlAlchemyIssueRepository,
)


@dataclass
class FindAllBindings:
    session: Session
    repository: SqlAlchemyIssueRepository = field(init=False)
    _arranged_issues: list[Issue] = field(default_factory=list, init=False)
    _limit: int = field(default=10, init=False)
    _offset: int = field(default=0, init=False)
    _filter_status: IssueStatus | None = field(default=None, init=False)
    _filter_issue_type: IssueType | None = field(default=None, init=False)
    _filter_severity: Severity | None = field(default=None, init=False)
    _filter_labels: list[str] | None = field(default=None, init=False)
    _result: list[Issue] = field(default_factory=list, init=False)

    def __post_init__(self: "FindAllBindings") -> None:
        self.repository = SqlAlchemyIssueRepository(session=self.session)

    def given(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "传入limit和offset参数，其他过滤参数为空":
                self._arrange_multiple_issues()
            case "传入status过滤参数":
                self._arrange_issues_with_different_statuses()
            case "传入多个过滤参数（如status、issue_type、severity、labels）":
                self._arrange_issues_with_multiple_attributes()
            case "过滤条件没有匹配的Issue":
                self._arrange_no_matching_issues()
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self) -> "FindAllBindings":
        return self

    def when(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "调用find_all方法":
                self._when_call_find_all()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        match semantic_text:
            case "返回按分页参数查询到的Issue列表，不应用任何过滤条件":
                self._then_return_paginated_issues()
            case "返回符合指定状态的Issue列表":
                self._then_return_status_filtered_issues()
            case "返回同时满足所有过滤条件的Issue列表":
                self._then_return_all_filters_matched()
            case "返回空列表":
                self._then_return_empty_list()
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    # ─────────────────────────── Arrange ────────────────────────────

    def _arrange_multiple_issues(self) -> None:
        # 创建10个Issue
        for i in range(10):
            issue = IssueFactory.create()
            self.repository.save(issue)
            self._arranged_issues.append(issue)
        self._limit = 5
        self._offset = 0

    def _arrange_issues_with_different_statuses(self) -> None:
        # 创建3个REPORTED状态的Issue
        for _ in range(3):
            issue = IssueFactory.create()
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        # 创建2个IN_PROGRESS状态的Issue
        for _ in range(2):
            issue = IssueFactory.create()
            issue.status = IssueStatus.IN_PROGRESS
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        self._filter_status = IssueStatus.IN_PROGRESS

    def _arrange_issues_with_multiple_attributes(self) -> None:
        # 创建2个符合条件的Issue：BUG类型、CRITICAL严重度、带bug标签
        bug_label = Label.create(name="bug")
        for _ in range(2):
            issue = IssueFactory.create(
                issue_type=IssueType.BUG,
                severity=Severity.CRITICAL,
            )
            issue.add_label(bug_label)
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        # 创建3个不符合条件的Issue
        for _ in range(3):
            issue = IssueFactory.create(
                issue_type=IssueType.FEATURE,
                severity=Severity.MINOR,
            )
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        self._filter_issue_type = IssueType.BUG
        self._filter_severity = Severity.CRITICAL
        self._filter_labels = ["bug"]

    def _arrange_no_matching_issues(self) -> None:
        # 创建一些Issue，但过滤条件不会匹配
        for _ in range(5):
            issue = IssueFactory.create()
            self.repository.save(issue)
            self._arranged_issues.append(issue)

        # 过滤不存在的标签
        self._filter_labels = ["non-existent-tag"]

    # ─────────────────────────── Act ────────────────────────────

    def _when_call_find_all(self) -> None:
        self._result = self.repository.find_all(
            limit=self._limit,
            offset=self._offset,
            status=self._filter_status,
            issue_type=self._filter_issue_type,
            severity=self._filter_severity,
            labels=self._filter_labels,
        )

    # ─────────────────────────── Assert ────────────────────────────

    def _then_return_paginated_issues(self) -> None:
        assert len(self._result) == self._limit
        # 验证返回的是最新创建的5个
        issue_ids = [str(i.id) for i in self._result]
        expected_ids = [str(i.id) for i in sorted(self._arranged_issues, key=lambda x: x.created_at, reverse=True)[:5]]
        assert issue_ids == expected_ids

    def _then_return_status_filtered_issues(self) -> None:
        assert len(self._result) == 2
        assert all(issue.status == IssueStatus.IN_PROGRESS for issue in self._result)

    def _then_return_all_filters_matched(self) -> None:
        assert len(self._result) == 2
        assert all(issue.type == IssueType.BUG for issue in self._result)
        assert all(issue.severity == Severity.CRITICAL for issue in self._result)
        assert all(any(label.name == "bug" for label in issue.labels) for issue in self._result)

    def _then_return_empty_list(self) -> None:
        assert len(self._result) == 0


@pytest.fixture
def find_all_bindings(db_session: Session) -> FindAllBindings:
    return FindAllBindings(session=db_session)
