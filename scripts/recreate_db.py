import sys
import argparse
import logging
from task_graph.bootstrap import create_container
from task_graph.shared.infrastructure.orm import Base

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_recreate")


def drop_all_tables(database):
    """Drop all existing tables in the database."""
    logger.info("Dropping all existing tables...")
    Base.metadata.drop_all(bind=database._engine)
    logger.info("All tables dropped successfully.")


def main():
    parser = argparse.ArgumentParser(description="Drop and recreate database tables")
    args = parser.parse_args()

    try:
        container = create_container(init_resources=True)
        db = container.shared.database()
        drop_all_tables(db)

        logger.info("Creating database tables...")
        db.init_db()
        logger.info("Database recreation completed successfully.")

    except Exception as e:
        logger.error(f"Recreation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
