from event_hub import EventHub

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration, Factory, Resource, Callable
from task_graph.shared.infrastructure.database import Database, init_database
from task_graph.shared.infrastructure.event_hub_adapter import EventHubAdapter


class Container(DeclarativeContainer):
    """Shared kernel DI container for cross-cutting concerns."""

    # Use Dependency Injector native Configuration provider
    config = Configuration()

    # Shared infrastructure
    database = Resource(
        init_database,
        connection_string=config.database_url.as_(str),
    )

    event_hub: Singleton[EventHub] = Singleton(EventHub)
    
    event_bus_factory: Callable = Callable(EventHubAdapter.build_factory, hub=event_hub)

