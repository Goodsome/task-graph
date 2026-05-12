from dependency_injector.providers import Dependency, Configuration, Singleton
from task_graph.issue_tracking.domain.services.issue_status_transition_service import (
    IssueStatusTransitionService,
)

from task_graph.issue_tracking.infrastructure.adapters.sql_alchemy_issue_repository import (
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
from task_graph.issue_tracking.application.event_handlers.on_issue_created import OnIssueCreated
from dependency_injector.containers import DeclarativeContainer
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.shared.infrastructure.database import Database
from task_graph.shared.infrastructure.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    database: Dependency[Database] = Dependency(instance_of=Database)
    event_publisher_factory = Dependency()
    event_hub = Dependency()

    # Unit of Work
    issue_repository_factory: Factory[SqlAlchemyIssueRepository] = Factory(
        SqlAlchemyIssueRepository
    )

    unit_of_work: Factory[SqlAlchemyUnitOfWork[IssueRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=issue_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )
    create_issue: Factory[CreateIssue] = Factory(
        CreateIssue,
        uow=unit_of_work,
    )
    # Status transition service
    issue_status_transition_service: Singleton[IssueStatusTransitionService] = Singleton(
        IssueStatusTransitionService
    )

    update_issue_status: Factory[UpdateIssueStatus] = Factory(
        UpdateIssueStatus,
        uow=unit_of_work,
        status_transition_service=issue_status_transition_service,
    )
    update_issue_metadata: Factory[UpdateIssueMetadata] = Factory(
        UpdateIssueMetadata,
        uow=unit_of_work,
    )
    add_comment: Factory[AddComment] = Factory(
        AddComment,
        uow=unit_of_work,
    )
    link_issue_to_task: Factory[LinkIssueToTask] = Factory(
        LinkIssueToTask,
        uow=unit_of_work,
    )
    unlink_issue_from_task: Factory[UnlinkIssueFromTask] = Factory(
        UnlinkIssueFromTask,
        uow=unit_of_work,
    )
    close_issue: Factory[CloseIssue] = Factory(
        CloseIssue,
        uow=unit_of_work,
    )
    get_issue_details: Factory[GetIssueDetails] = Factory(
        GetIssueDetails, uow=unit_of_work
    )
    list_issues: Factory[ListIssues] = Factory(ListIssues, uow=unit_of_work)

    # Event Handlers
    on_issue_created: Factory[OnIssueCreated] = Factory(
        OnIssueCreated,
        event_hub=event_hub,
    )
