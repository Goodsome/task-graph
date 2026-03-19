from __future__ import annotations
from pydantic import Field
from task_graph.shared.models import ValueObject
from typing import Self, Union


class Submitter(ValueObject):
    """Information about the issue submitter"""

    name: str
    email: str
    external_id: str | None = Field(default=None)

    def create(self, name: str, email: str, external_id: str | None = None) -> Self: ...

    def validate_email(self, email: str) -> str: ...
