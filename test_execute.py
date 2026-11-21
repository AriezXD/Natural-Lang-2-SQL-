
from database import execute_query

sql = """
SELECT
    c.CustomerId,
    c.FirstName,
    c.LastName,
    SUM(i.Total) AS TotalSpending
FROM Customer AS c
JOIN Invoice AS i
    ON c.CustomerId = i.CustomerId
GROUP BY
    c.CustomerId,
    c.FirstName,
    c.LastName
ORDER BY TotalSpending DESC
LIMIT 5;
"""

try:
    results = execute_query(sql)

    print("\nTop 5 Customers by Spending:\n")

    for row in results:
        print(row)

except Exception as e:
    print(f"Execution failed: {e}")
