import logging
from dataclasses import dataclass

# 假设这是你要触发的 Use Case 及其对应的 Command
from task_graph.planning.application.use_cases.get_task_details import (
    GetTaskDetailsQuery,
    GetTaskDetails,
)
from task_graph.planning.domain.events import TaskCreated

logger = logging.getLogger(__name__)


@dataclass
class OnTaskCreatedHandler:
    get_task_details: GetTaskDetails

    def __call__(self, event: TaskCreated):
        logger.info(
            f"Received TaskCreatedEvent for {event.task_id}, triggering subtask creation."
        )

        query = GetTaskDetailsQuery(
            task_id=event.task_id,
        )

        result = self.get_task_details.execute(query)

        if not result.success:
            logger.error(f"Failed to handle event for {event.task_id}: {result.error}")
        
        logger.info(f"Task details: {result.task}")