
import sqlglot
from sqlglot import exp


MAX_ROWS = 100


def validate_sql(sql: str) -> str:
    """
    Validate generated SQL.
    Allow only a single SELECT or UNION query.
    Automatically add a maximum row limit.
    """

    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty")

    try:
        statements = sqlglot.parse(sql, read="sqlite")

        # Reject empty or multiple statements
        statements = [stmt for stmt in statements if stmt is not None]

        if len(statements) != 1:
            raise ValueError("Only one SQL statement is allowed.")

        query = statements[0]

        # Allow only SELECT-based queries
        if not isinstance(query, (exp.Select, exp.Union)):
            raise ValueError("Only SELECT queries are allowed.")

        # Add a default limit if one isn't provided
        limit = query.args.get("limit")

        if limit is None:
            query = query.limit(MAX_ROWS)

        # Cap excessively large numeric limits
        else:
            limit_value = limit.expression

            if isinstance(limit_value, exp.Literal) and not limit_value.is_string:
                if int(limit_value.this) > MAX_ROWS:
                    query = query.limit(MAX_ROWS)

        return query.sql(dialect="sqlite")

    except sqlglot.errors.ParseError as e:
        raise ValueError(f"Invalid SQL syntax: {e}") from e
