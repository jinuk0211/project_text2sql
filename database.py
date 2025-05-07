
engine = create_engine('sqlite:///../Chinook.db')

# table names
inspector = inspect(engine)
table_names = inspector.get_table_names()
print("table_names:\n", table_names)

# simple query
# with Session(engine) as session:
#     result = session.execute(text("SELECT * FROM Artist LIMIT 10"))
#     print("\nrows:")
#     for row in result:
#         print(row)
# INSERT 구문 작성 및 실행
with engine.connect() as conn:
    stmt = insert(artists).values(Name="New Artist Name")
    conn.execute(stmt)
    conn.commit()


import pandas as pd
from typing import List

def query_executor(query: str, output_columns: List[str]):
    engine = create_engine(uri)

    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))

            if result.returns_rows:
                df = pd.DataFrame(result.fetchall(), columns=output_columns)
                return df.to_csv(index=False)
            else:
                return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    finally:
        engine.dispose()

query = """SELECT 
    c."Country",
    COUNT(DISTINCT c."CustomerId") as "CustomerCount",
    ROUND(AVG(i."Total"), 2) as "AverageTotal"
FROM Customer c
LEFT JOIN Invoice i ON c."CustomerId" = i."CustomerId"
GROUP BY c."Country"
HAVING COUNT(DISTINCT c."CustomerId") > 5
ORDER BY "AverageTotal" DESC;"""

output_columns = ["Country", "CustomerCount", "AverageTotal"]
response = query_executor(query, output_columns)

print(response)