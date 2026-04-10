from dependency_injector.providers import Dependency, Configuration

from task_graph.issue_tracking.infrastructure.repositories.sql_alchemy_issue_repository import (
    SqlAlchemyIssueRepository,
)
from task_graph.issue_tracking.application.use_cases.update_issue_metadata import (
    UpdateIssueMetadata,
)
from task_graph.issue_tracking.application.use_cases.close_issue import CloseIssue
from task_graph.issue_tracking.application.use_cases.list_issues import ListIssues
from task_graph.issue_tracking.application.use_cases.add_comment import AddComment
from task_graph.issue_tracking.application.use_cases.update_issue_status import (
    UpdateIssueStatus,
)
from task_graph.issue_tracking.application.use_cases.link_issue_to_task import (
    LinkIssueToTask,
)
from task_graph.issue_tracking.application.use_cases.get_issue_details import (
    GetIssueDetails,
)
from task_graph.issue_tracking.application.use_cases.unlink_issue_from_task import (
    UnlinkIssueFromTask,
)
from dependency_injector.providers import Factory
from task_graph.issue_tracking.application.use_cases.create_issue import CreateIssue
from dependency_injector.containers import DeclarativeContainer
from task_graph.issue_tracking.infrastructure.adapters.postgres_notify_event_publisher import (
    PostgresNotifyEventPublisher,
)

from task_graph.shared.infrastructure.database import Database

class Container(DeclarativeContainer):
    
    config = Configuration()
    database = Dependency(instance_of=Database)
    
    sql_alchemy_issue_repository = Factory(
        SqlAlchemyIssueRepository,
        session=database.provided.session_factory,
    )
    postgres_notify_event_publisher = Factory(
        PostgresNotifyEventPublisher,
        session=database.provided.session_factory,
        channel="issue_events",
    )
    create_issue = Factory(
        CreateIssue,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    update_issue_status = Factory(
        UpdateIssueStatus,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    update_issue_metadata = Factory(
        UpdateIssueMetadata,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    add_comment = Factory(
        AddComment,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    link_issue_to_task = Factory(
        LinkIssueToTask,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    unlink_issue_from_task = Factory(
        UnlinkIssueFromTask,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    close_issue = Factory(
        CloseIssue,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=postgres_notify_event_publisher,
    )
    get_issue_details = Factory(
        GetIssueDetails, issue_repository=sql_alchemy_issue_repository
    )
    list_issues = Factory(ListIssues, issue_repository=sql_alchemy_issue_repository)
