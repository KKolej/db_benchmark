import os
from typing import Any


class ConfigManager:
    _instance = None

    def __new__(cls, **cli_values):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, **cli_values):
        self._config = {}
        if self._initialized:
            return

        self._initialized = True

        for key, val in cli_values.items():
            if val is not None:
                self._config[key] = val

        self._load_from_env()

        self._config['mongodb_collection'] = 'test_collection'
        self._config['mysql_table'] = 'test_table'

    def _load_from_env(self):
        self._config['mysql_host'] = os.getenv('MYSQL_HOST')
        self._config['mysql_port'] = os.getenv('MYSQL_PORT')
        self._config['mysql_user'] = os.getenv('MYSQL_USER')
        self._config['mysql_password'] = os.getenv('MYSQL_PASSWORD')
        self._config['mysql_database'] = os.getenv('MYSQL_DB')

        self._config['mongodb_host'] = os.getenv('MONGO_HOST')
        self._config['mongodb_port'] = os.getenv('MONGO_PORT')
        self._config['mongodb_user'] = os.getenv('MONGO_USER')
        self._config['mongodb_password'] = os.getenv('MONGO_PASSWORD')
        self._config['mongodb_database'] = os.getenv('MONGO_DB')

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def get_mysql_connection_string(self) -> str:
        return f"mysql://{self.get('mysql_user')}:{self.get('mysql_password')}@{self.get('mysql_host')}:{self.get('mysql_port')}/{self.get('mysql_database')}"

    def get_mongodb_connection_string(self) -> str:
        return f"mongodb://{self.get('mongodb_user')}:{self.get('mongodb_password')}@{self.get('mongodb_host')}:{self.get('mongodb_port')}/?authSource=admin"
