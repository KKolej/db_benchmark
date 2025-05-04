import pandas as pd
from typing import List, Union, Optional
import os

from .operation_result import OperationResult
from ..charts.chart_generator import ChartGenerator
from .results_file_manager import ResultsFileManager
from ..common.index_types import IndexType
from ..utils.logging_config import ProgressLogger


class ResultsVisualizer:
    def __init__(
            self,
            results_dir: str,
            records: int,
            timing_method: str,
            iterations: int,
            indexes_type: Union[str, IndexType]
    ):
        self.results: List[OperationResult] = []
        self.iterations = iterations
        self.indexes_type = (
            indexes_type.value if isinstance(indexes_type, IndexType) else indexes_type
        )
        self.file_manager = ResultsFileManager(
            results_dir,
            records,
            timing_method,
            self.indexes_type
        )
        self.results_dir = self.file_manager.main_results_dir

    def add_result(self, database: str, operation: str, records: int, time: float,
                   timing_method: str, indexes_type: str,
                   threads: int, iteration: int):
        if indexes_type:
            self.indexes_type = indexes_type
            self.file_manager = ResultsFileManager(
                self.file_manager.base_dir, records, timing_method,
                self.indexes_type, results_dir=self.results_dir
            )

        result = OperationResult(
            database=database, operation=operation, records=records,
            time=time, timestamp=pd.Timestamp.now(),
            timing_method=timing_method, indexes_type=self.indexes_type,
            threads=threads, iteration=iteration
        )
        self.results.append(result)

    def show_results(self, indexes_type: Optional[str] = None):
        if not self.results:
            ProgressLogger.print("No results to display.")
            return
        grouped = {}
        for r in self.results:
            key = r.indexes_type
            if indexes_type and key != indexes_type:
                continue
            grouped.setdefault(key, []).append(r)
        for idx, results in grouped.items():
            df = pd.DataFrame([vars(r) for r in results])
            if df.empty:
                continue
            timing_method = df['timing_method'].iat[0]
            records = df['records'].iat[0]
            self.file_manager = ResultsFileManager(
                self.file_manager.base_dir,
                records,
                timing_method,
                idx,
                results_dir=self.results_dir
            )
            self._show_standard_chart(df)
            if self.iterations > 1:
                self._show_histogram_chart(df)
                self._show_iterations_comparison_chart(df)
            ProgressLogger.print(df.to_string(index=False))
            self.file_manager.save_results(results, df)

    def _show_standard_chart(self, df: pd.DataFrame):
        if df.empty:
            return
        method = df['timing_method'].iat[0]
        records = df['records'].iat[0]
        chart_path = self.file_manager.get_chart_path(method, records)
        ChartGenerator.generate_standard_chart(df, chart_path)

    def _show_histogram_chart(self, df: pd.DataFrame):
        if df.empty:
            return
        method = df['timing_method'].iat[0]
        records = df['records'].iat[0]
        chart_path = self.file_manager.get_chart_path(method, records, suffix="histogram")
        ChartGenerator.generate_histogram_chart(df, chart_path)

    def _show_iterations_comparison_chart(self, df: pd.DataFrame):
        if df.empty:
            return
        method = df['timing_method'].iat[0]
        records = df['records'].iat[0]
        chart_path = self.file_manager.get_chart_path(method, records, suffix="iterations_comparison")
        ChartGenerator.generate_iterations_comparison_chart(df, chart_path)

    def show_clients_comparison_chart(self, database: str, client_results: List[dict[str, any]], records: int,
                                      indexes_type: Optional[str] = None):
        if not client_results:
            return
        current_index = indexes_type or self.indexes_type
        if self.file_manager.indexes_type != current_index:
            self.file_manager = ResultsFileManager(
                self.file_manager.base_dir,
                records,
                "database",
                current_index,
                results_dir=self.results_dir
            )
        chart_path = self.file_manager.get_chart_path("database", records, suffix=f"clients_{database.lower()}")
        ChartGenerator.generate_clients_comparison_chart(client_results, chart_path, database)
