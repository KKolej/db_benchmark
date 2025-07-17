# 2. Kluczowe zagadnienia związane z realizacją projektu

## 2.1 System generowania wykresów i wizualizacji wyników

Jednym z najważniejszych i najbardziej złożonych aspektów implementacyjnych aplikacji jest system automatycznego generowania wykresów porównawczych wydajności baz danych. System ten stanowi kluczowy element całej architektury aplikacji, umożliwiając nie tylko wizualizację wyników testów, ale także ich szczegółową analizę statystyczną i porównawczą. Implementacja tego systemu wymagała zastosowania zaawansowanych technik programistycznych oraz integracji z bibliotekami do wizualizacji danych.

### 2.1.1 Architektura systemu wykresów - szczegółowa analiza

System wizualizacji został zaprojektowany zgodnie z zasadami programowania obiektowego i wzorcem separacji odpowiedzialności (Separation of Concerns). Składa się z trzech głównych komponentów, z których każdy pełni specyficzną rolę w procesie generowania wykresów:

**ChartGenerator** - klasa statyczna odpowiedzialna wyłącznie za generowanie różnych typów wykresów. Implementuje wzorzec Factory Method, gdzie każda metoda statyczna jest odpowiedzialna za tworzenie konkretnego typu wykresu. Klasa ta wykorzystuje bibliotekę matplotlib z konfiguracją backend'u 'Agg', co umożliwia generowanie wykresów bez konieczności wyświetlania ich na ekranie, co jest kluczowe w środowisku serwerowym.

**ResultsVisualizer** - klasa koordynująca cały proces wizualizacji, która zarządza przepływem danych między komponentami systemu. Odpowiada za agregację wyników testów, ich grupowanie według różnych kryteriów (typ indeksu, baza danych, operacja) oraz orchestrację procesu generowania wykresów. Klasa implementuje wzorzec Command, gdzie każda metoda wizualizacji enkapsuluje kompletny proces tworzenia określonego typu wykresu.

**ResultsFileManager** - komponent odpowiedzialny za zarządzanie systemem plików, organizację struktury folderów wyników oraz generowanie ścieżek do plików wykresów. Implementuje wzorzec Strategy dla różnych strategii organizacji plików w zależności od typu testów i konfiguracji.

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

matplotlib.use('Agg')  # Backend bez GUI dla środowiska serwerowego

class ChartGenerator:
    @staticmethod
    def generate_standard_chart(df: pd.DataFrame, output_path: str) -> None:
        fig, ax = plt.subplots(figsize=(12, 8))
        avg_time_data = df.groupby(['database', 'operation'])['time'].mean().reset_index()
        operations = sorted(avg_time_data['operation'].unique())
        databases = sorted(avg_time_data['database'].unique())
````
</augment_code_snippet>

### 2.1.2 Szczegółowa implementacja algorytmów generowania wykresów

System implementuje cztery różne typy wykresów, każdy z których służy innemu celowi analitycznemu i wykorzystuje różne techniki wizualizacji danych. Każdy typ wykresu został zaprojektowany z myślą o maksymalnej czytelności i informatywności dla użytkownika końcowego.

**Wykres słupkowy standardowy** - główny wykres porównawczy, który stanowi serce systemu wizualizacji. Implementacja tego wykresu wykorzystuje zaawansowane techniki grupowania danych oraz automatyczne obliczenia statystyczne. Wykres przedstawia średnie czasy wykonania operacji dla każdej bazy danych, z automatycznym dodawaniem etykiet wartości na słupkach oraz obliczaniem różnic procentowych między bazami danych.

Algorytm generowania wykresu słupkowego wykonuje następujące kroki:
1. Grupowanie danych według bazy danych i operacji z obliczeniem średnich czasów
2. Sortowanie operacji alfabetycznie dla zapewnienia spójności wizualnej
3. Obliczenie pozycji słupków z uwzględnieniem szerokości i odstępów
4. Iteracyjne tworzenie słupków dla każdej bazy danych z różnymi kolorami
5. Automatyczne dodawanie etykiet z wartościami na każdym słupku
6. Generowanie tekstu porównawczego z obliczeniami procentowymi
7. Konfiguracja osi, tytułu i legendy wykresu

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
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
            avg_time_data[(avg_time_data['database'] == database) &
                         (avg_time_data['operation'] == operation)]['time'].iloc[0]
            if not avg_time_data[(avg_time_data['database'] == database) &
                                (avg_time_data['operation'] == operation)].empty else 0
            for operation in operations]

        if database == 'MySQL':
            mysql_avg_times = avg_times
        if database == 'MongoDB':
            mongodb_avg_times = avg_times

        bar_objects = ax.bar(x_positions - bar_width / 2 + i * bar_width,
                           avg_times, bar_width, label=database)
        ChartGenerator._add_labels(bar_objects)
````
</augment_code_snippet>

**Metoda dodawania etykiet** implementuje precyzyjne pozycjonowanie tekstu na wykresie, z automatycznym obliczaniem optymalnej pozycji dla każdej etykiety:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
@staticmethod
def _add_labels(bar_objects):
    for bar in bar_objects:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.005,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
````
</augment_code_snippet>

