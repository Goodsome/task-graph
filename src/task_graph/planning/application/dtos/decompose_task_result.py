from pydantic import BaseModel, Field


class DecomposeTaskResult(BaseModel):
    """Result of the DecomposeTask use case."""

    success: bool
    task_id: str
    sub_task_ids: list[str] = Field(default_factory=list)
    error: str | None = Field(default=None)
