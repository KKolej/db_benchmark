#!/usr/bin/env python3
import os
import re
import json
import csv
import argparse
from datetime import datetime
from typing import Tuple, List, Optional

from database.utils.logging_config import ProgressLogger


class ReportGenerator:
    @staticmethod
    def parse_folder_name(folder_name: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        pattern = r'results_(\d{8})_(\d{6})_records(\d+)_database'
        match = re.match(pattern, os.path.basename(folder_name))
        if match:
            date_str, time_str, records = match.groups()
            formatted_date = datetime.strptime(date_str, '%Y%m%d').strftime('%d.%m.%Y')
            formatted_time = datetime.strptime(time_str, '%H%M%S').strftime('%H:%M:%S')
            return formatted_date, formatted_time, int(records)
        return None, None, None

    @staticmethod
    def extract_operation_times(json_path: str) -> Tuple[float, float, float, float, float, float, float, float]:
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                operations = json.load(file).get('results', [])
            mongodb_insert_time = next((r['time'] for r in operations if r['database'] == 'MongoDB' and r['operation'].lower() == 'insert'), 0)
            mongodb_fetch_time = next((r['time'] for r in operations if r['database'] == 'MongoDB' and r['operation'].lower() in ['fetchall', 'fetch']), 0)
            mongodb_update_time = next((r['time'] for r in operations if r['database'] == 'MongoDB' and r['operation'].lower() == 'update'), 0)
            mongodb_delete_time = next((r['time'] for r in operations if r['database'] == 'MongoDB' and r['operation'].lower() == 'delete'), 0)
            mysql_insert_time = next((r['time'] for r in operations if r['database'] == 'MySQL' and r['operation'].lower() == 'insert'), 0)
            mysql_fetch_time = next((r['time'] for r in operations if r['database'] == 'MySQL' and r['operation'].lower() in ['fetchall', 'fetch']), 0)
            mysql_update_time = next((r['time'] for r in operations if r['database'] == 'MySQL' and r['operation'].lower() == 'update'), 0)
            mysql_delete_time = next((r['time'] for r in operations if r['database'] == 'MySQL' and r['operation'].lower() == 'delete'), 0)
            return (
                mongodb_insert_time,
                mongodb_fetch_time,
                mongodb_update_time,
                mongodb_delete_time,
                mysql_insert_time,
                mysql_fetch_time,
                mysql_update_time,
                mysql_delete_time
            )
        except Exception:
            return 0, 0, 0, 0, 0, 0, 0, 0

    @staticmethod
    def get_absolute_results_path(relative_path: str) -> str:
        return relative_path if os.path.isabs(relative_path) else os.path.join('results', relative_path)

    @staticmethod
    def prettify_index_type(index_type: str) -> str:
        return index_type.replace('_', ' ').title()

    @staticmethod
    def compare_times(time1: float, time2: float) -> str:
        if time1 > 0 and time2 > 0:
            if time1 < time2:
                return f"MongoDB szybszy o {(time2 / time1 - 1) * 100:.2f}%"
            elif time2 < time1:
                return f"MySQL szybszy o {(time1 / time2 - 1) * 100:.2f}%"
            return "Identyczny czas"
        return "N/A"

    @classmethod
    def generate_summary(cls, results_directory: str, date: str, time: str, record_count: int) -> None:
        full_path = cls.get_absolute_results_path(results_directory)
        if not os.path.exists(full_path):
            ProgressLogger.error(f"Folder nie istnieje: {full_path}")
            return

        index_folders = sorted(
            [f for f in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, f))],
            key=lambda name: int(name.split('_')[0]) if name.split('_')[0].isdigit() else 999
        )

        csv_output = os.path.join(full_path, f'summary_{record_count}.csv')
        txt_output = os.path.join(full_path, f'summary_{record_count}.txt')

        csv_columns = [
            'Typ indeksu',
            'MongoDB Insert', 'MongoDB Fetch', 'MongoDB Update', 'MongoDB Delete',
            'MySQL Insert', 'MySQL Fetch', 'MySQL Update', 'MySQL Delete',
            'Porownanie Insert', 'Porownanie Fetch', 'Porownanie Update', 'Porownanie Delete'
        ]

        summary_lines = [
            f"PODSUMOWANIE TESTÓW - {date} {time}",
            f"Liczba rekordów: {record_count}",
            "",
            "=" * 80,
            ""
        ]

        with open(csv_output, 'w', newline='', encoding='utf-8') as csv_file, open(txt_output, 'w', encoding='utf-8') as txt_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(csv_columns)

            for folder in index_folders:
                json_path = os.path.join(full_path, folder, f'results_{record_count}.json')
                if not os.path.exists(json_path):
                    ProgressLogger.error(f"Brak pliku JSON: {json_path}")
                    continue

                mongodb_insert_time, mongodb_fetch_time, mongodb_update_time, mongodb_delete_time, \
                mysql_insert_time, mysql_fetch_time, mysql_update_time, mysql_delete_time = cls.extract_operation_times(json_path)

                insert_cmp = cls.compare_times(mongodb_insert_time, mysql_insert_time)
                fetch_cmp = cls.compare_times(mongodb_fetch_time, mysql_fetch_time)
                update_cmp = cls.compare_times(mongodb_update_time, mysql_update_time)
                delete_cmp = cls.compare_times(mongodb_delete_time, mysql_delete_time)

                index_type_name = folder.split('_', 1)[1] if '_' in folder else folder
                formatted_index_type = cls.prettify_index_type(index_type_name)

                writer.writerow([
                    formatted_index_type,
                    f"{mongodb_insert_time:.2f}", f"{mongodb_fetch_time:.2f}", f"{mongodb_update_time:.2f}", f"{mongodb_delete_time:.2f}",
                    f"{mysql_insert_time:.2f}", f"{mysql_fetch_time:.2f}", f"{mysql_update_time:.2f}", f"{mysql_delete_time:.2f}",
                    insert_cmp, fetch_cmp, update_cmp, delete_cmp
                ])

                summary_lines.extend([
                    f"Typ indeksu: {formatted_index_type}",
                    f"  MongoDB Insert: {mongodb_insert_time:.2f} ms", f"  MongoDB Fetch: {mongodb_fetch_time:.2f} ms",
                    f"  MongoDB Update: {mongodb_update_time:.2f} ms", f"  MongoDB Delete: {mongodb_delete_time:.2f} ms",
                    f"  MySQL Insert:  {mysql_insert_time:.2f} ms", f"  MySQL Fetch:  {mysql_fetch_time:.2f} ms",
                    f"  MySQL Update:  {mysql_update_time:.2f} ms", f"  MySQL Delete:  {mysql_delete_time:.2f} ms"
                ])

                for label, comparison in zip(["Insert", "Fetch", "Update", "Delete"], [insert_cmp, fetch_cmp, update_cmp, delete_cmp]):
                    if comparison != 'N/A':
                        summary_lines.append(f"  {label}: {comparison}")

                summary_lines.extend(["", "-" * 80, ""])

            txt_file.write("\n".join(summary_lines))

        ProgressLogger.important_info(f"CSV summary saved to: {csv_output}")
        ProgressLogger.important_info(f"TXT summary saved to: {txt_output}")