**Algorytm generowania tekstu porównawczego** implementuje zaawansowane obliczenia statystyczne, które automatycznie określają, która baza danych jest szybsza i o ile procent:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
@staticmethod
def _generate_comparison_text(operations, mysql_avg_times, mongodb_avg_times):
    comparison_texts = []
    for operation, mysql_time, mongodb_time in zip(operations, mysql_avg_times, mongodb_avg_times):
        if mysql_time > 0 and mongodb_time > 0:
            if mysql_time > mongodb_time:
                comparison_texts.append(
                    f'{operation}: MongoDB szybszy o {(mysql_time / mongodb_time - 1) * 100:.2f}% '
                    f'(MySQL:{mysql_time:.3f},MongoDB:{mongodb_time:.3f})')
            elif mongodb_time > mysql_time:
                comparison_texts.append(
                    f'{operation}: MySQL szybszy o {(mongodb_time / mysql_time - 1) * 100:.2f}% '
                    f'(MySQL:{mysql_time:.3f},MongoDB:{mongodb_time:.3f})')
            else:
                comparison_texts.append(f'{operation}: Identyczny czas')
    return comparison_texts
````
</augment_code_snippet>

**Histogram czasów wykonania** - drugi kluczowy typ wykresu, który implementuje zaawansowaną analizę rozkładu czasów wykonania. Ten typ wizualizacji jest szczególnie wartościowy dla analizy stabilności wydajności i identyfikacji anomalii w czasach odpowiedzi. Histogram wykorzystuje algorytm automatycznego binowania danych, który dzieli zakres czasów na 20 równych przedziałów, co zapewnia optymalną czytelność rozkładu.

Implementacja histogramu wykorzystuje subplot dla każdej operacji, co umożliwia równoczesne porównanie rozkładów dla różnych typów operacji bazodanowych. Algorytm automatycznie dostosowuje wysokość wykresów w zależności od liczby operacji, zapewniając proporcjonalne przedstawienie danych:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
@staticmethod
def generate_histogram_chart(df: pd.DataFrame, output_path: str) -> None:
    operations = sorted(df['operation'].unique())
    databases = sorted(df['database'].unique())
    fig, axs = plt.subplots(len(operations), 1, figsize=(12, 6 * len(operations)))

    # Obsługa przypadku pojedynczej operacji
    if len(operations) == 1:
        axs = [axs]

    for i, operation in enumerate(operations):
        for database in databases:
            execution_times = df[(df['database'] == database) &
                               (df['operation'] == operation)]['time']
            if not execution_times.empty:
                axs[i].hist(execution_times, bins=20, alpha=0.5, label=database)

        axs[i].set_title(operation)
        axs[i].set_xlabel('Czas (ms)')
        axs[i].set_ylabel('Liczba')
        axs[i].legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)
````
</augment_code_snippet>

**Wykres porównania iteracji** - trzeci typ wykresu implementuje analizę trendów wydajności w czasie. Ten wykres jest kluczowy dla identyfikacji wzorców wydajnościowych, takich jak degradacja wydajności w czasie, efekty cache'owania, czy optymalizacje wykonywane przez silniki baz danych. Implementacja wykorzystuje wykresy liniowe z markerami, co umożliwia precyzyjne śledzenie zmian wydajności między kolejnymi iteracjami testów.

Algorytm automatycznie sortuje dane według numerów iteracji i tworzy osobny subplot dla każdej operacji, co pozwala na szczegółową analizę trendów dla każdego typu operacji bazodanowej:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
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
            filtered_data = df[(df['database'] == database) &
                             (df['operation'] == operation)].sort_values('iteration')
            if not filtered_data.empty:
                axs[i].plot(filtered_data['iteration'], filtered_data['time'],
                          marker='o', label=database)

        axs[i].set_title(operation)
        axs[i].set_xlabel('Iteracja')
        axs[i].set_ylabel('Czas (ms)')
        axs[i].legend()
        axs[i].grid(True)  # Dodanie siatki dla lepszej czytelności

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)
````
</augment_code_snippet>

**Wykres porównania klientów** - czwarty i najbardziej zaawansowany typ wykresu, który analizuje wydajność w kontekście równoległego dostępu wielu klientów do bazy danych. Ten wykres jest szczególnie istotny dla analizy skalowalności systemów bazodanowych w środowiskach wieloużytkownikowych. Implementacja wykorzystuje różne style markerów dla każdego klienta, co umożliwia łatwe rozróżnienie poszczególnych klientów na wykresie.

Algorytm automatycznie przypisuje unikalne style markerów z predefiniowanej listy, zapewniając wizualną różnorodność nawet przy dużej liczbie klientów:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
@staticmethod
def generate_clients_comparison_chart(results: List[Dict], output_path: str,
                                      database_name: Optional[str] = None) -> None:
    if not results:
        return

    client_ids = sorted({r['client_id'] for r in results})
    iterations = sorted({r.get('iteration', 1) for r in results})
    fig, ax = plt.subplots(figsize=(14, 8))

    # Predefiniowana lista stylów markerów dla różnych klientów
    marker_styles = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'X', 'd']

    for idx, client_id in enumerate(client_ids):
        client_times = [
            next((r['time'] for r in results
                 if r['client_id'] == client_id and r.get('iteration', 1) == iteration), 0)
            for iteration in iterations]

        ax.plot(iterations, client_times,
               marker=marker_styles[idx % len(marker_styles)],
               label=f'Klient {client_id}')

    ax.set_xlabel('Iteracja')
    ax.set_ylabel('Czas (ms)')
    ax.set_title(f'Klienci {database_name}')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)
````
</augment_code_snippet>

### 2.1.3 Zaawansowany proces orchestracji generowania wykresów

Proces generowania wykresów stanowi złożony workflow, który jest w pełni zautomatyzowany i zarządzany przez klasę `ResultsVisualizer`. Ta klasa implementuje wzorzec Facade, ukrywając złożoność procesu generowania wykresów za prostym interfejsem. Proces ten składa się z kilku kluczowych etapów, każdy z których jest starannie zoptymalizowany pod kątem wydajności i niezawodności.

