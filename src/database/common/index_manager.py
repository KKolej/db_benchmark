import logging
from abc import ABC, abstractmethod

from .index_types import IndexType
from ..utils.logging_config import ProgressLogger


class IndexManager(ABC):

    @abstractmethod
    def create_foreign_key_index(self, table_name: str) -> bool:
        pass


    def create_indexes(self, index_type: IndexType, table_name: str) -> bool:
        try:
            method_map = {
                IndexType.FOREIGN_KEY.value: lambda: self.create_foreign_key_index(table_name),
            }

            method = method_map.get(index_type)
            if method:
                return method()
            else:
                ProgressLogger.warn(f"Unknown index type: {index_type}")
                return False
        except Exception as exc:
            ProgressLogger.error(f"Error creating indexes: {exc}")
            return False
