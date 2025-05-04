import logging
from ..common.index_manager import IndexManager
from ..common.retry_decorator import RetryDecorator
from ..utils.logging_config import ProgressLogger


class MySQLIndexManager(IndexManager):
    def __init__(self, query_executor):
        self._query_executor = query_executor

    @RetryDecorator.retry_on_error()
    def create_foreign_key_index(self, table_name: str) -> bool:
        try:
            create_query = f"CREATE INDEX idx_client_id ON {table_name} (client_id)"
            future_create = self._query_executor.execute_query(create_query)
            future_create.result()
            ProgressLogger.important_info("Created foreign key index (idx_client_id).")
            return True
        except Exception as e:
            ProgressLogger.error(f"Error creating foreign key index: {e}")
            return False

