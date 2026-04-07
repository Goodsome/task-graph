from task_graph.planning.domain.enums import RecurrenceType
from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject


class RecurrencePolicy(ValueObject):
    """Rules for creating a successor task upon completion."""

    type: RecurrenceType
    max_repetitions: int = Field(default_factory=int)
    current_iteration: int

    def next_iteration(
        self,
    ) -> "RecurrencePolicy": ...
