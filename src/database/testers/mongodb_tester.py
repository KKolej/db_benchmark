from typing import Optional, List, Dict
from .database_tester import DatabaseTester
from ..common import IndexType
from ..mongodb.mongodb_user_repository import MongoDBUserRepository
from ..common.config_manager import ConfigManager
from ..repositories.database_type import DatabaseType


class MongoDBTester(DatabaseTester):
    def __init__(self, max_batch_size: int, show_progress: bool, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.db_type = DatabaseType.MONGO
        connection_str = self.config_manager.get_mongodb_connection_string()
        db_name = self.config_manager.get('mongodb_database')
        self.base_collection_name = self.config_manager.get('mongodb_collection')

        repository = MongoDBUserRepository(
            connection_str=connection_str,
            db_name=db_name,
            collection_name=self.base_collection_name,
            config_manager=self.config_manager
        )

        super().__init__(repository,  self.db_type.value, max_batch_size, show_progress, config_manager)

    def get_collection_name(self, index_type: str, iteration: int) -> str:
        return f"{self.base_collection_name}_test_{index_type}_iter_{iteration}"

    def test_fetch_all_users(
        self,
        iteration: int,
        index_type: IndexType,
        number_of_records: int,
        users: List[Dict],
    ):
        collection_name = self.get_collection_name(index_type, iteration)

        self.repository = MongoDBUserRepository(
            connection_str=self.repository.conn.connection_str,
            db_name=self.repository.conn.db_name,
            collection_name=collection_name,
            config_manager=self.config_manager
        )

        return super().test_fetch_all_users(
            iteration=iteration,
            index_type=index_type,
            number_of_records=number_of_records,
            users=users,
        )
