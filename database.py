from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
# engine = create_engine('sqlite:///../Chinook.db')


def import_buildings_from_file(db_path: str, txt_path: str, limit: int = None) -> None:
    
    # Create database engine
    engine = create_engine(f"sqlite:///{db_path}")

    # Ensure the `buildings` table exists
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT,
                pnu TEXT,
                area REAL
            )
            """
        ))

    # Compile regex pattern once
    pattern = re.compile(r"주소: (.*?), PNU: (\d+), 면적: ([\d.]+)")

    # Open and parse the text file
    with open(txt_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit: # limit 번 줄까지 insert
                break
            line = line.strip()
            if not line:
                continue

            matches = pattern.findall(line)
            if not matches:
                continue

            # Insert all matched entries for this line
            with engine.begin() as conn:
                for address, pnu, area in matches:
                    conn.execute(
                        text(
                            """
                            INSERT INTO buildings (address, pnu, area)
                            VALUES (:address, :pnu, :area)
                            """
                        ),
                        {"address": address.strip(), "pnu": pnu.strip(), "area": float(area)}
                    )
# import_buildings_from_file(db_path="/content/building.db",txt_path="/content/daegu.txt",limit=10)



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