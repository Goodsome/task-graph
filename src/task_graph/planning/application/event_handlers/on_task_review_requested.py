from dataclasses import dataclass

from task_graph.planning.domain.events import TaskReviewRequested
from event_hub import EventHub, integration_events as ie
import logging

logger = logging.getLogger(__name__)

@dataclass
class OnTaskReviewRequested:

    event_hub: EventHub

    def handle_publish_integration_event(self, event: TaskReviewRequested):
        e = ie.TaskReviewRequested(
            task_id=event.task_id,
            project_id=event.project_id,
            scope_level=event.scope_level.value,
            bounded_context=event.bounded_context,
            architecture_layer=event.architecture_layer.value if event.architecture_layer else None,
            parent_id=event.parent_id
        )
        self.event_hub.publish_integration_sync(e)
