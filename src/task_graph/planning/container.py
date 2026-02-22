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
from task_graph.planning.infrastructure.repositories.yaml_task_repository import YamlTaskRepository
from task_graph.planning.infrastructure.repositories.sql_alchemy_task_repository import SqlAlchemyTaskRepository
from task_graph.planning.infrastructure.database import Database
from task_graph.planning.config import get_settings


class PlanningContainer(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Planning Context.
    """

    # --- Configuration ---
    config = providers.Configuration()

    # --- Infrastructure Layer ---

    _settings_obj = get_settings()

    if _settings_obj.DATABASE_URL:
        # Database connection
        database = providers.Singleton(
            Database,
            connection_string=str(_settings_obj.DATABASE_URL)
        )
        
        # Determine actual implementation based on config
        task_repository = providers.Singleton(
            SqlAlchemyTaskRepository,
            session_factory=database.provided.session_factory
        )
    else:
        # Fallback to YAML implementation
        task_repository = providers.Singleton(
            YamlTaskRepository,
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
        repository=task_repository
    )

    modify_task_dependencies = providers.Factory(
        ModifyTaskDependencies,
        repository=task_repository,
        cycle_detector=cycle_detection_service,
        dependency_resolver=dependency_resolution_service
    )

    revise_task_details = providers.Factory(
        ReviseTaskDetails,
        repository=task_repository
    )

    update_task_status = providers.Factory(
        UpdateTaskStatus,
        repository=task_repository,
        resolution_service=dependency_resolution_service
    )

    suggest_next_action = providers.Factory(
        SuggestNextAction,
        repository=task_repository,
        priority_service=priority_analysis_service
    )

    list_tasks = providers.Factory(
        ListTasks,
        repository=task_repository
    )
    
    get_task_details = providers.Factory(
        GetTaskDetails,
        repository=task_repository
    )

    delete_task = providers.Factory(
        DeleteTask,
        repository=task_repository
    )

    submit_task_result = providers.Factory(
        SubmitTaskResult,
        repository=task_repository
    )

    claim_task = providers.Factory(
        ClaimTask,
        repository=task_repository,
        dependency_service=dependency_resolution_service
    )

    review_task = providers.Factory(
        ReviewTask,
        repository=task_repository,
        resolution_service=dependency_resolution_service
    )

