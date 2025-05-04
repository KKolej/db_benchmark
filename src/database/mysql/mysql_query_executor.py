import logging
from ..common.query_executor import QueryExecutor
from .mysql_connection_pool import MySQLConnectionPool
from ..common.config_manager import ConfigManager
from ..utils.logging_config import ProgressLogger

class MySQLQueryExecutor(QueryExecutor):
    def __init__(self, connection_pool=None, config_manager=None, max_workers=None):
        cfg = config_manager or ConfigManager()
        self.pool = connection_pool or MySQLConnectionPool(cfg)
        workers = max_workers or self.pool.pool_size
        super().__init__(self.pool, workers)
        ProgressLogger.print(f"Initialized MySQL query executor (workers={workers})")

    def close(self):
        if hasattr(self, 'pool') and self.pool:
            self.pool.close_all()
        self.shutdown()
