from pydantic import BaseModel


class SubmitterDTO(BaseModel):
    name: str
