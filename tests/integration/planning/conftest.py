import pytest
from typing import Generator
from sqlalchemy.orm import Session

# 导入容器和配置
from task_graph.bootstrap import create_container, ApplicationContainer, AppConfig
from task_graph.shared.config import get_settings
from task_graph.shared.infrastructure.orm import Base

# 导入ORM模型确保Base.metadata能扫描到所有表
import task_graph.planning.infrastructure.orm_models


# 1. 准备测试环境的配置
@pytest.fixture(scope="session")
def test_config() -> AppConfig:
    """测试专用配置，使用测试数据库连接。"""
    shared_settings = get_settings()
    test_db_url = shared_settings.test_database_url
    assert test_db_url is not None, "TEST_DATABASE_URL is not set in environment variables"

    # 覆盖共享配置中的database_url为测试数据库地址
    return AppConfig(
        shared={
            "database_url": test_db_url
        }
    )

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