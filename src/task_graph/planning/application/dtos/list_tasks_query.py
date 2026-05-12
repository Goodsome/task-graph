from pydantic import BaseModel, Field
from task_graph.planning.domain.enums import ScopeLevel, TaskStatus


class ListTasksQuery(BaseModel):
    project_id: str | None = Field(default=None)
    page: int = Field(default=1)
    page_size: int = Field(default=10)
    status: TaskStatus | None = Field(default=None)
    scope_level: ScopeLevel | None = Field(default=None)
    search: str | None = Field(default="")
