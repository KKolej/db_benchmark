import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

matplotlib.use('Agg')


class ChartGenerator:

    @staticmethod
    def _add_labels(bar_objects):
        for bar in bar_objects:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.005, f'{height:.3f}', ha='center', va='bottom',
                     fontsize=9)

    @staticmethod
    def _generate_comparison_text(operations, mysql_avg_times, mongodb_avg_times):
        comparison_texts = []
        for operation, mysql_time, mongodb_time in zip(operations, mysql_avg_times, mongodb_avg_times):
            if mysql_time > 0 and mongodb_time > 0:
                if mysql_time > mongodb_time:
                    comparison_texts.append(
                        f'{operation}: MongoDB szybszy o {(mysql_time / mongodb_time - 1) * 100:.2f}% (MySQL:{mysql_time:.3f},MongoDB:{mongodb_time:.3f})')
                elif mongodb_time > mysql_time:
                    comparison_texts.append(
                        f'{operation}: MySQL szybszy o {(mongodb_time / mysql_time - 1) * 100:.2f}% (MySQL:{mysql_time:.3f},MongoDB:{mongodb_time:.3f})')
                else:
                    comparison_texts.append(f'{operation}: Identyczny czas')
        return comparison_texts

    @staticmethod
    def generate_standard_chart(df: pd.DataFrame, output_path: str) -> None:
        fig, ax = plt.subplots(figsize=(12, 8))
        avg_time_data = df.groupby(['database', 'operation'])['time'].mean().reset_index()
        operations = sorted(avg_time_data['operation'].unique())
        databases = sorted(avg_time_data['database'].unique())
        x_positions = np.arange(len(operations))
        bar_width = 0.35
        mysql_avg_times = []
        mongodb_avg_times = []
        for i, database in enumerate(databases):
            avg_times = [
                avg_time_data[(avg_time_data['database'] == database) & (avg_time_data['operation'] == operation)][
                    'time'].iloc[0] if not avg_time_data[
                    (avg_time_data['database'] == database) & (avg_time_data['operation'] == operation)].empty else 0
                for operation in operations]
            if database == 'MySQL':
                mysql_avg_times = avg_times
            if database == 'MongoDB':
                mongodb_avg_times = avg_times
            bar_objects = ax.bar(x_positions - bar_width / 2 + i * bar_width, avg_times, bar_width, label=database)
            ChartGenerator._add_labels(bar_objects)
        ax.set_xlabel('Operacja')
        ax.set_ylabel('Czas (ms)')
        index_type = df['indexes_type'].iat[0] if not df.empty else ''
        num_records = df['records'].iat[0] if not df.empty else 0
        max_iteration = df['iteration'].max() if not df.empty else 1
        ax.set_title(f'Porownanie - {index_type.replace("_", " ").upper()}  records number: {num_records} iterations:{max_iteration}')
        ax.set_xticks(x_positions)
        ax.set_xticklabels(operations)
        ax.legend()
        comparison_text = ChartGenerator._generate_comparison_text(operations, mysql_avg_times, mongodb_avg_times)
        plt.figtext(0.5, 0.01, '', ha='center', fontsize=10,
                    bbox={'facecolor': 'lightgray', 'alpha': 0.5, 'pad': 5})
        plt.tight_layout(rect=[0, 0.1, 1, 0.95])
        plt.savefig(output_path)
        plt.close(fig)

    @staticmethod
    def generate_histogram_chart(df: pd.DataFrame, output_path: str) -> None:
        operations = sorted(df['operation'].unique())
        databases = sorted(df['database'].unique())
        fig, axs = plt.subplots(len(operations), 1, figsize=(12, 6 * len(operations)))
        if len(operations) == 1:
            axs = [axs]
        for i, operation in enumerate(operations):
            for database in databases:
                execution_times = df[(df['database'] == database) & (df['operation'] == operation)]['time']
                if not execution_times.empty:
                    axs[i].hist(execution_times, bins=20, alpha=0.5, label=database)
            axs[i].set_title(operation)
            axs[i].set_xlabel('Czas (ms)')
            axs[i].set_ylabel('Ilość operacji')
            axs[i].legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close(fig)

    @staticmethod
    def generate_iterations_comparison_chart(df: pd.DataFrame, output_path: str) -> None:
        operations = sorted(df['operation'].unique())
        databases = sorted(df['database'].unique())
        iterations = sorted(df['iteration'].unique())
        fig, axs = plt.subplots(len(operations), 1, figsize=(14, 6 * len(operations)))
        if len(operations) == 1:
            axs = [axs]
        for i, operation in enumerate(operations):
            for database in databases:
                filtered_data = df[(df['database'] == database) & (df['operation'] == operation)].sort_values(
                    'iteration')
                if not filtered_data.empty:
                    axs[i].plot(filtered_data['iteration'], filtered_data['time'], marker='o', label=database)
            axs[i].set_title(operation)
            axs[i].set_xlabel('Iteracja')
            axs[i].set_ylabel('Czas (ms)')
            axs[i].legend()
            axs[i].grid(True)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close(fig)

    @staticmethod
    def generate_clients_comparison_chart(results: List[Dict], output_path: str,
                                          database_name: Optional[str] = None) -> None:
        if not results:
            return
        client_ids = sorted({r['client_id'] for r in results})
        iterations = sorted({r.get('iteration', 1) for r in results})
        fig, ax = plt.subplots(figsize=(14, 8))
        marker_styles = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'X', 'd']
        for idx, client_id in enumerate(client_ids):
            client_times = [
                next((r['time'] for r in results if r['client_id'] == client_id and r.get('iteration', 1) == iteration),
                     0) for iteration in iterations]
            ax.plot(iterations, client_times, marker=marker_styles[idx % len(marker_styles)],
                    label=f'Klient {client_id}')
        ax.set_xlabel('Iteracja')
        ax.set_ylabel('Czas (ms)')
        ax.set_title(f'Klienci {database_name}')
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close(fig)
