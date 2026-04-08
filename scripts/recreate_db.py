import sys
import argparse
import logging
from sqlalchemy import text, create_engine
from task_graph.planning.config import get_settings
from task_graph.planning.infrastructure.database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_recreate")


def drop_all_tables(database: Database):
    """Drop all existing tables in the database."""
    from task_graph.planning.infrastructure.orm import Base

    logger.info("Dropping all existing tables...")
    Base.metadata.drop_all(bind=database._engine)
    logger.info("All tables dropped successfully.")


def main():
    parser = argparse.ArgumentParser(description="Drop and recreate database tables")
    parser.add_argument("--test", action="store_true", help="Use TEST_DATABASE_URL instead of DATABASE_URL")
    args = parser.parse_args()

    settings = get_settings()

    db_url = settings.TEST_DATABASE_URL if args.test else settings.DATABASE_URL
    if not db_url:
        env_var = "TEST_DATABASE_URL" if args.test else "DATABASE_URL"
        logger.error(f"{env_var} is not set in environment variables or .env file.")
        sys.exit(1)

    logger.info(f"Recreating database tables at {str(db_url).split('@')[-1]}")

    try:
        db = Database(str(db_url))

        drop_all_tables(db)

        logger.info("Creating database tables...")
        db.init_db()
        logger.info("Database recreation completed successfully.")

    except Exception as e:
        logger.error(f"Recreation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
