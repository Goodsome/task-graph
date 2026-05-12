from pydantic import BaseModel, Field


class SuggestNextActionQuery(BaseModel):
    top_n: int
    project_id: str | None = Field(default=None)
