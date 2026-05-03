"""
应用程序启动工厂：负责配置加载、容器实例化和资源初始化。
遵循组合根模式：在程序入口点一次性完成所有组装工作。
"""
from typing import Optional
from .container import ApplicationContainer
from .config import load_all_configurations, AppConfig
from .subscriptions import bind_all_events



def create_container(
    config_override: Optional[AppConfig] = None,
    init_resources: bool = True
) -> ApplicationContainer:
    """
    创建并配置应用程序DI容器。

    Args:
        config_override: 可选的自定义配置，用于测试或特殊启动场景
        init_resources: 是否自动初始化数据库等外部资源

    Returns:
        已完成配置的ApplicationContainer实例
    """
    # 1. 创建干净的容器实例
    container = ApplicationContainer()

    # 2. 加载配置（优先使用传入的覆盖配置）
    app_config = config_override if config_override is not None else load_all_configurations()

    # 3. 将配置字典灌入顶层配置树
    # Dependency Injector自动将配置分层传递给所有子容器
    container.config.from_pydantic(app_config)
    
    bind_all_events(container)

    # 4. 初始化需要建立连接的资源（数据库连接池、事件总线等）
    if init_resources:
        container.init_resources()

    
    return container


__all__ = ["create_container"]
