import logging
import pymysql
from ..common.database_connection import DatabaseConnection
from ..common.config_manager import ConfigManager
from ..utils.logging_config import ProgressLogger

class MySQLConnection(DatabaseConnection):
    def __init__(self, config_manager: ConfigManager, connection=None):
        self.config_manager = config_manager
        self.connection = connection
        if self.connection is None:
            self._create_connection()

    def _create_connection(self):
        try:
            host = self.config_manager.get('mysql_host')
            port = int(self.config_manager.get('mysql_port'))
            user = self.config_manager.get('mysql_user')
            password = self.config_manager.get('mysql_password')
            database = self.config_manager.get('mysql_database')

            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor
            )

            cursor = self.connection.cursor()
            cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES'")
            cursor.execute("SET SESSION innodb_lock_wait_timeout=50")
            cursor.execute("SET SESSION wait_timeout=28800")
            cursor.execute("SET SESSION interactive_timeout=28800")
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cursor.close()

            ProgressLogger.print("Created new MySQL connection")
        except Exception as e:
            ProgressLogger.error(f"Error creating MySQL connection: {e}")
            raise

    def get_cursor(self):
        try:
            if not self.is_connected():
                ProgressLogger.print("Connection does not exist or is inactive, creating new...")
                self._create_connection()

            return self.connection.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            ProgressLogger.error(f"Error getting cursor: {e}")
            return None

    def close_connection(self):
        if not self.is_connected():
            return

        try:
            self.connection.close()
        except Exception as e:
            ProgressLogger.error(f"Błąd podczas zamykania połączenia: {e}")
        finally:
            self.connection = None

    def is_connected(self):
        return (
            self.connection is not None and
            hasattr(self.connection, 'open') and
            self.connection.open
        )
