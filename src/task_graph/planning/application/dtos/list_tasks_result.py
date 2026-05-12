from pydantic import BaseModel, Field
from task_graph.planning.application.dtos.summary_task import SummaryTask


class ListTasksResult(BaseModel):
    tasks: list[SummaryTask]
    total_count: int
    total_pages: int
    current_page: int
    error: str | None = Field(default=None)
