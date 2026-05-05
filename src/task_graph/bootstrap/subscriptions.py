import logging

from event_hub import EventHub

from typing import cast
from task_graph.planning.domain.events import TaskChangesRequested, TaskCompleted, TaskDecomposing, TaskReady, TaskReviewRequested
from .container import ApplicationContainer

logger = logging.getLogger(__name__)

def bind_all_events(container: ApplicationContainer) -> None:
    """集中绑定系统中的所有事件订阅关系"""

    event_hub: EventHub = cast(EventHub, container.shared.event_hub()) 

    event_hub.register_domain(
        TaskCompleted,
        container.planning.on_task_completed().handle_complete_decomposition
    )

    event_hub.register_domain(
        TaskCompleted,
        container.planning.on_task_completed().handle_unlock_task
    )

    event_hub.register_domain(
        TaskDecomposing,
        container.planning.on_task_decomposing().handle_decompose_task
    )

    event_hub.register_domain(
        TaskReady,
        container.planning.on_task_ready().handle_publish_integration_event
    )

    event_hub.register_domain(
        TaskReviewRequested,
        container.planning.on_task_review_requested().handle_publish_integration_event
    )

    event_hub.register_domain(
        TaskChangesRequested,
        container.planning.on_task_changes_requested().handle_publish_integration_event
    )


