import time
import sys
import argparse
import logging
from sqlalchemy import text, create_engine
from task_graph.shared.config import get_settings
from task_graph.shared.infrastructure.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_init")

def create_database_if_not_exists(url: str):
    """Create the target database if it doesn't exist."""
    # Split URL to get the target database name and a base connection URL
    # format: postgresql://user:pass@host:port/dbname
    base_url, db_name = url.rsplit('/', 1)
    # Handle potential query parameters in URL
    if '?' in db_name:
        db_name = db_name.split('?')[0]
    
    # Connect to the default 'postgres' database to perform administrative tasks
    admin_url = f"{base_url}/postgres"
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    try:
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            exists = result.scalar()
            
            if not exists:
                logger.info(f"Database '{db_name}' does not exist. Creating...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
    except Exception as e:
        logger.error(f"Failed to check/create database: {e}")
        # We don't exit here because the target database might actually exist 
        # but we couldn't connect to 'postgres' for some reason
    finally:
        engine.dispose()

def wait_for_db(database: Database, max_retries: int = 10, delay: int = 3):
    """Wait for the database to be ready and accepting connections."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Try to connect and execute a simple query
            with database.get_session() as session:
                session.execute(text("SELECT 1"))
                logger.info("Database is ready.")
                return True
        except Exception as e:
            retry_count += 1
            logger.warning(f"Database not ready (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(delay)
    
    logger.error("Database connection timed out.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Initialize database tables")
    parser.add_argument("--test", action="store_true", help="Use TEST_DATABASE_URL instead of DATABASE_URL")
    args = parser.parse_args()

    settings = get_settings()

    db_url = settings.test_database_url if args.test else settings.database_url
    if not db_url:
        env_var = "TEST_DATABASE_URL" if args.test else "DATABASE_URL"
        logger.error(f"{env_var} is not set in environment variables or .env file.")
        sys.exit(1)

    logger.info(f"Initializing database at {str(db_url).split('@')[-1]}")

    try:
        create_database_if_not_exists(str(db_url))

        db = Database(str(db_url))

        if not wait_for_db(db):
            sys.exit(1)

        logger.info("Creating database tables...")
        db.init_db()
        logger.info("Database initialization completed successfully.")

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
