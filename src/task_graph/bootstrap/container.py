"""
Root DI container for the entire application.
Aggregates all bounded context containers and provides shared dependencies.
纯声明式设计：只描述依赖关系，不包含任何配置数据和实例化逻辑。
"""
from dependency_injector import containers, providers
from task_graph.shared.container import Container as SharedContainer
from task_graph.planning.container import Container as PlanningContainer
from task_graph.issue_tracking.container import Container as IssueTrackingContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Root application container that composes all context containers."""

    # Wiring configuration - add packages where dependencies need to be injected
    wiring_config = containers.WiringConfiguration(
        packages=[
            "task_graph.planning.interfaces",
            "task_graph.issue_tracking.interfaces",
            "task_graph.planning.interfaces.tui",
        ]
    )

    # 顶层全局配置树
    config = providers.Configuration()

    # Shared container - 自动接收顶层配置的 shared 段
    shared: providers.Container[SharedContainer] = providers.Container(
        SharedContainer,
        config=config.shared,
    )

    # Planning bounded context container - 自动接收顶层配置的 planning 段 + 共享依赖
    planning = providers.Container(
        PlanningContainer,
        config=config.planning,
        database=shared.database,
        event_bus_factory=shared.event_bus_factory,
        event_hub=shared.event_hub,
    )

    # Issue Tracking bounded context container
    issue_tracking = providers.Container(
        IssueTrackingContainer,
        config=config.issue_tracking,
        database=shared.database,
        event_bus_factory=shared.event_bus_factory,
    )


__all__ = ["ApplicationContainer"]
