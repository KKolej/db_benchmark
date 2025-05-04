import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv
import gc

from database.utils.logging_config import (
    set_current_iteration, configure_logging, ProgressLogger
)
from database.common.index_types import IndexType
from database.common.record_types import RecordType
from database.common.config_manager import ConfigManager
from database.test_runner import TestRunner


def main():
    set_current_iteration(0)

    import resource
    resource.setrlimit(resource.RLIMIT_AS, (18 * 1024 * 1024 * 1024, -1))

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(project_root, '.env'))
    parser = argparse.ArgumentParser(description='Database Performance Comparison')
    parser.add_argument('--records', type=int, default=500000, help='Number of records per client')
    parser.add_argument('--batch-size', type=int, default=5000, help='Batch size for data operations')
    parser.add_argument('--clients', type=int, default=2, help='Number of parallel clients')
    parser.add_argument('--iterations', type=int, default=2, help='Number of test iterations')
    parser.add_argument('--mysql-pool-size', type=int, default=20, help='MySQL connection pool size')
    parser.add_argument('--mongo-pool-size', type=int, default=125, help='MongoDB connection pool size')
    parser.add_argument('--log-progress', type=str, default='True', help='Show progress (True/False)')
    parser.add_argument('--indexes-type', type=str, default=IndexType.ALL.value,
                        help=f'Index type ({", ".join([t.value for t in IndexType])})')
    parser.add_argument('--record-type', type=str, default=RecordType.BIG.value,
                        help=f'Record type ({RecordType.BIG.value}/{RecordType.SMALL.value}). Big records contain full personal data, small records contain only numeric value and client_id')
    parser.add_argument('--test-update', type=str, default='True', help='Test update operations (True/False)')

    args = parser.parse_args()

    config_manager = ConfigManager(
        mysql_pool_size=args.mysql_pool_size,
        mongodb_pool_size=args.mongo_pool_size,
        records=args.records,
        batch_size=args.batch_size,
        clients=args.clients,
        iterations=args.iterations,
        show_progress=args.log_progress,
        indexes_type=args.indexes_type,
        record_type=args.record_type,
        test_update=args.test_update,
    )

    show_progress = config_manager.get('show_progress')
    configure_logging(show_progress=show_progress)

    iterations = config_manager.get('iterations')
    records = config_manager.get('records')
    indexes_type = config_manager.get('indexes_type')
    batch_size = config_manager.get('batch_size')

    runner = TestRunner(
        config_manager=config_manager,
        total_records=records,
        iterations=iterations,
        index_types=indexes_type,
        max_batch_size=batch_size,
        show_progress=show_progress,
    )

    try:
        runner.run()
        runner.close()
        gc.collect()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(base_dir)
        results_dir = os.path.join(project_dir, 'results')

        if not os.path.exists(results_dir):
            possible_paths = [
                os.path.join(os.getcwd(), 'results'),
                os.path.join(os.path.dirname(os.getcwd()), 'results')
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    results_dir = path
                    break

        if os.path.exists(results_dir):
            results_folders = [
                f for f in os.listdir(results_dir)
                if f.startswith('results_') and os.path.isdir(os.path.join(results_dir, f))
            ]

            if results_folders:
                latest_folder = max(results_folders)
                reports_script = os.path.join(base_dir, 'generate_reports.py')

                if os.path.exists(reports_script):
                    full_path = os.path.join(results_dir, latest_folder)
                    ProgressLogger.important_info(f"Running: {sys.executable} {reports_script} --folder {full_path} --type all")
                    result = subprocess.run(
                        [sys.executable, reports_script, '--folder', full_path, '--type', 'all'],
                        capture_output=True, text=True
                    )
                    if result.stdout:
                        ProgressLogger.print(f"Result: {result.stdout}")

                gc.collect()

    except Exception as e:
        ProgressLogger.error(f"Error generating summaries: {e}")


if __name__ == "__main__":
    main()