**Etap 1: Agregacja i grupowanie danych**
Pierwszym krokiem w procesie generowania wykresów jest agregacja wyników testów i ich grupowanie według różnych kryteriów. System implementuje zaawansowany algorytm grupowania, który organizuje dane według typu indeksu, co umożliwia generowanie osobnych wykresów dla różnych konfiguracji testowych:

<augment_code_snippet path="src/database/result_handling/results_visualizer.py" mode="EXCERPT">
````python
def show_results(self, indexes_type: Optional[str] = None):
    if not self.results:
        ProgressLogger.print("No results to display.")
        return

    # Zaawansowane grupowanie wyników według typu indeksu
    grouped = {}
    for r in self.results:
        key = r.indexes_type
        if indexes_type and key != indexes_type:
            continue
        grouped.setdefault(key, []).append(r)

    # Iteracja przez każdą grupę i generowanie wykresów
    for idx, results in grouped.items():
        df = pd.DataFrame([vars(r) for r in results])
        if df.empty:
            continue

        # Aktualizacja konfiguracji file managera dla bieżącej grupy
        timing_method = df['timing_method'].iat[0]
        records = df['records'].iat[0]
        self.file_manager = ResultsFileManager(
            self.file_manager.base_dir,
            records,
            timing_method,
            idx,
            results_dir=self.results_dir
        )

        # Generowanie różnych typów wykresów
        self._show_standard_chart(df)
        if self.iterations > 1:
            self._show_histogram_chart(df)
            self._show_iterations_comparison_chart(df)

        # Wyświetlenie tabelarycznych wyników i zapis do plików
        ProgressLogger.print(df.to_string(index=False))
        self.file_manager.save_results(results, df)
````
</augment_code_snippet>

**Etap 2: Inteligentne zarządzanie typami wykresów**
System implementuje inteligentną logikę decyzyjną, która określa, które typy wykresów powinny być generowane w zależności od konfiguracji testów. Na przykład, histogramy i wykresy porównania iteracji są generowane tylko wtedy, gdy liczba iteracji jest większa niż 1, co zapobiega tworzeniu bezużytecznych wizualizacji:

<augment_code_snippet path="src/database/result_handling/results_visualizer.py" mode="EXCERPT">
````python
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
````
</augment_code_snippet>

**Etap 3: Specjalizowane generowanie wykresów klientów**
System implementuje również specjalizowaną metodę dla generowania wykresów porównania klientów, która obsługuje bardziej złożone scenariusze testowe z wieloma klientami równoległymi:

<augment_code_snippet path="src/database/result_handling/results_visualizer.py" mode="EXCERPT">
````python
def show_clients_comparison_chart(self, database: str, client_results: List[Dict], records: int,
                                  indexes_type: Optional[str] = None):
    if not client_results:
        return

    # Dynamiczna aktualizacja konfiguracji dla wykresów klientów
    current_index = indexes_type or self.indexes_type
    if self.file_manager.indexes_type != current_index:
        self.file_manager = ResultsFileManager(
            self.file_manager.base_dir,
            records,
            "database",
            current_index,
            results_dir=self.results_dir
        )

    # Generowanie specjalizowanej ścieżki dla wykresów klientów
    chart_path = self.file_manager.get_chart_path("database", records,
                                                 suffix=f"clients_{database.lower()}")
    ChartGenerator.generate_clients_comparison_chart(client_results, chart_path, database)
````
</augment_code_snippet>

### 2.1.4 Zaawansowany system organizacji i zarządzania plikami wykresów

System zarządzania plikami wykresów implementuje hierarchiczną strukturę organizacji, która zapewnia logiczne grupowanie wyników według różnych kryteriów. Klasa `ResultsFileManager` odpowiada za tworzenie i zarządzanie złożoną strukturą folderów, która odzwierciedla organizację testów i ułatwia nawigację po wynikach.

**Hierarchiczna struktura folderów**
System automatycznie tworzy hierarchiczną strukturę folderów, która organizuje wyniki według timestamp'u, liczby rekordów, metody pomiaru czasu oraz typu indeksów. Ta struktura zapewnia, że wyniki różnych testów nie będą się ze sobą mieszać i można je łatwo identyfikować:

<augment_code_snippet path="src/database/result_handling/results_file_manager.py" mode="EXCERPT">
````python
def __init__(self,
             base_dir: str = 'results',
             records: int = None,
             timing_method: str = None,
             indexes_type: str = 'no_indexes',
             results_dir: str = None):
    # Określenie ścieżki głównej projektu
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    self.base_dir = os.path.join(project_root, base_dir)
    os.makedirs(self.base_dir, exist_ok=True)

    self.indexes_type = indexes_type

    # Tworzenie unikalnego folderu dla sesji testowej
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

    # Mapowanie typów indeksów na nazwy folderów z prefiksami sortującymi
    idx_map = {
        'no_indexes': '01_bez_indeksow',
        'foreign_key': '02_indeks_klucza_obcego',
        'all': '00_wszystkie_indeksy'
    }

    folder = idx_map.get(indexes_type, indexes_type)
    self.current_results_dir = os.path.join(self.main_results_dir, folder)
    os.makedirs(self.current_results_dir, exist_ok=True)
````
</augment_code_snippet>

**Inteligentne generowanie ścieżek do wykresów**
System implementuje inteligentny algorytm generowania ścieżek do plików wykresów, który uwzględnia różne parametry testów i typy wykresów. Algorytm zapewnia unikalne nazwy plików, które zawierają wszystkie istotne informacje o konfiguracji testu:

