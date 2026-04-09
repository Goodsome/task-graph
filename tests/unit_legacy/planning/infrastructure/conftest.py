import pytest
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker, Session
from task_graph.shared.infrastructure.orm import Base

@compiles(JSONB, "sqlite")
def compile_jsonb(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)

@compiles(UUID, "sqlite")
def compile_uuid(type_, compiler, **kw):
    return "VARCHAR(36)"

@compiles(ARRAY, "sqlite")
def compile_array(type_, compiler, **kw):
    return "JSON"

@pytest.fixture(scope="session")
def engine():
    # Use SQLite in-memory for testing
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """Provides a transactional session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def session_factory(engine, tables):
    """Provides a session factory for the repository."""
    return sessionmaker(bind=engine)
