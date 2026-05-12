from pydantic import BaseModel, Field


class ModifyTaskDependenciesResult(BaseModel):
    success: bool
    error: str = Field(default_factory=str)
