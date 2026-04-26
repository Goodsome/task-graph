from task_graph.planning.domain.enums import ArchitectureLayer
from task_graph.shared.domain.core.value_object import ValueObject
from typing import Self


class ScopeContext(ValueObject):
    """Value object containing context information related to the task's scope level."""

    bounded_context: str | None = None
    architecture_layer: ArchitectureLayer | None = None
    component_name: str | None = None
    atomic_name: str | None = None

    @classmethod
    def create(
        cls: type[Self],
        bounded_context: str | None = None,
        architecture_layer: ArchitectureLayer | None = None,
        component_name: str | None = None,
    ) -> Self:
        """Factory method to create a new ScopeContext instance."""
        return cls(
            bounded_context=bounded_context,
            architecture_layer=architecture_layer,
            component_name=component_name,
        )