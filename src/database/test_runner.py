import gc
from typing import List, Dict, Any

from .repositories.database_type import DatabaseType
from .testers.mongodb_tester import MongoDBTester
from .testers.mysql_tester import MySQLTester
from .result_handling.results_visualizer import ResultsVisualizer
from .utils.logging_config import ProgressLogger
from .common.index_types import IndexType
from .common.config_manager import ConfigManager

class TestRunner:
    DB_LIST = ("MongoDB", "MySQL")

    def __init__(self, total_records: int, iterations: int, index_types, max_batch_size: int, show_progress: bool, config_manager: ConfigManager) -> None:
        self.total_records = total_records
        self.iterations = iterations
        self.config_manager = config_manager
        idx_enum = IndexType.from_string(index_types)
        self.index_types = IndexType.get_all_types() if idx_enum == IndexType.ALL else (
            [index_types] if isinstance(index_types, str) else index_types or [IndexType.NO_INDEXES.value])

        self.testers = {
            "MongoDB": MongoDBTester(max_batch_size, show_progress, config_manager),
            "MySQL": MySQLTester(max_batch_size, show_progress, config_manager),
        }

        self.visualizer = ResultsVisualizer(
            results_dir="results",
            records=total_records,
            timing_method="database",
            iterations=iterations,
            indexes_type=self.index_types[0]
        )

        self.client_results = {db: {idx: [] for idx in self.index_types} for db in self.DB_LIST}

    def _drop_test_collections(self, tester) -> None:
        repo = tester.repository

        if tester.db_type == DatabaseType.MONGO:
            with repo.conn as conn:
                db = conn.client[repo.conn.db_name]
                for name in db.list_collection_names():
                    if name.startswith("test"):
                        db.drop_collection(name)
                        ProgressLogger.important_info(f"Dropped collection: {name}")

        elif tester.db_type == DatabaseType.MYSQL:
            exe = repo._query_executor
            for row in exe.execute_query("SHOW TABLES").result():
                name = next(iter(row.values()))
                if name.startswith("test"):
                    exe.execute_query(f"DROP TABLE IF EXISTS {name}").result()
                    ProgressLogger.important_info(f"Dropped table: {name}")

    def clean_databases(self) -> None:
        for db, tester in self.testers.items():
            try:
                tester.repository.clear_collection()
                self._drop_test_collections(tester)
                ProgressLogger.important_info(f"Database {db} cleaned")
            except Exception as e:
                ProgressLogger.error(f"Error cleaning {db}: {e}")

    def _save_results(self, db: str, idx: str, iteration: int, insert_t: float, fetch_t: float, inserted: int, results: List[Dict]) -> None:
        for r in results:
            r["iteration"] = iteration
        self.client_results.setdefault(db, {}).setdefault(idx, []).extend(results)

        self.visualizer.add_result(db, "Insert", self.total_records, insert_t, "database", idx, 1, iteration)
        self.visualizer.add_result(db, "FetchAll", self.total_records, fetch_t, "database", idx, 1, iteration)

    def _save_update_results(self, db: str, idx: str, iteration: int, update_t: float, updated: int, results: List[Dict]) -> None:
        for r in results:
            r["iteration"] = iteration
        self.client_results.setdefault(db, {}).setdefault(idx, []).extend(results)

        self.visualizer.add_result(db, "Update", self.total_records, update_t, "database", idx, 1, iteration)

    def _save_delete_results(self, db: str, idx: str, iteration: int, delete_t: float, deleted: int, results: List[Dict]) -> None:
        for r in results:
            r["iteration"] = iteration
        self.client_results.setdefault(db, {}).setdefault(idx, []).extend(results)

        self.visualizer.add_result(db, "Delete", self.total_records, delete_t, "database", idx, 1, iteration)

    def run(self) -> bool:
        for idx in self.index_types:
            ProgressLogger.important_info(f"Starting tests for index type: {idx.upper()}")
            self.clean_databases()

            test_data_cache = {}

            for i in range(1, self.iterations + 1):
                ProgressLogger.important_info(f"Running iteration {i} for index type {idx.upper()}")

                for db_name, tester in self.testers.items():
                    ProgressLogger.important_info(f"Testing {db_name} - Iteration {i}")

                    tester.repository.clear_collection()

                    test_data = test_data_cache.get(i)
                    try:
                        insert_t, fetch_t, inserted, results, generated_data = tester.test_fetch_all_users(
                            iteration=i,
                            index_type=idx,
                            number_of_records=self.total_records,
                            users=test_data
                        )
                    except Exception as e:
                        ProgressLogger.error(f"Error testing {db_name} with {idx} index: {e}")
                        insert_t = fetch_t = 0.0
                        inserted = 0
                        results = []
                        generated_data = None

                    self._save_results(db_name, idx, i, insert_t, fetch_t, inserted, results)

                    test_update = self.config_manager.get('test_update', 'True').lower() == 'true'
                    if test_update:
                        try:
                            update_t, updated, update_results = tester.test_update_users(
                                iteration=i,
                                index_type=idx,
                                number_of_records=self.total_records,
                                users=generated_data
                            )
                            self._save_update_results(db_name, idx, i, update_t, updated, update_results)
                        except Exception as e:
                            ProgressLogger.error(f"Error testing update on {db_name} with {idx} index: {e}")

                    test_delete = self.config_manager.get('test_delete', 'True').lower() == 'true'
                    if test_delete:
                        try:
                            delete_t, deleted, delete_results = tester.test_delete_users(
                                iteration=i,
                                index_type=idx,
                                number_of_records=self.total_records,
                                users=generated_data
                            )
                            self._save_delete_results(db_name, idx, i, delete_t, deleted, delete_results)
                        except Exception as e:
                            ProgressLogger.error(f"Error testing delete on {db_name} with {idx} index: {e}")

                    if generated_data is not None and i not in test_data_cache:
                        test_data_cache[i] = generated_data

                    gc.collect()

            for tester in self.testers.values():
                self._drop_test_collections(tester)

            self.visualizer.show_results(indexes_type=idx)

            for db, idx_res in self.client_results.items():
                if idx in idx_res and idx_res[idx]:
                    self.visualizer.show_clients_comparison_chart(db, idx_res[idx], self.total_records, idx)

            gc.collect()
            ProgressLogger.important_info(f"Completed tests for index type: {idx.upper()}")

        self.client_results.clear()
        gc.collect()
        return True

    def close(self):
        for db_name, tester in self.testers.items():
            try:
                tester.close()
                ProgressLogger.important_info(f"Closed tester for {db_name}")
            except Exception as e:
                ProgressLogger.error(f"Error closing tester for {db_name}: {e}")

        self.testers.clear()
        self.client_results.clear()
        gc.collect()
