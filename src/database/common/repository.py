from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Union

from .index_types import IndexType

class Repository(ABC):

    @abstractmethod
    def create_users_bulk(self, users_data: List[Dict]) -> Tuple[List[str], float]:
        pass

    @abstractmethod
    def get_all_users(self, client_id: int) -> Tuple[List[Dict], float]:
        pass

    @abstractmethod
    def clear_collection(self) -> bool:
        pass
