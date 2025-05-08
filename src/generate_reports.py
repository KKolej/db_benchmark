#!/usr/bin/env python3
import os
import re
import json
import csv
import argparse
from datetime import datetime
from typing import Tuple, List, Any, Optional

from database.utils.logging_config import ProgressLogger


class ReportGenerator:
    @staticmethod
    def parse_folder_name(folder_name: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        pattern = r'results_(\d{8})_(\d{6})_records(\d+)_database'
        match = re.match(pattern, os.path.basename(folder_name))
        if match:
            date_str, time_str, records = match.groups()
            date = datetime.strptime(date_str, '%Y%m%d').strftime('%d.%m.%Y')
            time = datetime.strptime(time_str, '%H%M%S').strftime('%H:%M:%S')
            return date, time, int(records)
        return None, None, None

    @staticmethod
    def get_results_from_json(json_file: str) -> Tuple[float, float, float, float, float, float, float, float]:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                results = json.load(f).get('results', [])
            mongodb_insert = next(
                (r['time'] for r in results if r['database'] == 'MongoDB' and r['operation'].lower() == 'insert'), 0)
            mongodb_fetch = next((r['time'] for r in results if
                                  r['database'] == 'MongoDB' and r['operation'].lower() in ['fetchall', 'fetch']), 0)
            mongodb_update = next((r['time'] for r in results if
                                  r['database'] == 'MongoDB' and r['operation'].lower() == 'update'), 0)
            mongodb_delete = next((r['time'] for r in results if
                                  r['database'] == 'MongoDB' and r['operation'].lower() == 'delete'), 0)
            mysql_insert = next(
                (r['time'] for r in results if r['database'] == 'MySQL' and r['operation'].lower() == 'insert'), 0)
            mysql_fetch = next((r['time'] for r in results if
                                r['database'] == 'MySQL' and r['operation'].lower() in ['fetchall', 'fetch']), 0)
            mysql_update = next((r['time'] for r in results if
                                r['database'] == 'MySQL' and r['operation'].lower() == 'update'), 0)
            mysql_delete = next((r['time'] for r in results if
                                r['database'] == 'MySQL' and r['operation'].lower() == 'delete'), 0)
            return mongodb_insert, mongodb_fetch, mongodb_update, mongodb_delete, mysql_insert, mysql_fetch, mysql_update, mysql_delete
        except Exception:
            return 0, 0, 0, 0, 0, 0, 0, 0

    @staticmethod
    def get_results_path(results_folder: str) -> str:
        return results_folder if os.path.isabs(results_folder) else os.path.join('results', results_folder)

    @staticmethod
    def format_index_type(index_type: str) -> str:
        return index_type.replace('_', ' ').title()

    @staticmethod
    def calculate_comparison(value1: float, value2: float) -> str:
        if value1 > 0 and value2 > 0:
            if value1 < value2:
                diff = (value2 / value1 - 1) * 100
                return f"MongoDB szybszy o {diff:.2f}%"
            elif value2 < value1:
                diff = (value1 / value2 - 1) * 100
                return f"MySQL szybszy o {diff:.2f}%"
            return "Identyczny czas"
        return "N/A"

    @classmethod
    def generate_standard_summary(cls, results_folder: str, date: str, time: str, records: int) -> None:
        results_path = cls.get_results_path(results_folder)
        if not os.path.exists(results_path):
            ProgressLogger.error(f"Folder nie istnieje: {results_path}")
            return

        subfolders = sorted(
            [f for f in os.listdir(results_path) if os.path.isdir(os.path.join(results_path, f))],
            key=lambda x: int(x.split('_')[0]) if x.split('_')[0].isdigit() else 999
        )

        csv_file = os.path.join(results_path, f'summary_{records}.csv')
        txt_file = os.path.join(results_path, f'summary_{records}.txt')

        csv_header = [
            'Typ indeksu',
            'MongoDB Insert', 'MongoDB Fetch', 'MongoDB Update', 'MongoDB Delete',
            'MySQL Insert', 'MySQL Fetch', 'MySQL Update', 'MySQL Delete',
            'MongoDB vs MySQL Insert', 'MongoDB vs MySQL Fetch', 'MongoDB vs MySQL Update', 'MongoDB vs MySQL Delete'
        ]

        summary_lines = [
            f"PODSUMOWANIE TESTÓW - {date} {time}",
            f"Liczba rekordów: {records}",
            "",
            "=" * 80,
            ""
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as csv_f, \
                open(txt_file, 'w', encoding='utf-8') as txt_f:
            csv_writer = csv.writer(csv_f, delimiter=';')
            csv_writer.writerow(csv_header)

            for sub in subfolders:
                json_file = os.path.join(results_path, sub, f'results_{records}.json')
                if not os.path.exists(json_file):
                    ProgressLogger.error(f"Brak pliku JSON: {json_file}")
                    continue

                mi, mf, mu, md, yi, yf, yu, yd = cls.get_results_from_json(json_file)
                mi_ms, mf_ms, mu_ms, md_ms = mi, mf, mu, md
                yi_ms, yf_ms, yu_ms, yd_ms = yi, yf, yu, yd

                insert_cmp = cls.calculate_comparison(mi_ms, yi_ms)
                fetch_cmp = cls.calculate_comparison(mf_ms, yf_ms)
                update_cmp = cls.calculate_comparison(mu_ms, yu_ms)
                delete_cmp = cls.calculate_comparison(md_ms, yd_ms)

                idx_type = sub.split('_', 1)[1] if '_' in sub else sub
                idx_type = cls.format_index_type(idx_type)

                csv_writer.writerow([
                    idx_type,
                    f"{mi_ms:.2f}", f"{mf_ms:.2f}", f"{mu_ms:.2f}", f"{md_ms:.2f}",
                    f"{yi_ms:.2f}", f"{yf_ms:.2f}", f"{yu_ms:.2f}", f"{yd_ms:.2f}",
                    insert_cmp, fetch_cmp, update_cmp, delete_cmp
                ])

                summary_lines.extend([
                    f"Typ indeksu: {idx_type}",
                    f"  MongoDB Insert: {mi_ms:.2f} ms", f"  MongoDB Fetch: {mf_ms:.2f} ms",
                    f"  MongoDB Update: {mu_ms:.2f} ms", f"  MongoDB Delete: {md_ms:.2f} ms",
                    f"  MySQL Insert:  {yi_ms:.2f} ms", f"  MySQL Fetch:  {yf_ms:.2f} ms",
                    f"  MySQL Update:  {yu_ms:.2f} ms", f"  MySQL Delete:  {yd_ms:.2f} ms"
                ])

                if insert_cmp != 'N/A':
                    summary_lines.append(f"  Insert: {insert_cmp}")
                if fetch_cmp != 'N/A':
                    summary_lines.append(f"  Fetch: {fetch_cmp}")
                if update_cmp != 'N/A':
                    summary_lines.append(f"  Update: {update_cmp}")
                if delete_cmp != 'N/A':
                    summary_lines.append(f"  Delete: {delete_cmp}")

                summary_lines.extend(["", "-" * 80, ""])

            txt_f.write("\n".join(summary_lines))

        ProgressLogger.important_info(f"CSV summary saved to: {csv_file}")
        ProgressLogger.important_info(f"TXT summary saved to: {txt_file}")


def generate_summary(results_folder: str) -> None:
    date, time, rec = ReportGenerator.parse_folder_name(results_folder)
    if date and rec:
        ReportGenerator.generate_standard_summary(results_folder, date, time, rec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generuje podsumowania dla folderów z wynikami testów.')
    parser.add_argument('--folder', type=str)
    parser.add_argument('--type', type=str, choices=['standard', 'main', 'all'], default='all')
    args = parser.parse_args()

    if args.folder:
        if args.type in ['standard', 'all']:
            d, t, r = ReportGenerator.parse_folder_name(args.folder)
            if d:
                ReportGenerator.generate_standard_summary(args.folder, d, t, r)
    else:
        base = 'results'
        if os.path.exists(base):
            folders = sorted(
                [f for f in os.listdir(base) if f.startswith('results_')],
                reverse=True
            )
            if folders:
                latest = folders[0]
                ProgressLogger.print(f"Używam najnowszego folderu: {latest}")
                d, t, r = ReportGenerator.parse_folder_name(latest)
                if args.type in ['standard', 'all'] and d:
                    ReportGenerator.generate_standard_summary(latest, d, t, r)
