from typing import Dict, List, Tuple, Optional, Any

from ..common import IndexType
from ..common.record_types import RecordType
from ..common.repository import Repository
from ..common.retry_decorator import RetryDecorator
from ..common.config_manager import ConfigManager
from .mysql_query_executor import MySQLQueryExecutor
from .mysql_index_manager import MySQLIndexManager
from .mysql_connection import MySQLConnection
from ..utils.logging_config import ProgressLogger


class MySQLUserRepository(Repository):
    def __init__(
            self,
            table_name: str,
            query_executor: Optional[MySQLQueryExecutor] = None,
            config_manager: Optional[ConfigManager] = None
    ):
        self.config_manager = config_manager or ConfigManager()
        self._query_executor = query_executor or MySQLQueryExecutor(config_manager=self.config_manager)
        self._index_manager = MySQLIndexManager(self._query_executor)
        self.db = MySQLConnection(config_manager=self.config_manager)
        self.cursor = self.db.get_cursor()
        self.table_name = table_name
        self._ensure_table_exists()

    def setup_profiling(self) -> None:
        try:
            self.cursor.execute("TRUNCATE TABLE performance_schema.events_statements_summary_by_digest")
            self.cursor.execute("TRUNCATE TABLE performance_schema.events_statements_history")
        except Exception as e:
            ProgressLogger.error(f"Could not reset performance_schema: {e}")

    def _get_query_time(self, operation: str) -> float:
        try:
            sql = (
                "SELECT SUM(TIMER_WAIT)/1000000000 AS execution_time_ms "
                "FROM performance_schema.events_statements_history "
                "WHERE EVENT_NAME LIKE %s"
            )
            pattern = f"statement/sql/{operation.lower()}%"
            self.cursor.execute(sql, (pattern,))
            result = self.cursor.fetchone() or {}
            f = float(result.get("execution_time_ms", 0.0))
            return f
        except Exception as e:
            ProgressLogger.error(f"Could not get query time: {e}")
            return 0.0

    @RetryDecorator.retry_on_error()
    def create_users_bulk(self, users_data: List[Dict[str, Any]]) -> Tuple[List[str], float]:
        self.setup_profiling()
        try:
            record_type = self.config_manager.get('record_type')

            if record_type.lower() == RecordType.SMALL.value:
                insert_query = (
                    f"INSERT INTO {self.table_name} "
                    "(value, client_id) "
                    "VALUES (%(value)s, %(client_id)s)"
                )
            else:
                insert_query = (
                    f"INSERT INTO {self.table_name} "
                    "(first_name, last_name, email, address, age, client_id) "
                    "VALUES (%(first_name)s, %(last_name)s, %(email)s, %(address)s, %(age)s, %(client_id)s)"
                )

            future = self._query_executor.execute_many(insert_query, users_data)
            result = future.result()

            if result and hasattr(result, 'rowcount') and result.rowcount > 0:
                inserted_ids = [str(i) for i in range(result.rowcount)]
            else:
                inserted_ids = [str(i) for i in range(len(users_data))]

            execution_time = self._get_query_time('insert')
            return inserted_ids, execution_time
        except Exception as e:
            ProgressLogger.error(f"Error inserting users: {e}")
            return [], 0.0

    @RetryDecorator.retry_on_error()
    def get_all_users(
            self,
            client_id: int
    ) -> Tuple[List[Dict[str, Any]], float]:
        self.setup_profiling()
        try:
            query = f"SELECT * FROM {self.table_name}"
            params: List[Any] = []

            if client_id is not None:
                query += " WHERE client_id = %s"
                params.append(client_id)

            future = self._query_executor.execute_query(query, tuple(params))
            result = future.result()

            execution_time = self._get_query_time('select')
            return result, execution_time
        except Exception as e:
            ProgressLogger.error(f"Error fetching users: {e}")
            return [], 0.0

    @RetryDecorator.retry_on_error()
    def update_users(
            self,
            client_id: int,
            record_type: str
    ) -> Tuple[int, float]:
        self.setup_profiling()
        try:
            if record_type == RecordType.SMALL.value:
                update_query = f"UPDATE {self.table_name} SET value = value + 1 WHERE client_id = %s"
            else:
                update_query = f"UPDATE {self.table_name} SET age = 30, first_name = 'test_name' WHERE client_id = %s"

            params = [client_id]
            future = self._query_executor.execute_query(update_query, tuple(params))
            result = future.result()

            modified_count = result.rowcount if result and hasattr(result, 'rowcount') else 0
            execution_time = self._get_query_time('update')
            return modified_count, execution_time
        except Exception as e:
            ProgressLogger.error(f"Error updating users: {e}")
            return 0, 0.0

    @RetryDecorator.retry_on_error()
    def delete_users(
            self,
            client_id: int,
            record_type: str
    ) -> Tuple[int, float]:
        self.setup_profiling()
        delete_query = f"DELETE FROM {self.table_name} WHERE client_id = %s"
        params = [client_id]

        future = self._query_executor.execute_query(delete_query, tuple(params))

        result = future.result()

        deleted_count = result.rowcount if result and hasattr(result, 'rowcount') else 0
        execution_time = self._get_query_time('delete')

        return deleted_count, execution_time

    @RetryDecorator.retry_on_error()
    def clear_collection(self) -> bool:
        try:
            self._query_executor.execute_query(f"DROP TABLE IF EXISTS {self.table_name}").result()
            self._ensure_table_exists()
            return True
        except Exception as e:
            ProgressLogger.error(f"Error clearing table {self.table_name}: {e}")
            return False

    def create_indexes(self, index_type: IndexType, table_name: str) -> bool:
        return self._index_manager.create_indexes(index_type, table_name)

    def ensure_foreign_key_index(self) -> bool:
        return self._index_manager.create_foreign_key_index()

    @RetryDecorator.retry_on_error()
    def _ensure_table_exists(self) -> bool:
        if self.table_name is None:
            return True
        try:
            record_type = self.config_manager.get('record_type', RecordType.BIG.value)

            if record_type.lower() == RecordType.SMALL.value:
                create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        value INT,
                        client_id INT DEFAULT 0
                    )
                """
            else:
                create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        first_name VARCHAR(255),
                        last_name VARCHAR(255),
                        email VARCHAR(255),
                        address VARCHAR(255),
                        age INT,
                        client_id INT DEFAULT 0
                    )
                """

            self._query_executor.execute_query(create_table_query).result()
            return True
        except Exception as e:
            ProgressLogger.error(f"Error creating table {self.table_name}: {e}")
            return False

    def close(self) -> None:
        if hasattr(self, 'cursor') and self.cursor:
            try:
                self.cursor.close()
            except Exception as e:
                ProgressLogger.error(f"Error closing cursor: {e}")
            self.cursor = None

        if hasattr(self, '_query_executor') and self._query_executor:
            try:
                self._query_executor.close()
            except Exception as e:
                ProgressLogger.error(f"Error closing query executor: {e}")

        if hasattr(self, 'db') and self.db:
            try:
                self.db.close_connection()
            except Exception as e:
                ProgressLogger.error(f"Error closing DB connection: {e}")

        ProgressLogger.print("MySQL repository resources closed")
