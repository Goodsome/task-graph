from pydantic import BaseModel, Field


class ReviseTaskDetailsCommand(BaseModel):
    task_id: str
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    effort: int | None = Field(default=None)
    base_value: float | None = Field(default=None)
