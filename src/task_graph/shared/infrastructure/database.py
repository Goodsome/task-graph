from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from task_graph.shared.infrastructure.orm import Base
import logging

class Database:
    """
    Database connection handling using SQLAlchemy.
    """
    def __init__(self, connection_string: str) -> None:
        self._engine: Engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            echo=True,
        )
        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False
        )
    
    def get_session(self) -> Session:
        """Create a new database session."""
        return self._session_factory()
    
    def close(self) -> None:
        """Close the database connection pool."""
        self._engine.dispose()
    
    def init_db(self) -> None:
        """Create database tables if they don't exist."""
        try:
            Base.metadata.create_all(self._engine)
            logging.info("Database tables created successfully.")
        except Exception as e:
            logging.error(f"Failed to create database tables: {e}")
            raise e

    @property
    def session_factory(self) -> sessionmaker[Session]:
        return self._session_factory

    @property
    def engine(self) -> Engine:
        """Get the underlying SQLAlchemy engine."""
        return self._engine


def init_database(connection_string: str) -> Iterator[Database]:
    """数据库资源的生命周期管理"""
    # 1. 实例化 Database 对象
    db = Database(connection_string)
    
    # 2. 启动时的初始化逻辑 (对应 init_resources)
    try:
        # 可选：显式连一下数据库测试连通性，做到 Fail-Fast
        with db.engine.connect() as conn:
            pass 
            
        # 调用你的建表逻辑（如果你的项目不使用 Alembic 等迁移工具的话）
        db.init_db()
        logging.info("Database initialized and connected successfully.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise e

    # 3. 将准备就绪的数据库实例 yield 给容器
    yield db

    # 4. 关闭时的清理逻辑 (对应 shutdown_resources)
    logging.info("Closing database connection pool...")
    db.close()