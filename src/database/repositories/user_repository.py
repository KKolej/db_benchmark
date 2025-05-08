from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class UserRepository():
    @abstractmethod
    def create_users_bulk(self, users_data: List[Dict]) -> Tuple[List[str], float]:
        pass

    @abstractmethod
    def get_all_users(self, client_id: int) -> Tuple[List[Dict], float]:
        pass

    @abstractmethod
    def clear_collection(self):
        pass

    @abstractmethod
    def setup_profiling(self):
        pass

    @abstractmethod
    def create_indexes(self, index_type, table_or_collection_name):
        pass

    @abstractmethod
    def delete_users(self, client_id: int, record_type: str) -> Tuple[int, float]:
        pass

    @abstractmethod
    def update_users(self, client_id: int, record_type: str) -> Tuple[int, float]:
        pass