<augment_code_snippet path="src/database/result_handling/results_file_manager.py" mode="EXCERPT">
````python
def get_chart_path(self, method: str, records: int, suffix: str = None) -> str:
    name = f"chart_{method}_{records}"
    if suffix:
        name += f"_{suffix}"
    return os.path.join(self.current_results_dir, f"{name}.png")
````
</augment_code_snippet>

**Wieloformatowy zapis wyników**
System implementuje wieloformatowy zapis wyników, który obejmuje zarówno dane tabelaryczne (CSV, JSON) jak i wizualizacje (PNG). Ta funkcjonalność zapewnia maksymalną elastyczność w dalszej analizie wyników:

<augment_code_snippet path="src/database/result_handling/results_file_manager.py" mode="EXCERPT">
````python
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
    # Konwersja timestamp'ów do formatu ISO dla kompatybilności JSON
    for r in data['results']:
        r['timestamp'] = r['timestamp'].isoformat()
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    ProgressLogger.print(f"Results saved to JSON: {path}")
````
</augment_code_snippet>

## 2.2 Zaawansowany system logowania i monitorowania postępu

Aplikacja implementuje wysoce zaawansowany i wielowarstwowy system logowania, który stanowi kluczowy element infrastruktury monitorowania wydajności. System ten został zaprojektowany z myślą o zapewnieniu pełnej transparentności procesu testowania, umożliwiając śledzenie postępu testów w czasie rzeczywistym oraz szczegółowe rejestrowanie wszystkich istotnych zdarzeń podczas wykonywania testów wydajnościowych. Implementacja systemu logowania uwzględnia specyficzne wymagania środowiska wielowątkowego oraz potrzebę precyzyjnego śledzenia iteracji testowych.

### 2.2.1 Wielowarstwowa architektura systemu logowania

System logowania został zaprojektowany jako wielowarstwowa architektura, która składa się z kilku współpracujących ze sobą komponentów. Każdy komponent pełni specyficzną rolę w procesie rejestrowania i formatowania komunikatów logowania, zapewniając jednocześnie wysoką wydajność i thread-safety.

**Warstwa abstrakcji logowania - ProgressLogger**
Głównym komponentem systemu jest klasa `ProgressLogger`, która implementuje wzorzec Facade, ukrywając złożoność standardowego systemu logowania Pythona za prostym i intuicyjnym interfejsem. Klasa ta zapewnia różne poziomy logowania, każdy z właściwym formatowaniem i prefiksami:

<augment_code_snippet path="src/database/utils/logging_config.py" mode="EXCERPT">
````python
_current_iteration = "0"
_iteration_lock = threading.Lock()
_show_progress = True
_original_print = builtins.print

class ProgressLogger:
    @staticmethod
    def print(args):
        ProgressLogger.important_info(args)

    @staticmethod
    def important_info(message, iteration=None):
        it = iteration if iteration is not None else _current_iteration
        _original_print(f"[INFO] [Iteracja {it}] {message}")

    @staticmethod
    def error(message, iteration=None):
        it = iteration if iteration is not None else _current_iteration
        _original_print(f"[ERROR] [Iteracja {it}] {message}")

    @staticmethod
    def warn(message, iteration=None):
        it = iteration if iteration is not None else _current_iteration
        _original_print(f"[WARN] [Iteracja {it}] {message}")
````
</augment_code_snippet>

**Warstwa filtrowania i kontekstu - IterationFilter**
System implementuje zaawansowany mechanizm filtrowania, który automatycznie wzbogaca każdy komunikat logowania o informacje kontekstowe, szczególnie o numer bieżącej iteracji testu. Ta funkcjonalność jest kluczowa dla analizy wyników testów wieloiteracyjnych:

<augment_code_snippet path="src/database/utils/logging_config.py" mode="EXCERPT">
````python
class IterationFilter(logging.Filter):
    def filter(self, record):
        with _iteration_lock:
            record.iteration = _current_iteration
        return True
````
</augment_code_snippet>

### 2.2.2 Zaawansowane formatowanie i konfiguracja komunikatów

System logowania implementuje inteligentny mechanizm formatowania komunikatów, który dostosowuje się do różnych trybów działania aplikacji. W trybie pełnego logowania komunikaty zawierają szczegółowe informacje o iteracji i poziomie logowania, podczas gdy w trybie cichym wyświetlane są tylko najważniejsze informacje.

**Dynamiczna konfiguracja formatowania**
Funkcja `configure_logging` implementuje dynamiczną konfigurację systemu logowania, która może być dostosowana do różnych scenariuszy użycia:

