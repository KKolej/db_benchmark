from concurrent.futures import ThreadPoolExecutor
import logging
from ..utils.logging_config import ProgressLogger


class QueryExecutor:
    def __init__(self, connection_pool, max_workers: int):
        self.connection_pool = connection_pool
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def shutdown(self):
        if self._executor:
            self._executor.shutdown(wait=True)
            ProgressLogger.print("ThreadPoolExecutor shutdown complete")

    def execute_query(self, query: str, params=None):
        def _run(query_text, parameters):
            conn = self.connection_pool.get_connection()
            try:
                cursor = conn.get_cursor()
                cursor.execute(query_text, parameters or ())
                return cursor.fetchall()
            finally:
                cursor.close()
                self.connection_pool.release_connection(conn)
        return self._executor.submit(_run, query, params)

    def execute_many(self, query: str, params_list):
        def _run(query_text, parameter_list):
            conn = self.connection_pool.get_connection()
            try:
                cursor = conn.get_cursor()
                cursor.executemany(query_text, parameter_list)
                return cursor.rowcount
            finally:
                cursor.close()
                self.connection_pool.release_connection(conn)
        return self._executor.submit(_run, query, params_list)
