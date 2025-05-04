from typing import List, Dict
from .database_tester import DatabaseTester
from ..mysql.mysql_user_repository import MySQLUserRepository
from ..common.config_manager import ConfigManager
from ..repositories.database_type import DatabaseType


class MySQLTester(DatabaseTester):
    def __init__(self, max_batch_size: int, show_progress: bool, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.db_type = DatabaseType.MYSQL
        self.mysql_database = self.config_manager.get('mysql_database')
        self.connection_str = self.config_manager.get_mysql_connection_string()
        self.base_table_name = self.config_manager.get('mysql_table')

        repository = MySQLUserRepository(None, config_manager=self.config_manager)
        super().__init__(repository, self.db_type.value, max_batch_size, show_progress, self.config_manager)

    def get_table_name(self, index_type: str, iteration: int) -> str:
        return f"{self.base_table_name}_test_{index_type}_iter_{iteration}"

    def test_fetch_all_users(
            self,
            iteration: int,
            index_type: str,
            number_of_records: int,
            users: List[Dict],
    ):
        table_name = self.get_table_name(index_type or "no_indexes", iteration)
        self.repository = MySQLUserRepository(table_name=table_name, config_manager=self.config_manager)

        return super().test_fetch_all_users(
            iteration=iteration,
            index_type=index_type,
            number_of_records=number_of_records,
            users=users,
        )
