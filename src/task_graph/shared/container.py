import asyncio
from collections.abc import Iterator
from event_hub import EventHub, RedisStreamPublisher

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Resource, Callable
from task_graph.shared.infrastructure.database import Database, init_database
from task_graph.shared.infrastructure.event_hub_adapter import EventHubAdapter

def init_event_hub() -> Iterator[EventHub]:
    publisher=RedisStreamPublisher()
    hub = EventHub(
        publisher=publisher,
    )
    asyncio.run(hub.start())

    yield hub

    try:
        asyncio.run(hub.stop())
    except RuntimeError:
        # Event loop may already be closing during process shutdown
        pass
    

class Container(DeclarativeContainer):
    """Shared kernel DI container for cross-cutting concerns."""

    # Use Dependency Injector native Configuration provider
    config: Configuration = Configuration()

    # Shared infrastructure
    database: Resource[Database] = Resource(
        init_database,
        connection_string=config.database_url.as_(str),
    )

    event_hub: Resource[EventHub] = Resource(init_event_hub)
    
    event_publisher_factory: Callable = Callable(EventHubAdapter.build_factory, hub=event_hub)

