from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )



class Entity(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )


class Aggregate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
