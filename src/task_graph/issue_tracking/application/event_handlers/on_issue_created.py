from dataclasses import dataclass

from event_hub import EventHub, integration_events as ie
from task_graph.issue_tracking.domain.events import IssueCreated
import logging

logger = logging.getLogger(__name__)


@dataclass
class OnIssueCreated:

    event_hub: EventHub

    def handle_publish_integration_event(self, event: IssueCreated):
        e = ie.IssueCreated(
            issue_id=event.issue_id,
            project_id=event.project_id,
            title=event.title,
            type=event.type.value,
            severity=event.severity.value,
            submitter_name=event.submitter_name,
        )
        self.event_hub.publish_integration_sync(e)
