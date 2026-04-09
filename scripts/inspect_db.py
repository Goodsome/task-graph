import sys
import argparse
from sqlalchemy import create_engine, inspect
from task_graph.shared.config import get_settings

def inspect_database(url: str):
    engine = create_engine(url)
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    if not tables:
        print("No tables found in database.")
        return

    print(f"Database: {url.split('@')[-1]}\n")
    print(f"Found {len(tables)} table(s):\n")

    for table_name in tables:
        print(f"{'=' * 60}")
        print(f"Table: {table_name}")
        print(f"{'=' * 60}")

        columns = inspector.get_columns(table_name)
        for col in columns:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col["default"] else ""
            print(f"  {col['name']:<30} {str(col['type']):<20} {nullable} {default}")

        pk = inspector.get_pk_constraint(table_name)
        if pk and pk["constrained_columns"]:
            print(f"\n  Primary Key: {', '.join(pk['constrained_columns'])}")

        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            print(f"  Foreign Key: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        print()

    engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Inspect database tables and columns")
    parser.add_argument("--test", action="store_true", help="Use TEST_DATABASE_URL instead of DATABASE_URL")
    args = parser.parse_args()

    settings = get_settings()

    db_url = settings.test_database_url if args.test else settings.database_url
    if not db_url:
        env_var = "TEST_DATABASE_URL" if args.test else "DATABASE_URL"
        print(f"{env_var} is not set in environment variables or .env file.")
        sys.exit(1)

    inspect_database(str(db_url))


if __name__ == "__main__":
    main()
