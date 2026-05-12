from task_graph.planning.domain.aggregates.task import Task
from pydantic import BaseModel


class SuggestNextActionResult(BaseModel):
    tasks: list[Task]