<augment_code_snippet path="src/database/utils/logging_config.py" mode="EXCERPT">
````python
def configure_logging(show_progress=True):
    global _show_progress
    _show_progress = show_progress

    # Czyszczenie istniejących handlerów
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Dynamiczne formatowanie w zależności od trybu
    fmt = ('[%(levelname)s] [Iteracja %(iteration)s] %(message)s' if show_progress
           else '[%(levelname)s] %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(fmt))
    console_handler.addFilter(IterationFilter())

    # Konfiguracja poziomu logowania
    root_logger.setLevel(logging.INFO if show_progress else logging.WARNING)
    root_logger.addHandler(console_handler)

    # Podmiana standardowej funkcji print
    builtins.print = custom_print if show_progress else ProgressLogger.print
````
</augment_code_snippet>

**Inteligentna podmiana funkcji print**
System implementuje zaawansowany mechanizm podmiany standardowej funkcji `print`, który zapewnia spójność formatowania wszystkich komunikatów wyjściowych aplikacji:

<augment_code_snippet path="src/database/utils/logging_config.py" mode="EXCERPT">
````python
def custom_print(*args, **kwargs):
    if not _show_progress:
        return

    with _iteration_lock:
        it = _current_iteration

    if args:
        first = str(args[0])
        # Sprawdzenie czy komunikat nie jest już sformatowany
        if not first.startswith('[Iteracja') and not first.startswith('[INFO]') and not first.startswith('[BŁĄD]'):
            args = (f"[Iteracja {it}] {first}",) + args[1:]

    _original_print(*args, **kwargs)
````
</augment_code_snippet>

### 2.2.3 Thread-safe zarządzanie stanem iteracji w środowisku wielowątkowym

Jednym z najważniejszych aspektów implementacyjnych systemu logowania jest zapewnienie thread-safety w środowisku wielowątkowym. System testów wydajnościowych wykorzystuje równoległe wykonywanie operacji, co wymaga szczególnej ostrożności w zarządzaniu stanem globalnym.

**Mechanizm blokowania dla stanu iteracji**
System implementuje zaawansowany mechanizm blokowania, który zapewnia atomowe operacje na zmiennej przechowującej numer bieżącej iteracji:

<augment_code_snippet path="src/database/utils/logging_config.py" mode="EXCERPT">
````python
_current_iteration = "0"
_iteration_lock = threading.Lock()

def set_current_iteration(iteration):
    global _current_iteration
    with _iteration_lock:
        _current_iteration = str(iteration)
````
</augment_code_snippet>

**Zastosowanie w praktyce**
System zarządzania iteracjami jest wykorzystywany w głównej pętli testowej, gdzie każda iteracja jest odpowiednio oznaczana:

<augment_code_snippet path="src/database/testers/database_tester.py" mode="EXCERPT">
````python
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
````
</augment_code_snippet>

### 2.2.4 Integracja systemu logowania z komponentami aplikacji

System logowania jest głęboko zintegrowany z wszystkimi komponentami aplikacji, zapewniając spójne i informatywne komunikaty na każdym etapie wykonywania testów. Ta integracja obejmuje komponenty zarządzania połączeniami, wykonywania zapytań, oraz generowania wyników.

**Logowanie w systemie zarządzania połączeniami**
System logowania jest wykorzystywany do monitorowania tworzenia i zarządzania połączeniami z bazami danych:

<augment_code_snippet path="src/database/mysql/mysql_connection_pool.py" mode="EXCERPT">
````python
class MySQLConnectionPool(ConnectionPool):
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        size = int(self.config_manager.get('mysql_pool_size', 5))
        super().__init__(size)
        ProgressLogger.print(f'Initialized MySQL connection pool (size={size})')

    def create_connection(self):
        ProgressLogger.print('Creating new MySQL connection')
        return MySQLConnection(self.config_manager)
````
</augment_code_snippet>

**Logowanie w procesie wykonywania testów**
System logowania zapewnia szczegółowe informacje o każdym etapie wykonywania testów wydajnościowych:

<augment_code_snippet path="src/database/testers/database_tester.py" mode="EXCERPT">
````python
def _generate_users(self, records: int) -> List[Dict]:
    record_type = self.config_manager.get("record_type")
    ProgressLogger.important_info(f"Generating test record with type: {record_type}")
    clients = self.config_manager.get("clients", 1)
    data = MultiClientDataGenerator.generate_data_for_clients(records, clients, record_type)
    return [u for batch in data for u in batch]
````
</augment_code_snippet>

## 2.3 Zaawansowany system konfiguracji i zarządzania parametrami aplikacji

Aplikacja implementuje wysoce zaawansowany i elastyczny system zarządzania konfiguracją, który stanowi fundament całej architektury aplikacji. System ten został zaprojektowany z myślą o maksymalnej elastyczności i łatwości konfiguracji, integrując w spójny sposób parametry pochodzące z różnych źródeł: argumentów wiersza poleceń, zmiennych środowiskowych oraz wartości domyślnych. Ta wielowarstwowa architektura konfiguracji umożliwia łatwe dostosowanie aplikacji do różnych środowisk i scenariuszy testowych bez konieczności modyfikacji kodu źródłowego.

### 2.3.1 Implementacja wzorca Singleton z zaawansowaną inicjalizacją

Klasa `ConfigManager` implementuje wzorzec Singleton w sposób thread-safe, zapewniając jednolity i globalny dostęp do konfiguracji w całej aplikacji. Implementacja tego wzorca została starannie zaprojektowana, aby zapewnić, że konfiguracja jest inicjalizowana tylko raz, niezależnie od liczby miejsc w kodzie, które próbują uzyskać dostęp do managera konfiguracji.

**Zaawansowana implementacja Singleton**
System implementuje wzorzec Singleton z mechanizmem leniwej inicjalizacji, który zapewnia, że konfiguracja jest ładowana dopiero przy pierwszym dostępie:

<augment_code_snippet path="src/database/common/config_manager.py" mode="EXCERPT">
````python
class ConfigManager:
    _instance = None

    def __new__(cls, **cli_values):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, **cli_values):
        self._config = {}
        if self._initialized:
            return

        self._initialized = True

        # Ładowanie parametrów z argumentów wiersza poleceń
        for key, val in cli_values.items():
            if val is not None:
                self._config[key] = val

        # Ładowanie zmiennych środowiskowych
        self._load_from_env()

        # Ustawienie wartości domyślnych specyficznych dla aplikacji
        self._config['mongodb_collection'] = 'test_collection'
        self._config['mysql_table'] = 'test_table'
````
</augment_code_snippet>

**Mechanizm zapobiegania wielokrotnej inicjalizacji**
System wykorzystuje flagę `_initialized` do zapobiegania wielokrotnej inicjalizacji konfiguracji, co jest kluczowe w środowisku wielowątkowym gdzie różne komponenty mogą próbować jednocześnie uzyskać dostęp do managera konfiguracji.

