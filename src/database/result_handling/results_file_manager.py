import os
import json
import pandas as pd
from dataclasses import asdict
from datetime import datetime
from typing import List

from .operation_result import OperationResult
from ..utils.logging_config import ProgressLogger

class ResultsFileManager:
    def __init__(self,
                 base_dir: str = 'results',
                 records: int = None,
                 timing_method: str = None,
                 indexes_type: str = 'no_indexes',
                 results_dir: str = None):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.base_dir = os.path.join(project_root, base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        self.indexes_type = indexes_type
        if results_dir:
            self.main_results_dir = results_dir
        else:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            name = f"results_{ts}"
            if records is not None:
                name += f"_records{records}"
            if timing_method:
                name += f"_{timing_method}"
            self.main_results_dir = os.path.join(self.base_dir, name)
        os.makedirs(self.main_results_dir, exist_ok=True)
        idx_map = {
            'no_indexes': '01_bez_indeksow',
            'foreign_key': '02_indeks_klucza_obcego',
            'all': '00_wszystkie_indeksy'
        }
        folder = idx_map.get(indexes_type, indexes_type)
        self.current_results_dir = os.path.join(self.main_results_dir, folder)
        os.makedirs(self.current_results_dir, exist_ok=True)

    def save_results(self, results: List[OperationResult], df: pd.DataFrame):
        records = df['records'].iat[0] if not df.empty else 0
        self._save_csv(df, records)
        self._save_json(results, records)

    def _save_csv(self, df: pd.DataFrame, records: int):
        path = os.path.join(self.current_results_dir, f"results_{records}.csv")
        df.to_csv(path, index=False)
        ProgressLogger.print(f"Results saved to CSV: {path}")

    def _save_json(self, results: List[OperationResult], records: int):
        path = os.path.join(self.current_results_dir, f"results_{records}.json")
        data = {'results': [asdict(r) for r in results]}
        for r in data['results']:
            r['timestamp'] = r['timestamp'].isoformat()
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        ProgressLogger.print(f"Results saved to JSON: {path}")

    def get_chart_path(self, method: str, records: int, suffix: str = None) -> str:
        name = f"chart_{method}_{records}"
        if suffix:
            name += f"_{suffix}"
        return os.path.join(self.current_results_dir, f"{name}.png")
