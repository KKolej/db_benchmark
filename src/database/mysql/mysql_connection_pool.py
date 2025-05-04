import logging
from ..common.connection_pool import ConnectionPool
from ..common.config_manager import ConfigManager
from .mysql_connection import MySQLConnection
from ..utils.logging_config import ProgressLogger


class MySQLConnectionPool(ConnectionPool):
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        size = int(self.config_manager.get('mysql_pool_size', 5))
        super().__init__(size)
        ProgressLogger.print(f'Initialized MySQL connection pool (size={size})')

    def create_connection(self):
        ProgressLogger.print('Creating new MySQL connection')
        return MySQLConnection(self.config_manager)
