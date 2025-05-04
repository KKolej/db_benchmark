import logging
from pymongo import MongoClient
from ..common.config_manager import ConfigManager
from ..common.database_connection import DatabaseConnection
from ..utils.logging_config import ProgressLogger


class MongoDBConnection(DatabaseConnection):
    def __init__(self, connection_str: str, db_name: str, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.connection_str = connection_str
        self.db_name = db_name
        self.max_pool_size = self.config_manager.get('mongodb_pool_size')
        self.client = None
        self.connection = None
        self._initialize_connection()

    def _initialize_connection(self):
        try:
            ProgressLogger.important_info(f"Connect to MongoDB: {self.connection_str} (db_name: {self.db_name}), max_pool_size: {self.max_pool_size}")
            self.client = MongoClient(
                self.connection_str,
                maxPoolSize=self.max_pool_size,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=10000,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
                serverSelectionTimeoutMS=5000,
                retryWrites=True,
                w=1,
                journal=False
            )
            self.connection = self.client[self.db_name]
            self.client.admin.command('ping')
            try:
                self.connection.command({'profile': 2})
            except Exception as profile_error:
                ProgressLogger.error(f"Cannot enable MongoDB profiling: {profile_error}")
            ProgressLogger.important_info(f"Successfully connected to MongoDB database: {self.db_name}")
        except Exception as e:
            ProgressLogger.error(f"Cannot create MongoDB connection: {e}")
            raise

    def get_collection(self, collection_name: str):
        if self.connection is None:
            raise Exception("Database connection has not been established.")
        return self.connection[collection_name]

    def get_cursor(self):
        return self.connection

    def close_connection(self):
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                ProgressLogger.error(f"Error closing MongoDB connection: {e}")
            finally:
                self.client = None
                self.connection = None

    def is_connected(self):
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
