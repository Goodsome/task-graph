from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration
from task_graph.shared.infrastructure.database import Database


class SharedContainer(DeclarativeContainer):
    """Shared DI container for cross-cutting concerns."""

    # Use Dependency Injector native Configuration provider
    config = Configuration()

    # Shared infrastructure
    database = Singleton(
        Database,
        connection_string=config.DATABASE_URL.as_(str),
    )
