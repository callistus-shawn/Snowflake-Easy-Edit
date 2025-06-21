import pandas as pd
import snowflake.connector
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeTableEditor:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect_to_snowflake(self, database: str, schema: str) -> bool:
        try:
            self.conn = snowflake.connector.connect(
                user="your_username",
                password="your_password",
                account="your_acc",
                warehouse="your_wh",
                database=database,
                schema=schema
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            return False

    def get_tables(self) -> List[str]:
        try:
            self.cursor.execute("SHOW TABLES")
            return [row[1] for row in self.cursor.fetchall()]
        except Exception:
            return []

    def get_table_columns(self, table_name: str) -> List[Dict]:
        try:
            self.cursor.execute(f"DESCRIBE TABLE {table_name}")
            return [{
                'name': row[0],
                'type': row[1],
                'nullable': row[2] == 'Y',
                'primary_key': row[5] == 'Y' if len(row) > 5 else False
            } for row in self.cursor.fetchall()]
        except Exception:
            return []

    def load_table_data(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(self.cursor.fetchall(), columns=columns)
        except Exception:
            return pd.DataFrame()

    def update_record(self, table_name: str, primary_key_col: str,
                      primary_key_value: Any, column_name: str, new_value: Any) -> bool:
        try:
            value_str = "NULL" if pd.isna(new_value) else f"'{new_value}'" if isinstance(new_value, str) else str(new_value)
            pk_value_str = f"'{primary_key_value}'" if isinstance(primary_key_value, str) else str(primary_key_value)

            query = f"""
            UPDATE {table_name} 
            SET {column_name} = {value_str} 
            WHERE {primary_key_col} = {pk_value_str}
            """
            logger.info(f"Executing query: {query}")
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception:
            return False

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
