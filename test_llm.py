
from llm import generate_sql
from database import execute_query

question = "Show me the top 5 customers by total spending"

sql = generate_sql(question)

print("\nGenerated SQL:")
print(sql)

print("\nExecuting query...")

try:
    results = execute_query(sql)

    for row in results:
        print(row)

except Exception as e:
    print("Execution failed:", e)
