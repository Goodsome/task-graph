from pydantic import BaseModel, Field


class ModifyTaskDependenciesCommand(BaseModel):
    task_id: str
    added_dependencies: list[str] = Field(default_factory=list)
    removed_dependencies: list[str] = Field(default_factory=list)
