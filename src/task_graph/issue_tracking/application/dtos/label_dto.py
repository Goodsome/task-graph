from pydantic import BaseModel


class LabelDTO(BaseModel):
    name: str
