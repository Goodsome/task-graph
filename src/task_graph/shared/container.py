from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration, Factory, Resource
from task_graph.shared.infrastructure.database import Database, init_database
from task_graph.shared.infrastructure.event_bus import PgNotifyEventBus


class Container(DeclarativeContainer):
    """Shared kernel DI container for cross-cutting concerns."""

    # Use Dependency Injector native Configuration provider
    config = Configuration()

    # Shared infrastructure
    database = Resource(
        init_database,
        connection_string=config.database_url.as_(str),
    )

    # Shared event bus factory
    event_bus_factory = Factory(PgNotifyEventBus)
