import logging

from event_hub import EventHub

from task_graph.planning.domain.events import TaskCompleted
from .container import ApplicationContainer

logger = logging.getLogger(__name__)

def bind_all_events(container: ApplicationContainer) -> None:
    """集中绑定系统中的所有事件订阅关系"""

    event_hub: EventHub = container.shared.event_hub() 

    event_hub.register_domain(
        TaskCompleted,
        container.planning.on_task_completed().handle_complete_decomposition
    )

    event_hub.register_domain(
        TaskCompleted,
        container.planning.on_task_completed().handle_unlock_task
    )

