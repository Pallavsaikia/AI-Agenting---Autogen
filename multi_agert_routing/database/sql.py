import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL
from database import SQLConnectionSettings
import time
from sqlalchemy.exc import OperationalError
class SQLFunctions:
    def __init__(self):
        # Fetch the connection settings from SQLConnectionSettings
        host, database, user, password = SQLConnectionSettings.get_config()
        
        # Define the connection string for pyodbc
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={host};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=3600;"
            
        )
        
        # Create a URL object for SQLAlchemy
        connection_url = URL.create(
            "mssql+pyodbc",
            query={"odbc_connect": connection_string}
        )
        
        # Create the SQLAlchemy engine
        self.engine = create_engine(connection_url)
        
    def close_connection(self):
        """Closes the SQLAlchemy engine connection."""
        if self.engine:
            self.engine.dispose()
            print("Database connection closed.")
            
    def fetch_query_data(self, query: str) -> pd.DataFrame:
        """
        Fetches data from the SQL database and returns it as a Pandas DataFrame.
        
        :param query: SQL query string
        :return: Pandas DataFrame with the query result
        """
        with self.engine.connect() as connection:
            return pd.read_sql_query(query, connection)

    def insert_single_row(self, table_name: str, data: dict) -> None:
        """
        Inserts a single row of data into the specified table.
        
        :param table_name: Name of the target table
        :param data: Dictionary of column names and values
        """
        df = pd.DataFrame([data])
        with self.engine.connect() as connection:
            df.to_sql(table_name, con=connection, if_exists='append', index=False, method='multi')

    def insert_bulk_rows(self, table_name: str, data: pd.DataFrame) -> None:
        """
        Inserts multiple rows of data into the specified table in bulk.
        
        :param table_name: Name of the target table
        :param data: Pandas DataFrame containing the data to be inserted
        """
        with self.engine.connect() as connection:
            data.to_sql(table_name, con=connection, if_exists='append', index=False, method='multi')


    def insert_bulk_rows_batch(self, table_name: str, data: pd.DataFrame, batch_size: int = 500, max_retries: int = 3) -> None:
        """
        Inserts multiple rows of data into the specified table in bulk, using batching.
        Includes automatic reconnection and retry logic in case of failure.

        :param table_name: Name of the target table
        :param data: Pandas DataFrame containing the data to be inserted
        :param batch_size: Number of rows per batch (default: 500)
        :param max_retries: Maximum number of retries on failure (default: 3)
        """
        for i in range(0, len(data), batch_size):
            batch = data.iloc[i:i + batch_size]
            retries = 0

            while retries <= max_retries:
                try:
                    with self.engine.connect() as connection:
                        batch.to_sql(table_name, con=connection, if_exists='append', index=False, method='multi')
                    print(f"Inserted batch {i // batch_size + 1}/{(len(data) // batch_size) + 1}")
                    break  # Break the retry loop on success

                except OperationalError as e:
                    retries += 1
                    print(f"Database connection lost. Retry {retries}/{max_retries}... Error: {e}")
                    
                    if retries > max_retries:
                        print("Max retries reached. Could not insert batch.")
                        raise
                    
                    # Exponential backoff before retrying
                    wait_time = 2 ** retries
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)

        print("Bulk insert completed successfully.")

            
    def delete_rows(self, table_name: str, condition: str) -> None:
        """
        Deletes rows from the specified table based on a given condition.
        
        :param table_name: Name of the target table
        :param condition: SQL condition (e.g., "column_name = 'value'")
        """
        query = f"DELETE FROM {table_name} WHERE {condition};"
        print(query)
        with self.engine.connect() as connection:
            with connection.begin():  # Explicit transaction to ensure commit
                result = connection.execute(text(query))
                print(f"Rows deleted: {result.rowcount}")
                
    

