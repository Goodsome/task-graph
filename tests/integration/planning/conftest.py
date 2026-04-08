import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from task_graph.planning.infrastructure.orm import Base
from task_graph.planning.config import get_settings

# 1. Session 级别的 Engine Fixture：每次运行 pytest 只创建一次表
@pytest.fixture(scope="session")
def db_engine():
    settings = get_settings()

    db_url = settings.TEST_DATABASE_URL
    assert db_url is not None, "TEST_DATABASE_URL is not set in environment variables"
    # 这里可以是 SQLite 内存库，也可以是你的专属测试库连接字符串
    engine = create_engine(str(db_url))
    
    # 创建所有表结构
    Base.metadata.create_all(engine)
    yield engine
    # 测试全部结束后销毁表
    Base.metadata.drop_all(engine)

# 2. Function 级别的 Session Fixture：每个测试用例都会拿到一个干净、隔离的 session
@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    提供一个事务隔离的数据库 Session。
    测试函数中的所有写入操作最终都会被回滚，确保测试之间绝对隔离。
    """
    connection = db_engine.connect()
    # 开启一个嵌套事务
    transaction = connection.begin()
    
    # 绑定 session 到这个特定的 connection
    session = Session(bind=connection)
    
    yield session  # 将 session 注入给你的 sqlalchemy_repo fixture
    
    # 测试结束后的清理工作：强制回滚，丢弃所有由测试产生的写入
    session.close()
    transaction.rollback()
    connection.close()