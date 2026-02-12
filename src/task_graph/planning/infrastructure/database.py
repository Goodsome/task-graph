from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from task_graph.planning.infrastructure.orm import Base
from task_graph.planning.config import get_settings
import logging

class Database:
    """
    Database connection handling using SQLAlchemy.
    """
    def __init__(self, connection_string: str) -> None:
        self._engine: Engine = create_engine(
            connection_string,
            pool_pre_ping=True
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
