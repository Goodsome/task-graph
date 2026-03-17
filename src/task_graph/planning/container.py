from dependency_injector import containers, providers

from task_graph.planning.application.use_cases.claim_task import ClaimTask
# 3. 导入 Use Cases
from task_graph.planning.application.use_cases.create_task import CreateTask
from task_graph.planning.application.use_cases.delete_task import DeleteTask
from task_graph.planning.application.use_cases.get_task_details import GetTaskDetails
from task_graph.planning.application.use_cases.list_tasks import ListTasks
from task_graph.planning.application.use_cases.modify_task_dependencies import ModifyTaskDependencies
from task_graph.planning.application.use_cases.review_task import ReviewTask
from task_graph.planning.application.use_cases.revise_task_details import ReviseTaskDetails
from task_graph.planning.application.use_cases.submit_task_result import SubmitTaskResult
from task_graph.planning.application.use_cases.suggest_next_action import SuggestNextAction
from task_graph.planning.application.use_cases.update_task_status import UpdateTaskStatus
# 2. 导入 Domain Services
from task_graph.planning.domain.services.cycle_detection_service import CycleDetectionService
from task_graph.planning.domain.services.dependency_resolution_service import DependencyResolutionService
from task_graph.planning.domain.services.priority_analysis_service import PriorityAnalysisService
from task_graph.planning.infrastructure.repositories.sql_alchemy_task_repository import SqlAlchemyTaskRepository
from task_graph.planning.application.unit_of_work import SqlAlchemyUnitOfWork
from task_graph.planning.infrastructure.database import Database
from task_graph.planning.config import get_settings


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Planning Context.
    """

    # --- Configuration ---
    config = providers.Configuration()

    # --- Infrastructure Layer ---

    _settings_obj = get_settings()

    # Database connection
    database = providers.Singleton(
        Database,
        connection_string=str(_settings_obj.DATABASE_URL)
    )
    
    unit_of_work = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory
    )
    # --- Domain Service Layer ---

    cycle_detection_service = providers.Factory(
        CycleDetectionService
    )

    dependency_resolution_service = providers.Factory(
        DependencyResolutionService
    )

    priority_analysis_service = providers.Factory(
        PriorityAnalysisService
    )

    # --- Application Layer (Use Cases) ---

    create_task: providers.Factory[CreateTask] = providers.Factory(
        CreateTask,
        uow=unit_of_work
    )

    modify_task_dependencies = providers.Factory(
        ModifyTaskDependencies,
        uow=unit_of_work,
        cycle_detector=cycle_detection_service,
        dependency_resolver=dependency_resolution_service
    )

    revise_task_details = providers.Factory(
        ReviseTaskDetails,
        uow=unit_of_work
    )

    update_task_status = providers.Factory(
        UpdateTaskStatus,
        uow=unit_of_work,
        resolution_service=dependency_resolution_service
    )

    suggest_next_action = providers.Factory(
        SuggestNextAction,
        uow=unit_of_work,
        priority_service=priority_analysis_service
    )

    list_tasks = providers.Factory(
        ListTasks,
        uow=unit_of_work
    )
    
    get_task_details = providers.Factory(
        GetTaskDetails,
        uow=unit_of_work
    )

    delete_task = providers.Factory(
        DeleteTask,
        uow=unit_of_work
    )

    submit_task_result = providers.Factory(
        SubmitTaskResult,
        uow=unit_of_work
    )

    claim_task = providers.Factory(
        ClaimTask,
        uow=unit_of_work,
        dependency_service=dependency_resolution_service
    )

    review_task = providers.Factory(
        ReviewTask,
        uow=unit_of_work,
        resolution_service=dependency_resolution_service
    )

