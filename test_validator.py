
from sql_validator import validate_sql

test_queries = [
    "SELECT * FROM Customer",
    "DELETE FROM Customer",
    "UPDATE Customer SET FirstName = 'Test'",
    "DROP TABLE Customer",
    "SELECT * FROM Track LIMIT 1000",
    "SELECT * FROM Customer; DELETE FROM Customer;"
]

for query in test_queries:
    print("\nOriginal query:", query)

    try:
        validated = validate_sql(query)
        print("ACCEPTED:", validated)

    except ValueError as e:
        print("BLOCKED:", e)
