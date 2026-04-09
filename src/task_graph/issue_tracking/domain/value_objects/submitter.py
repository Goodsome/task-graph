from __future__ import annotations
import re
from pydantic import Field, model_validator
from task_graph.shared.domain.core.value_object import ValueObject
from typing import Self, Any


class Submitter(ValueObject):
    """Information about the issue submitter"""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    external_id: str | None = Field(default=None, max_length=100)

    @classmethod
    def create(cls, name: str, email: str, external_id: str | None = None) -> Self:
        """Create a new Submitter instance"""
        cleaned_name = name.strip()
        cleaned_email = email.strip().lower()

        if not cleaned_name:
            raise ValueError("Submitter name cannot be empty")

        cls.validate_email(cleaned_email)

        return cls(
            name=cleaned_name,
            email=cleaned_email,
            external_id=external_id.strip() if external_id else None
        )

    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email format: {email}")

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, str) and '@' in data:
            # If only email is provided, use email as name
            return {"name": data.split('@')[0], "email": data}
        return data