def generate_summary(results_folder: str) -> None:
    parsed_date, parsed_time, record_count = ReportGenerator.parse_folder_name(results_folder)
    if parsed_date and record_count:
        ReportGenerator.generate_summary(results_folder, parsed_date, parsed_time, record_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generuje podsumowania dla folderów z wynikami testów.')
    parser.add_argument('--folder', type=str)
    parser.add_argument('--type', type=str, choices=['standard', 'main', 'all'], default='all')
    args = parser.parse_args()

    if args.folder:
        if args.type in ['standard', 'all']:
            parsed_date, parsed_time, record_count = ReportGenerator.parse_folder_name(args.folder)
            if parsed_date:
                ReportGenerator.generate_summary(args.folder, parsed_date, parsed_time, record_count)
    else:
        base_dir = 'results'
        if os.path.exists(base_dir):
            all_folders = sorted([f for f in os.listdir(base_dir) if f.startswith('results_')], reverse=True)
            if all_folders:
                latest_folder = all_folders[0]
                ProgressLogger.print(f"Używam najnowszego folderu: {latest_folder}")
                parsed_date, parsed_time, record_count = ReportGenerator.parse_folder_name(latest_folder)
                if args.type in ['standard', 'all'] and parsed_date:
                    ReportGenerator.generate_summary(latest_folder, parsed_date, parsed_time, record_count)