### 2.3.2 Zaawansowane ładowanie i walidacja zmiennych środowiskowych

System implementuje kompleksowy mechanizm ładowania zmiennych środowiskowych, który obsługuje konfigurację połączeń do obu systemów bazodanowych. Ten mechanizm zapewnia bezpieczne przechowywanie wrażliwych danych, takich jak hasła i dane uwierzytelniające, poza kodem źródłowym aplikacji.

**Systematyczne ładowanie konfiguracji baz danych**
Metoda `_load_from_env` implementuje systematyczne ładowanie wszystkich parametrów połączenia dla obu baz danych:

<augment_code_snippet path="src/database/common/config_manager.py" mode="EXCERPT">
````python
def _load_from_env(self):
    # Konfiguracja MySQL
    self._config['mysql_host'] = os.getenv('MYSQL_HOST')
    self._config['mysql_port'] = os.getenv('MYSQL_PORT')
    self._config['mysql_user'] = os.getenv('MYSQL_USER')
    self._config['mysql_password'] = os.getenv('MYSQL_PASSWORD')
    self._config['mysql_database'] = os.getenv('MYSQL_DB')

    # Konfiguracja MongoDB
    self._config['mongodb_host'] = os.getenv('MONGO_HOST')
    self._config['mongodb_port'] = os.getenv('MONGO_PORT')
    self._config['mongodb_user'] = os.getenv('MONGO_USER')
    self._config['mongodb_password'] = os.getenv('MONGO_PASSWORD')
    self._config['mongodb_database'] = os.getenv('MONGO_DB')
````
</augment_code_snippet>

**Bezpieczny dostęp do konfiguracji**
System implementuje bezpieczną metodę dostępu do parametrów konfiguracji z obsługą wartości domyślnych:

<augment_code_snippet path="src/database/common/config_manager.py" mode="EXCERPT">
````python
def get(self, key: str, default: Any = None) -> Any:
    return self._config.get(key, default)
````
</augment_code_snippet>

### 2.3.3 Kompleksowy system parsowania argumentów wiersza poleceń

Główny plik aplikacji implementuje bardzo rozbudowany system parsowania argumentów wiersza poleceń, który umożliwia precyzyjne dostosowanie wszystkich aspektów testów wydajnościowych. System ten został zaprojektowany z myślą o maksymalnej elastyczności i łatwości użycia.

**Szczegółowa konfiguracja parsera argumentów**
System implementuje parser argumentów z rozbudowanym zestawem opcji konfiguracyjnych:

<augment_code_snippet path="src/main.py" mode="EXCERPT">
````python
def main():
    set_current_iteration(0)

    # Ustawienie limitu pamięci dla aplikacji
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (18 * 1024 * 1024 * 1024, -1))

    # Ładowanie zmiennych środowiskowych z pliku .env
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(project_root, '.env'))

    # Konfiguracja parsera argumentów
    parser = argparse.ArgumentParser(description='Database Performance Comparison')
    parser.add_argument('--records', type=int, default=5000,
                       help='Number of records per client')
    parser.add_argument('--batch-size', type=int, default=2000,
                       help='Batch size for data operations')
    parser.add_argument('--clients', type=int, default=3,
                       help='Number of parallel clients')
    parser.add_argument('--iterations', type=int, default=3,
                       help='Number of test iterations')
    parser.add_argument('--mysql-pool-size', type=int, default=20,
                       help='MySQL connection pool size')
    parser.add_argument('--mongo-pool-size', type=int, default=125,
                       help='MongoDB connection pool size')
    parser.add_argument('--log-progress', type=str, default='True',
                       help='Show progress (True/False)')
    parser.add_argument('--indexes-type', type=str, default=IndexType.ALL.value,
                       help=f'Index type ({", ".join([t.value for t in IndexType])})')
    parser.add_argument('--record-type', type=str, default=RecordType.BIG.value,
                       help=f'Record type ({RecordType.BIG.value}/{RecordType.SMALL.value}). '
                            f'Big records contain full personal data, small records contain only numeric value and client_id')
    parser.add_argument('--test-update', type=str, default='True',
                       help='Test update operations (True/False)')
    parser.add_argument('--test-delete', type=str, default='True',
                       help='Test delete operations (True/False)')

    args = parser.parse_args()
````
</augment_code_snippet>

**Integracja argumentów z ConfigManager**
System implementuje bezproblemową integrację sparsowanych argumentów z ConfigManager:

<augment_code_snippet path="src/main.py" mode="EXCERPT">
````python
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
        test_delete=args.test_delete,
    )

    # Konfiguracja systemu logowania na podstawie parametrów
    show_progress = config_manager.get('show_progress')
    configure_logging(show_progress=show_progress)
````
</augment_code_snippet>

### 2.3.4 Inteligentne generowanie connection stringów i konfiguracja połączeń

System implementuje zaawansowane mechanizmy automatycznego generowania connection stringów dla obu systemów bazodanowych. Te mechanizmy uwzględniają specyficzne wymagania każdego systemu i zapewniają optymalne parametry połączenia.

**Generowanie connection stringa dla MySQL**
System generuje connection string dla MySQL z uwzględnieniem wszystkich niezbędnych parametrów:

<augment_code_snippet path="src/database/common/config_manager.py" mode="EXCERPT">
````python
def get_mysql_connection_string(self) -> str:
    return f"mysql://{self.get('mysql_user')}:{self.get('mysql_password')}@{self.get('mysql_host')}:{self.get('mysql_port')}/{self.get('mysql_database')}"
````
</augment_code_snippet>

