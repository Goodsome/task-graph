import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 2. 强制加载 .env.test 文件，并覆盖现有的环境变量
# 注意：这一步必须放在所有 from task_graph... import 之前！
test_env_path = PROJECT_ROOT / ".env.test"
load_dotenv(dotenv_path=test_env_path, override=True)

import pytest
from typing import Generator
from sqlalchemy.orm import Session

# 导入容器和配置
from task_graph.bootstrap import create_container, ApplicationContainer, AppConfig, load_all_configurations
from task_graph.shared.config import get_settings
from task_graph.shared.infrastructure.orm import Base

# 1. 准备测试环境的配置
@pytest.fixture(scope="session")
def test_config() -> AppConfig:
    """测试专用配置，使用测试数据库连接。"""
    config = load_all_configurations()
    return config

# 2. 初始化应用容器（Session级别，整个测试过程只创建一次）
@pytest.fixture(scope="session")
def app_container(test_config: AppConfig) -> Generator[ApplicationContainer, None, None]:
    """DI容器实例，使用测试配置。"""
    # 使用工厂创建容器并传入测试配置
    container = create_container(config_override=test_config, init_resources=True)

    # 自动进行依赖注入绑定
    container.wire(packages=[
        "task_graph.planning.interfaces",
        "task_graph.planning.application"
    ])

    yield container

    # 测试结束后清理容器资源
    container.shutdown_resources()

from task_graph.planning.application.ports.unit_of_work import UnitOfWork

# 3. 数据库表结构初始化（基于容器中的Engine）
@pytest.fixture(scope="session")
def db_schema(app_container: ApplicationContainer) -> Generator[None, None, None]:
    """管理数据库表生命周期：测试开始前建表，结束后删表。"""
    database = app_container.shared.database()
    engine = database.engine

    # 创建所有表
    Base.metadata.create_all(engine)

    yield

    # 销毁所有表
    Base.metadata.drop_all(engine)

# 4. 提供给每个测试用例的干净Session（Function级别）
@pytest.fixture(scope="function")
def db_session(app_container: ApplicationContainer, db_schema: None) -> Generator[Session, None, None]:
    """
    提供事务隔离的数据库Session。
    测试结束后自动回滚，确保测试用例之间互不干扰，即使测试显式调用commit()。
    """
    database = app_container.shared.database()
    connection = database.engine.connect()
    # 开启嵌套事务保证完全隔离
    transaction = connection.begin()

    # 绑定session到这个特定的connection
    session = Session(bind=connection)

    yield session

    # 测试结束后强制回滚所有写入
    session.close()
    transaction.rollback()
    connection.close()

# 5. 便捷获取UnitOfWork的fixture
@pytest.fixture(scope="function")
def unit_of_work(app_container: ApplicationContainer, db_session: Session) -> UnitOfWork:
    """直接从容器中获取UnitOfWork实例，方便业务逻辑测试。"""
    return app_container.planning.unit_of_work()