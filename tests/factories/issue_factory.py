from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use
from uuid import uuid4
from faker import Faker

fake = Faker()

from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.enums import IssueType, Severity, IssueStatus
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.domain.value_objects.issue_title import IssueTitle
from task_graph.issue_tracking.domain.value_objects.issue_description import IssueDescription
from task_graph.issue_tracking.domain.value_objects.submitter import Submitter
from task_graph.issue_tracking.domain.value_objects.label import Label
from task_graph.issue_tracking.domain.value_objects.task_link import TaskLink
from task_graph.issue_tracking.domain.entities.comment import Comment


# ==========================================
# Value Object Factories
# ==========================================
class IssueIdFactory(ModelFactory[IssueId]):
    __model__ = IssueId

    @classmethod
    def value(cls) -> str:
        return str(uuid4())


class IssueTitleFactory(ModelFactory[IssueTitle]):
    __model__ = IssueTitle

    @classmethod
    def value(cls) -> str:
        return fake.sentence(nb_words=6)


class IssueDescriptionFactory(ModelFactory[IssueDescription]):
    __model__ = IssueDescription

    @classmethod
    def value(cls) -> str:
        return fake.paragraph(nb_sentences=3)


class SubmitterFactory(ModelFactory[Submitter]):
    __model__ = Submitter

    name = Use(lambda: fake.name())


class LabelFactory(ModelFactory[Label]):
    __model__ = Label

    name = Use(lambda: fake.word())


class TaskLinkFactory(ModelFactory[TaskLink]):
    __model__ = TaskLink

    @classmethod
    def task_id(cls) -> str:
        return str(uuid4())


class CommentFactory(ModelFactory[Comment]):
    __model__ = Comment

    content = Use(lambda: fake.sentence())
    author = Use(lambda: fake.name())


# ==========================================
# Aggregate Root Factory
# ==========================================
class IssueFactory(ModelFactory[Issue]):
    __model__ = Issue

    # 定制化生成逻辑
    project_id = Use(lambda: str(uuid4()))
    title = Use(IssueTitleFactory.build)
    description = Use(IssueDescriptionFactory.build)
    type = Use(lambda: fake.random_element(list(IssueType)))
    severity = Use(lambda: fake.random_element(list(Severity)))
    status = IssueStatus.REPORTED
    submitter = Use(SubmitterFactory.build)
    labels = Use(lambda: [LabelFactory.build() for _ in range(fake.random_int(0, 3))])
    comments = Use(lambda: [CommentFactory.build() for _ in range(fake.random_int(0, 5))])
    task_links = list()
    created_at = Use(lambda: fake.date_time())
    updated_at = Use(lambda: fake.date_time())

    @classmethod
    def create(
        cls,
        project_id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        issue_type: IssueType | None = None,
        severity: Severity | None = None,
        submitter: Submitter | None = None,
        **kwargs
    ) -> Issue:
        """Create a new Issue aggregate using the domain factory method"""
        return Issue.create(
            project_id=project_id or str(uuid4()),
            title=title or IssueTitleFactory.build().value,
            description=description or IssueDescriptionFactory.build().value,
            issue_type=issue_type or fake.random_element(list(IssueType)),
            severity=severity or fake.random_element(list(Severity)),
            submitter=submitter or SubmitterFactory.build(),
            **kwargs
        )

