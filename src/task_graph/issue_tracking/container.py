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
from dependency_injector.providers import Factory, Callable
from task_graph.issue_tracking.application.use_cases.create_issue import CreateIssue
from dependency_injector.containers import DeclarativeContainer
from task_graph.shared.infrastructure.event_bus import PgNotifyEventBus
from task_graph.issue_tracking.infrastructure.repositories.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)

from task_graph.shared.infrastructure.database import Database

class Container(DeclarativeContainer):
    
    config = Configuration()
    database = Dependency(instance_of=Database)
    event_bus_factory = Dependency()
    
    sql_alchemy_issue_repository = Factory(
        SqlAlchemyIssueRepository,
        session=Factory(database.provided.session_factory),
    )
    pg_notify_event_bus = Factory(
        PgNotifyEventBus,
        session=Factory(database.provided.session_factory),
        channel="issue_events",
    )

    # Unit of Work
    issue_repository_factory = Factory(
        SqlAlchemyIssueRepository
    )
    
    unit_of_work = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        event_bus_channel="issue_events",
        issue_repository_factory=issue_repository_factory.provider,
        event_bus_factory=event_bus_factory.provider,
    )
    create_issue = Factory(
        CreateIssue,
        uow=unit_of_work,
    )
    update_issue_status = Factory(
        UpdateIssueStatus,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=pg_notify_event_bus,
    )
    update_issue_metadata = Factory(
        UpdateIssueMetadata,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=pg_notify_event_bus,
    )
    add_comment = Factory(
        AddComment,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=pg_notify_event_bus,
    )
    link_issue_to_task = Factory(
        LinkIssueToTask,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=pg_notify_event_bus,
    )
    unlink_issue_from_task = Factory(
        UnlinkIssueFromTask,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=pg_notify_event_bus,
    )
    close_issue = Factory(
        CloseIssue,
        issue_repository=sql_alchemy_issue_repository,
        event_publisher=pg_notify_event_bus,
    )
    get_issue_details = Factory(
        GetIssueDetails, issue_repository=sql_alchemy_issue_repository
    )
    list_issues = Factory(ListIssues, issue_repository=sql_alchemy_issue_repository)