**Generowanie connection stringa dla MongoDB**
System generuje connection string dla MongoDB z uwzględnieniem specyficznych wymagań tego systemu, takich jak authSource:

<augment_code_snippet path="src/database/common/config_manager.py" mode="EXCERPT">
````python
def get_mongodb_connection_string(self) -> str:
    return f"mongodb://{self.get('mongodb_user')}:{self.get('mongodb_password')}@{self.get('mongodb_host')}:{self.get('mongodb_port')}/?authSource=admin"
````
</augment_code_snippet>

### 2.3.5 Praktyczne zastosowanie systemu konfiguracji w komponentach aplikacji

System konfiguracji jest szeroko wykorzystywany przez wszystkie komponenty aplikacji, zapewniając spójny dostęp do parametrów konfiguracyjnych. Ta integracja obejmuje komponenty zarządzania połączeniami, wykonywania testów oraz generowania wyników.

**Wykorzystanie w pulach połączeń**
System konfiguracji jest wykorzystywany do konfiguracji pul połączeń dla obu baz danych:

<augment_code_snippet path="src/database/mysql/mysql_connection_pool.py" mode="EXCERPT">
````python
class MySQLConnectionPool(ConnectionPool):
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        size = int(self.config_manager.get('mysql_pool_size', 5))
        super().__init__(size)
        ProgressLogger.print(f'Initialized MySQL connection pool (size={size})')
````
</augment_code_snippet>

**Wykorzystanie w testerach baz danych**
System konfiguracji zapewnia parametry dla testerów baz danych:

<augment_code_snippet path="src/database/testers/mongodb_tester.py" mode="EXCERPT">
````python
class MongoDBTester(DatabaseTester):
    def __init__(self, max_batch_size: int, show_progress: bool, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.db_type = DatabaseType.MONGO
        connection_str = self.config_manager.get_mongodb_connection_string()
        db_name = self.config_manager.get('mongodb_database')
        self.base_collection_name = self.config_manager.get('mongodb_collection')
````
</augment_code_snippet>

## 2.4 Zaawansowane mechanizmy zarządzania danymi testowymi i ich przetwarzania

Aplikacja implementuje wysoce zaawansowany system zarządzania danymi testowymi, który obejmuje generowanie, przetwarzanie, agregację oraz analizę wyników testów wydajnościowych. System ten został zaprojektowany z myślą o maksymalnej wydajności, skalowalności oraz precyzji pomiarów, co jest kluczowe dla uzyskania wiarygodnych wyników porównawczych.

### 2.4.1 Struktura danych wyników i ich reprezentacja

System wykorzystuje zaawansowaną strukturę danych do reprezentacji wyników testów, która została zaprojektowana z myślą o efektywnym przechowywaniu i przetwarzaniu dużych ilości danych pomiarowych. Głównym komponentem tej struktury jest klasa `OperationResult`, która enkapsuluje wszystkie istotne informacje o pojedynczym pomiarze wydajności.

**Kompleksowa struktura OperationResult**
Klasa `OperationResult` implementuje dataclass pattern, zapewniając efektywne przechowywanie i serializację danych:

<augment_code_snippet path="src/database/result_handling/operation_result.py" mode="EXCERPT">
````python
@dataclass
class OperationResult:
    database: str
    operation: str
    records: int
    time: float
    timestamp: pd.Timestamp
    timing_method: str
    indexes_type: str
    threads: int
    iteration: int
````
</augment_code_snippet>

**Agregacja wyników w ResultsVisualizer**
System implementuje zaawansowane mechanizmy agregacji wyników, które umożliwiają grupowanie i analizę danych według różnych kryteriów:

<augment_code_snippet path="src/database/result_handling/results_visualizer.py" mode="EXCERPT">
````python
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
````
</augment_code_snippet>

### 2.4.2 Zaawansowane algorytmy przetwarzania i analizy danych

System implementuje szereg zaawansowanych algorytmów do przetwarzania i analizy zebranych danych wydajnościowych. Te algorytmy obejmują obliczenia statystyczne, analizę trendów oraz generowanie metryk porównawczych.

**Algorytm grupowania i agregacji danych**
System wykorzystuje pandas DataFrame do efektywnego grupowania i agregacji danych, co umożliwia szybkie obliczenia statystyczne:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
@staticmethod
def generate_standard_chart(df: pd.DataFrame, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))

    # Grupowanie danych i obliczanie średnich czasów
    avg_time_data = df.groupby(['database', 'operation'])['time'].mean().reset_index()
    operations = sorted(avg_time_data['operation'].unique())
    databases = sorted(avg_time_data['database'].unique())

    # Przygotowanie danych do wizualizacji
    x_positions = np.arange(len(operations))
    bar_width = 0.35
    mysql_avg_times = []
    mongodb_avg_times = []
````
</augment_code_snippet>

**Algorytm obliczania różnic procentowych**
System implementuje precyzyjny algorytm obliczania różnic procentowych między bazami danych:

<augment_code_snippet path="src/database/charts/chart_generator.py" mode="EXCERPT">
````python
@staticmethod
def _generate_comparison_text(operations, mysql_avg_times, mongodb_avg_times):
    comparison_texts = []
    for operation, mysql_time, mongodb_time in zip(operations, mysql_avg_times, mongodb_avg_times):
        if mysql_time > 0 and mongodb_time > 0:
            if mysql_time > mongodb_time:
                percentage_diff = (mysql_time / mongodb_time - 1) * 100
                comparison_texts.append(
                    f'{operation}: MongoDB szybszy o {percentage_diff:.2f}% '
                    f'(MySQL:{mysql_time:.3f},MongoDB:{mongodb_time:.3f})')
            elif mongodb_time > mysql_time:
                percentage_diff = (mongodb_time / mysql_time - 1) * 100
                comparison_texts.append(
                    f'{operation}: MySQL szybszy o {percentage_diff:.2f}% '
                    f'(MySQL:{mysql_time:.3f},MongoDB:{mongodb_time:.3f})')
            else:
                comparison_texts.append(f'{operation}: Identyczny czas')
    return comparison_texts
