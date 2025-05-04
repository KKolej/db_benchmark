import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

class ChartGenerator:
    @staticmethod
    def _add_labels(bars):
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, h + 0.005, f'{h:.3f}', ha='center', va='bottom', fontsize=9)

    @staticmethod
    def generate_standard_chart(df: pd.DataFrame, path: str) -> None:
        fig, ax = plt.subplots(figsize=(12, 8))
        data = df.groupby(['database','operation'])['time'].mean().reset_index()
        ops = sorted(data['operation'].unique())
        dbs = sorted(data['database'].unique())
        x = np.arange(len(ops)); w = 0.35
        mysql_times = []; mongo_times = []
        for i, db in enumerate(dbs):
            times = [data[(data['database']==db)&(data['operation']==op)]['time'].iloc[0] if not data[(data['database']==db)&(data['operation']==op)].empty else 0 for op in ops]
            if db=='MySQL': mysql_times = times
            if db=='MongoDB': mongo_times = times
            bars = ax.bar(x - w/2 + i*w, times, w, label=db)
            ChartGenerator._add_labels(bars)
        ax.set_xlabel('Operacja'); ax.set_ylabel('Czas (ms)')
        idx = df['indexes_type'].iat[0] if not df.empty else ''
        th = df['threads'].iat[0] if not df.empty else 1
        rec = df['records'].iat[0] if not df.empty else 0
        it = df['iteration'].max() if not df.empty else 1
        ax.set_title(f'Porównanie - {idx.replace("_"," ").upper()} (rek:{rec*th}, wątki:{th}, it:{it})')
        ax.set_xticks(x); ax.set_xticklabels(ops)
        ax.legend()
        text = []
        for op, m, n in zip(ops, mysql_times, mongo_times):
            if m>0 and n>0:
                if m>n:
                    text.append(f'{op}: MongoDB szybszy o {(m/n-1)*100:.2f}% (MySQL:{m:.3f},MongoDB:{n:.3f})')
                elif n>m:
                    text.append(f'{op}: MySQL szybszy o {(n/m-1)*100:.2f}% (MySQL:{m:.3f},MongoDB:{n:.3f})')
                else:
                    text.append(f'{op}: Identyczny czas')
        plt.figtext(0.5,0.01,'; '.join(text), ha='center', fontsize=10, bbox={'facecolor':'lightgray','alpha':0.5,'pad':5})
        plt.tight_layout(rect=[0,0.1,1,0.95]); plt.savefig(path); plt.close('all')

    @staticmethod
    def generate_histogram_chart(df: pd.DataFrame, path: str) -> None:
        ops = sorted(df['operation'].unique()); dbs = sorted(df['database'].unique())
        fig, axs = plt.subplots(len(ops),1,figsize=(12,6*len(ops)))
        if len(ops)==1: axs=[axs]
        for i, op in enumerate(ops):
            for db in dbs:
                data = df[(df['database']==db)&(df['operation']==op)]['time']
                if not data.empty: axs[i].hist(data, bins=20, alpha=0.5, label=db)
            axs[i].set_title(op); axs[i].set_xlabel('Czas (ms)'); axs[i].set_ylabel('Liczba'); axs[i].legend()
        plt.tight_layout(); plt.savefig(path); plt.close('all')

    @staticmethod
    def generate_iterations_comparison_chart(df: pd.DataFrame, path: str) -> None:
        ops = sorted(df['operation'].unique()); dbs = sorted(df['database'].unique()); its = sorted(df['iteration'].unique())
        fig, axs = plt.subplots(len(ops),1,figsize=(14,6*len(ops)))
        if len(ops)==1: axs=[axs]
        for i, op in enumerate(ops):
            for db in dbs:
                sub = df[(df['database']==db)&(df['operation']==op)].sort_values('iteration')
                if not sub.empty: axs[i].plot(sub['iteration'], sub['time'], marker='o', label=db)
            axs[i].set_title(op); axs[i].set_xlabel('Iteracja'); axs[i].set_ylabel('Czas (ms)'); axs[i].legend(); axs[i].grid(True)
        plt.tight_layout(); plt.savefig(path); plt.close('all')

    @staticmethod
    def generate_clients_comparison_chart(results: List[Dict], path: str, db_name: Optional[str]=None) -> None:
        if not results: return
        clients = sorted({r['client_id'] for r in results}); its = sorted({r.get('iteration',1) for r in results})
        fig, ax = plt.subplots(figsize=(14,8))
        markers = ['o','s','^','D','v']
        for idx, c in enumerate(clients):
            times = [next((r['time'] for r in results if r['client_id']==c and r.get('iteration',1)==it),0) for it in its]
            ax.plot(its, times, marker=markers[idx%len(markers)], label=f'Klient {c}')
        ax.set_xlabel('Iteracja'); ax.set_ylabel('Czas (ms)'); ax.set_title(f'Klienci {db_name}'); ax.legend(); ax.grid(True)
        plt.tight_layout(); plt.savefig(path); plt.close('all')
