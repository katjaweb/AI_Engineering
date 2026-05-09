import os
import urllib.request
from pydantic import BaseModel

import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
PARQUET_FILE = "yellow_tripdata_2024-01.parquet"

def get_connection():
    return duckdb.connect("taxi.db")


def setup_database():
    con = get_connection()

    if not os.path.exists(PARQUET_FILE):
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con.execute(f"""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM '{PARQUET_FILE}'
    """)

    count = con.execute("SELECT COUNT(*) FROM trips").fetchone()[0]

    con.close()

    print(f"Loaded {count} rows")
    return count


class SQLResult(BaseModel):
   sql_query: str
   result_text: str
   row_count: int


class SQLTools:
    def __init__(self, connection: duckdb.DuckDBPyConnection):
        self.con = connection

    def get_schema(self) -> str:
        """
        Return schema information for the trips table.
        """
        result = self.con.execute("DESCRIBE trips").fetchall()

        lines = ["Column Name | Type", "-" * 40]

        for row in result:
            column_name = row[0]
            column_type = row[1]
            lines.append(f"{column_name} | {column_type}")

        return "\n".join(lines)

    def run_sql(self, query: str) -> SQLResult:
        """
        Execute a SQL query and return formatted text output.
        Limits results to 50 rows.
        """
        try:
            # Wrap user query with LIMIT 50 if not already present
            limited_query = f"""
                SELECT * FROM (
                    {query}
                ) LIMIT 50
            """

            result = self.con.execute(limited_query)

            rows = result.fetchall()
            columns = [desc[0] for desc in result.description]

            lines = [" | ".join(columns)]
            lines.append("-" * 80)

            for row in rows:
                lines.append(" | ".join(str(v) for v in row))

            if not rows:
                lines.append("(no rows returned)")

            return SQLResult(
                sql_query=query,
                result_text="\n".join(lines),
                row_count=len(rows)
            )

        except Exception as e:
            return SQLResult(
                sql_query=query,
                result_text=f"SQL Error: {e}",
                row_count=0
            )
