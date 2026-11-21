
import sqlite3
from pathlib import Path
from sql_validator import validate_sql

DB_PATH = Path(__file__).parent / "data" / "Chinook.db"


def get_connection():
    """Create a read-only connection to the database."""

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    connection = sqlite3.connect(
        f"file:{DB_PATH.resolve().as_posix()}?mode=ro",
        uri=True
    )

    connection.row_factory = sqlite3.Row
    return connection


def get_schema():
    """Extract tables, columns, primary keys and foreign keys."""

    connection = get_connection()
    schema = {}

    try:
        cursor = connection.cursor()

        tables = cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        for table in tables:
            table_name = table["name"]

            columns = cursor.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            foreign_keys = cursor.execute(
                f'PRAGMA foreign_key_list("{table_name}")'
            ).fetchall()

            schema[table_name] = {
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "primary_key": bool(col["pk"])
                    }
                    for col in columns
                ],
                "foreign_keys": [
                    {
                        "column": fk["from"],
                        "references_table": fk["table"],
                        "references_column": fk["to"]
                    }
                    for fk in foreign_keys
                ]
            }

    finally:
        connection.close()

    return schema


def format_schema(schema):
    """Convert schema metadata into readable text for the LLM."""

    lines = []

    for table_name, details in schema.items():
        lines.append(f"\nTable: {table_name}")

        for column in details["columns"]:
            pk = " PRIMARY KEY" if column["primary_key"] else ""
            lines.append(
                f"  - {column['name']} ({column['type']}){pk}"
            )

        for fk in details["foreign_keys"]:
            lines.append(
                f"  - FOREIGN KEY: {fk['column']} -> "
                f"{fk['references_table']}.{fk['references_column']}"
            )

    return "\n".join(lines)


def execute_query(sql: str):
    """Validate and safely execute a read-only SQL query."""

    # Validate before touching the database
    safe_sql = validate_sql(sql)

    connection = get_connection()

    try:
        cursor = connection.execute(safe_sql)
        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()


if __name__ == "__main__":
    schema = get_schema()
    print(format_schema(schema))