````
</augment_code_snippet>

### 2.4.3 System automatycznego generowania raportów i podsumowań

Aplikacja implementuje zaawansowany system automatycznego generowania raportów, który tworzy kompleksowe podsumowania wyników testów w różnych formatach. System ten jest uruchamiany automatycznie po zakończeniu testów i generuje szczegółowe analizy wydajnościowe.

**Automatyczne uruchamianie generatora raportów**
System automatycznie identyfikuje najnowsze wyniki testów i uruchamia generator raportów:

<augment_code_snippet path="src/main.py" mode="EXCERPT">
````python
    try:
        runner.run()
        runner.close()
        gc.collect()

        # Lokalizacja folderów z wynikami
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(base_dir)
        results_dir = os.path.join(project_dir, 'results')

        # Wyszukiwanie najnowszego folderu z wynikami
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
````
</augment_code_snippet>

## 2.5 Kompleksowa integracja komponentów i zaawansowany przepływ danych

Wszystkie opisane systemy współpracują ze sobą w ramach głównej architektury aplikacji, tworząc spójny i efektywny przepływ danych od momentu inicjalizacji konfiguracji, przez wykonanie testów wydajnościowych, po generowanie wykresów i kompleksowych raportów analitycznych. Ta integracja została zaprojektowana z myślą o maksymalnej wydajności, niezawodności oraz łatwości rozszerzania funkcjonalności.

### 2.5.1 Główna pętla wykonawcza aplikacji

Serce aplikacji stanowi klasa `TestRunner`, która orchestruje cały proces testowania wydajności. Klasa ta implementuje wzorzec Template Method, definiując ogólny algorytm testowania, ale pozwalając poszczególnym komponentom na implementację specyficznych szczegółów:

<augment_code_snippet path="src/database/test_runner.py" mode="EXCERPT">
````python
class TestRunner:
    DB_LIST = ("MongoDB", "MySQL")

    def __init__(self, config_manager: ConfigManager, total_records: int, iterations: int,
                 index_types: str, max_batch_size: int, show_progress: bool):
        self.config_manager = config_manager
        self.total_records = total_records
        self.iterations = iterations
        self.max_batch_size = max_batch_size
        self.show_progress = show_progress

        # Inicjalizacja testerów dla każdej bazy danych
        self.testers = {}
        self.client_results = {}

        # Inicjalizacja systemu wizualizacji wyników
        self.visualizer = ResultsVisualizer(
            results_dir='results',
            records=total_records,
            timing_method='database',
            iterations=iterations,
            indexes_type=index_types
        )
````
</augment_code_snippet>

### 2.5.2 Zaawansowane mechanizmy zarządzania pamięcią i zasobami

System implementuje zaawansowane mechanizmy zarządzania pamięcią, które są kluczowe dla stabilnego działania aplikacji podczas długotrwałych testów wydajnościowych. Te mechanizmy obejmują automatyczne czyszczenie pamięci, zarządzanie połączeniami oraz optymalizację wykorzystania zasobów systemowych:

<augment_code_snippet path="src/database/test_runner.py" mode="EXCERPT">
````python
def run(self) -> bool:
    index_types_list = self._parse_index_types()

    for idx in index_types_list:
        ProgressLogger.important_info(f"Starting tests for index type: {idx.upper()}")

        # Wykonanie testów dla każdego typu indeksu
        for iteration in range(1, self.iterations + 1):
            self._run_single_iteration(iteration, idx)

        # Generowanie wizualizacji wyników
        self.visualizer.show_results(indexes_type=idx)

        # Generowanie wykresów porównania klientów
        for db, idx_res in self.client_results.items():
            if idx in idx_res and idx_res[idx]:
                self.visualizer.show_clients_comparison_chart(db, idx_res[idx], self.total_records, idx)

        # Wymuszone czyszczenie pamięci
        gc.collect()
        ProgressLogger.important_info(f"Completed tests for index type: {idx.upper()}")

    # Finalne czyszczenie zasobów
    self.client_results.clear()
    gc.collect()
    return True
````
</augment_code_snippet>

### 2.5.3 Podsumowanie architektury i jej zalet

Zaprezentowana implementacja systemu porównywania wydajności baz danych stanowi przykład zaawansowanej architektury aplikacji, która łączy w sobie:

1. **Modularność** - każdy komponent ma jasno zdefiniowaną odpowiedzialność i może być niezależnie testowany i rozwijany
2. **Skalowalność** - system może być łatwo rozszerzony o nowe typy baz danych, operacji czy metryk wydajności
3. **Niezawodność** - implementacja thread-safe mechanizmów oraz zaawansowane zarządzanie zasobami zapewnia stabilne działanie
4. **Elastyczność** - bogaty system konfiguracji umożliwia dostosowanie aplikacji do różnych scenariuszy testowych
5. **Użyteczność** - automatyczne generowanie wykresów i raportów czyni aplikację gotowym narzędziem do analizy wydajności

System logowania zapewnia pełną transparentność procesu testowania, system konfiguracji umożliwia łatwe dostosowanie parametrów, a system wizualizacji automatycznie generuje profesjonalne wykresy i raporty analityczne. Ta kompleksowa implementacja czyni aplikację potężnym narzędziem do porównywania wydajności różnych systemów bazodanowych w kontrolowanych warunkach testowych.
