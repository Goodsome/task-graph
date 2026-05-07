from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from task_graph.shared.domain.core.aggregate_root import AggregateRoot


@dataclass
class Repository[T_AR: AggregateRoot, T_ID](ABC):
    
    _seens: set[T_AR] = field(default_factory=set, init=False)

    def collect_seens(self) -> set[T_AR]:
        return self._seens

    def add(self, aggregate: T_AR) -> None:
        self._add(aggregate=aggregate)
        self._seens.add(aggregate)
        
    def get(self, id: T_ID) -> T_AR:
        a = self._get(id)
        self._seens.add(a)
        return a

    def save(self, aggregate: T_AR) -> None:
        self._save(aggregate=aggregate)
        self._seens.add(aggregate)

    @abstractmethod
    def _add(self, aggregate: T_AR) -> None: ...

    @abstractmethod
    def _get(self, id: T_ID) -> T_AR: ...
    
    @abstractmethod
    def _save(self, aggregate: T_AR) -> None: ...
    