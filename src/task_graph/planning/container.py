import functools
from dependency_injector import containers
from dependency_injector.providers import Callable, Configuration, Dependency, Factory, Singleton

from task_graph.planning.application.use_cases.claim_task import ClaimTask
from task_graph.planning.application.use_cases.complete_delegated_task import (
    CompleteDelegatedTask,
)
from task_graph.planning.application.use_cases.decompose_task import DecomposeTask

# 3. 导入 Use Cases
from task_graph.planning.application.use_cases.create_task import CreateTask
from task_graph.planning.application.use_cases.delete_task import DeleteTask
from task_graph.planning.application.use_cases.get_task_details import GetTaskDetails
from task_graph.planning.application.use_cases.list_tasks import ListTasks
from task_graph.planning.application.use_cases.modify_task_dependencies import (
    ModifyTaskDependencies,
)
from task_graph.planning.application.use_cases.review_task import ReviewTask
from task_graph.planning.application.use_cases.revise_task_details import (
    ReviseTaskDetails,
)
from task_graph.planning.application.use_cases.submit_task_result import (
    SubmitTaskResult,
)
from task_graph.planning.application.use_cases.suggest_next_action import (
    SuggestNextAction,
)
from task_graph.planning.application.use_cases.unlock_task import UnlockTask
from task_graph.planning.application.use_cases.update_task_status import (
    UpdateTaskStatus,
)
from task_graph.planning.application.event_handlers import (
    OnTaskChangesRequested,
    OnTaskCompleted,
    OnTaskDecomposing,
    OnTaskReady,
    OnTaskReviewRequested,
)


# 2. 导入 Domain Services
from task_graph.planning.domain.services.cycle_detection_service import (
    CycleDetectionService,
)
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.services.priority_analysis_service import (
    PriorityAnalysisService,
)
from task_graph.planning.infrastructure.adapters.sql_alchemy_task_query_service import (
    SqlAlchemyTaskQueryService,
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.infrastructure.adapters.sql_alchemy_task_repository import (
    SqlAlchemyTaskRepository,
)
from task_graph.shared.infrastructure.database import Database
from task_graph.shared.infrastructure.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from event_hub import EventHub


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Planning Context.
    """

    # --- Dependencies injected from parent container ---
    config: Configuration = Configuration()
    database: Dependency[Database] = Dependency(instance_of=Database)
    event_hub: Dependency[EventHub] = Dependency(instance_of=EventHub)
    event_bus_factory = Dependency()

    # --- Infrastructure Factories ---
    task_repository_factory: Factory[SqlAlchemyTaskRepository] = Factory(
        SqlAlchemyTaskRepository
    )

    event_publisher_factory = Callable(
        lambda event_bus_factory, channel: functools.partial(
            event_bus_factory, channel=channel
        ),
        event_bus_factory=event_bus_factory,
        channel=config.event_bus_channel,
    )

    unit_of_work: Factory[SqlAlchemyUnitOfWork[TaskRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=task_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )

    task_query_service: Factory[SqlAlchemyTaskQueryService] = Factory(
        SqlAlchemyTaskQueryService,
        session_factory=database.provided.session_factory,
    )
    # --- Domain Service Layer ---

    cycle_detection_service: Singleton[CycleDetectionService] = Singleton(
        CycleDetectionService
    )

    dependency_resolution_service: Singleton[DependencyResolutionService] = Singleton(
        DependencyResolutionService
    )

    priority_analysis_service: Singleton[PriorityAnalysisService] = Singleton(
        PriorityAnalysisService
    )

    # --- Application Layer (Use Cases) ---

    create_task: Factory[CreateTask] = Factory(CreateTask, uow=unit_of_work)

    modify_task_dependencies: Factory[ModifyTaskDependencies] = Factory(
        ModifyTaskDependencies,
        uow=unit_of_work,
        cycle_detector=cycle_detection_service,
        dependency_resolver=dependency_resolution_service,
    )

    revise_task_details: Factory[ReviseTaskDetails] = Factory(
        ReviseTaskDetails, uow=unit_of_work
    )

    update_task_status: Factory[UpdateTaskStatus] = Factory(
        UpdateTaskStatus,
        uow=unit_of_work,
        resolution_service=dependency_resolution_service,
    )

    unlock_task: Factory[UnlockTask] = Factory(
        UnlockTask,
        uow=unit_of_work,
        resolution_service=dependency_resolution_service,
    )

    suggest_next_action: Factory[SuggestNextAction] = Factory(
        SuggestNextAction, uow=unit_of_work, priority_service=priority_analysis_service
    )

    list_tasks: Factory[ListTasks] = Factory(ListTasks, query_service=task_query_service)

    get_task_details: Factory[GetTaskDetails] = Factory(
        GetTaskDetails, uow=unit_of_work
    )

    delete_task: Factory[DeleteTask] = Factory(DeleteTask, uow=unit_of_work)

    submit_task_result: Factory[SubmitTaskResult] = Factory(
        SubmitTaskResult, uow=unit_of_work
    )

    claim_task: Factory[ClaimTask] = Factory(
        ClaimTask, uow=unit_of_work, dependency_service=dependency_resolution_service
    )

    complete_delegated_task: Factory[CompleteDelegatedTask] = Factory(
        CompleteDelegatedTask, uow=unit_of_work
    )

    decompose_task: Factory[DecomposeTask] = Factory(
        DecomposeTask, uow=unit_of_work
    )

    review_task: Factory[ReviewTask] = Factory(
        ReviewTask, uow=unit_of_work,
    )

    on_task_completed: Factory[OnTaskCompleted] = Factory(
        OnTaskCompleted,
        complete_delegated_task=complete_delegated_task,
        unlock_task=unlock_task,
        task_query_service=task_query_service,
    )

    on_task_decomposing: Factory[OnTaskDecomposing] = Factory(
        OnTaskDecomposing,
        decompose_task=decompose_task,
    )

    on_task_ready: Factory[OnTaskReady] = Factory(
        OnTaskReady,
        event_hub=event_hub,
    )

    on_task_review_requested: Factory[OnTaskReviewRequested] = Factory(
        OnTaskReviewRequested,
        event_hub=event_hub,
    )

    on_task_changes_requested: Factory[OnTaskChangesRequested] = Factory(
        OnTaskChangesRequested,
        event_hub=event_hub,
    )