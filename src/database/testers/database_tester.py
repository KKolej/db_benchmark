import gc
from typing import List, Dict, Tuple, Optional

from ..common import IndexType
from ..data.data_generator import DataGenerator
from ..data.parallel_data_generator import ParallelDataGenerator
from ..repositories.user_repository import UserRepository
from ..utils.logging_config import set_current_iteration, ProgressLogger
from ..common.config_manager import ConfigManager

class DatabaseTester:
    def __init__(self, repository: UserRepository, db_name: str, max_batch_size: int, show_progress: bool, config_manager: ConfigManager):
        self.repository = repository
        self.db_name = db_name
        self.max_batch_size = max_batch_size
        self.show_progress = show_progress
        self.config_manager = config_manager

    def _check_index(self, index_type: IndexType) -> None:
        if index_type != IndexType.NO_INDEXES:
            table_or_collection_name = ""
            if hasattr(self.repository, "table_name"):
                table_or_collection_name = self.repository.table_name
            elif hasattr(self.repository, "collection"):
                table_or_collection_name = self.repository.collection.name
            self.repository.create_indexes(index_type, table_or_collection_name)

    def _generate_users(self, records: int) -> List[Dict]:
        ProgressLogger.important_info("Generating test users")
        clients = self.config_manager.get("clients", 1)
        data = ParallelDataGenerator.generate_data_parallel(records, clients)
        return [u for batch in data for u in batch]

    def _insert_data(self, users: List[Dict]) -> Tuple[float, int]:
        total_time = 0.0
        total_count = 0
        batch_size = min(self.max_batch_size, len(users))

        for i in range(0, len(users), batch_size):
            chunk = users[i:i + batch_size]
            ids, elapsed = self.repository.create_users_bulk(chunk)
            total_time += elapsed
            total_count += len(ids)

        return total_time, total_count

    def _fetch_all_users(self) -> Tuple[float, int, List[Dict[str, int]]]:
        clients = self.config_manager.get("clients", 1)
        total_time = total_records = 0
        results = []

        for cid in range(clients):
            users, t = self.repository.get_all_users(client_id=cid)
            users = users if isinstance(users, list) else []
            total_time += t
            total_records += len(users)
            results.append({"client_id": cid, "records": len(users), "time": t})

        return (total_time / clients if clients else 0), total_records, results

    def test_fetch_all_users(
            self,
            iteration: int,
            index_type: IndexType,
            number_of_records: int,
            users: List[Dict],
    ) -> Tuple[float, float, int, List[Dict], Optional[List[Dict]]]:
        set_current_iteration(iteration)
        if index_type:
            ProgressLogger.important_info(f"Testing {self.db_name} with {index_type.upper()} indexes")
        else:
            ProgressLogger.important_info(f"Testing {self.db_name} without indexes")

        self.repository.clear_collection()

        if users is None:
            users = self._generate_users(number_of_records)
            ProgressLogger.important_info(f"Generated {len(users)} records")

        self.repository.setup_profiling()

        ProgressLogger.important_info(f"Start insert data")
        insert_t, inserted = self._insert_data(users)

        ProgressLogger.important_info(f"Check indexes")
        self._check_index(index_type)

        ProgressLogger.important_info(f"Start fetch all")
        fetch_t, fetched, results = self._fetch_all_users()
        gc.collect()

        return insert_t, fetch_t, inserted, results, users

    def close(self):
        if hasattr(self, 'repository') and self.repository:
            try:
                self.repository.close()
                ProgressLogger.print(f"Closed repository for {self.db_name}")
            except Exception as e:
                ProgressLogger.error(f"Error closing repository for {self.db_name}: {e}")
