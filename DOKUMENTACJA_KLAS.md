# Dokumentacja Klas - System Porównania Wydajności Baz Danych

## Spis Treści
1. [Klasy Główne](#klasy-główne)
2. [Moduł MongoDB](#moduł-mongodb)
3. [Moduł MySQL](#moduł-mysql)
4. [Moduł Testowania](#moduł-testowania)
5. [Moduł Generowania Danych](#moduł-generowania-danych)
6. [Moduł Obsługi Wyników](#moduł-obsługi-wyników)
7. [Komponenty Wspólne](#komponenty-wspólne)
8. [Podsumowanie Aplikacji](#podsumowanie-aplikacji)

---

## Klasy Główne

### `main.py`
**Plik główny aplikacji**
- **Cel**: Punkt wejścia do aplikacji, parsowanie argumentów, uruchamianie testów
- **Zależności**: `ConfigManager`, `TestRunner`, `ProgressLogger`
- **Funkcjonalność**: 
  - Parsuje argumenty wiersza poleceń (liczba rekordów, klientów, iteracji)
  - Konfiguruje system logowania
  - Uruchamia testy wydajności
  - Automatycznie generuje raporty po zakończeniu testów

### `TestRunner`
**Główny koordynator testów**
- **Cel**: Zarządza całym procesem testowania wydajności baz danych
- **Zależności**: `MongoDBTester`, `MySQLTester`, `ResultsVisualizer`, `ConfigManager`
- **Funkcjonalność**:
  - Koordynuje testy dla różnych typów indeksów
  - Zarządza iteracjami testów
  - Czyści bazy danych przed testami
  - Zapisuje wyniki do plików CSV/JSON
  - Generuje wizualizacje wyników

---

## Moduł MongoDB

### `MongoDBConnection`
**Zarządzanie połączeniem z MongoDB**
- **Cel**: Nawiązywanie i zarządzanie połączeniem z bazą MongoDB
- **Zależności**: `pymongo.MongoClient`, `ConfigManager`
- **Funkcjonalność**:
  - Konfiguruje parametry połączenia (pool size, timeouty)
  - Włącza profilowanie MongoDB
  - Zarządza cyklem życia połączenia
  - Obsługuje błędy połączenia

### `MongoDBUserRepository`
**Repository dla operacji na użytkownikach w MongoDB**
- **Cel**: Implementuje operacje CRUD dla MongoDB z pomiarem wydajności
- **Zależności**: `MongoDBConnection`, `pymongo`, `Repository`
- **Funkcjonalność**:
  - Wstawianie danych (bulk insert)
  - Pobieranie wszystkich użytkowników
  - Aktualizacja użytkowników
  - Usuwanie użytkowników
  - Tworzenie indeksów
  - Pomiar czasu operacji przez system profilowania MongoDB

### `MongoDBTester`
**Tester specyficzny dla MongoDB**
- **Cel**: Przeprowadza testy wydajności specyficzne dla MongoDB
- **Zależności**: `DatabaseTester`, `MongoDBUserRepository`
- **Funkcjonalność**:
  - Generuje unikalne nazwy kolekcji dla każdego testu
  - Konfiguruje repository dla konkretnej kolekcji
  - Dziedziczy logikę testowania z `DatabaseTester`

---

## Moduł MySQL

### `MySQLConnection`
**Zarządzanie połączeniem z MySQL**
- **Cel**: Nawiązywanie i zarządzanie połączeniem z bazą MySQL
- **Zależności**: `pymysql`, `ConfigManager`
- **Funkcjonalność**:
  - Konfiguruje parametry połączenia MySQL
  - Ustawia tryby sesji (isolation level, timeouty)
  - Zarządza kursorami
  - Obsługuje reconnect w przypadku utraty połączenia

### `MySQLConnectionPool`
**Pula połączeń MySQL**
- **Cel**: Zarządza pulą połączeń MySQL dla lepszej wydajności
- **Zależności**: `ConnectionPool`, `MySQLConnection`
- **Funkcjonalność**:
  - Tworzy i zarządza pulą połączeń
  - Udostępnia połączenia na żądanie
  - Zwalnia nieużywane połączenia
  - Zamyka wszystkie połączenia przy shutdown

### `MySQLQueryExecutor`
**Executor zapytań MySQL**
- **Cel**: Wykonuje zapytania MySQL w sposób asynchroniczny
- **Zależności**: `QueryExecutor`, `MySQLConnectionPool`
- **Funkcjonalność**:
  - Wykonuje zapytania w puli wątków
  - Zarządza połączeniami z puli
  - Obsługuje błędy wykonania zapytań
  - Zwraca Future objects dla asynchronicznego przetwarzania

### `MySQLIndexManager`
**Zarządzanie indeksami MySQL**
- **Cel**: Tworzy i zarządza indeksami w MySQL
- **Zależności**: `IndexManager`, `RetryDecorator`
- **Funkcjonalność**:
  - Tworzy indeksy foreign key
  - Obsługuje błędy tworzenia indeksów
  - Używa retry decorator dla odporności na błędy

### `MySQLUserRepository`
**Repository dla operacji na użytkownikach w MySQL**
- **Cel**: Implementuje operacje CRUD dla MySQL z pomiarem wydajności
- **Zależności**: `Repository`, `MySQLQueryExecutor`, `MySQLIndexManager`
- **Funkcjonalność**:
  - Tworzy tabele dynamicznie
  - Wstawianie danych (bulk insert)
  - Pobieranie, aktualizacja, usuwanie użytkowników
  - Pomiar czasu operacji przez PERFORMANCE_SCHEMA
  - Zarządzanie indeksami

### `MySQLTester`
**Tester specyficzny dla MySQL**
- **Cel**: Przeprowadza testy wydajności specyficzne dla MySQL
- **Zależności**: `DatabaseTester`, `MySQLUserRepository`
- **Funkcjonalność**:
  - Generuje unikalne nazwy tabel dla każdego testu
  - Konfiguruje repository dla konkretnej tabeli
  - Dziedziczy logikę testowania z `DatabaseTester`

---

## Moduł Testowania

### `DatabaseTester` (abstrakcyjna)
**Bazowa klasa dla testerów baz danych**
- **Cel**: Definiuje wspólną logikę testowania dla wszystkich baz danych
- **Zależności**: `UserRepository`, `DataGenerator`, `MultiClientDataGenerator`
- **Funkcjonalność**:
  - Generuje dane testowe
  - Wykonuje testy wstawiania, pobierania, aktualizacji, usuwania
  - Mierzy czasy wykonania operacji
  - Zarządza wieloma klientami
  - Czyści dane po testach

---

## Moduł Generowania Danych

### `DataGenerator`
**Generator danych testowych**
- **Cel**: Generuje realistyczne dane użytkowników do testów
- **Zależności**: `random`, `RecordType`
- **Funkcjonalność**:
  - Generuje pełne rekordy (imię, nazwisko, email, adres, wiek)
  - Generuje proste rekordy (tylko wartość numeryczna)
  - Cachuje kombinacje imion/nazwisk dla wydajności
  - Obsługuje różne typy rekordów (BIG/SMALL)

### `MultiClientDataGenerator`
**Generator danych dla wielu klientów**
- **Cel**: Generuje dane podzielone między różnych klientów
- **Zależności**: `DataGenerator`
- **Funkcjonalność**:
  - Tworzy dane dla określonej liczby klientów
  - Przypisuje client_id do każdego rekordu
  - Zwraca dane pogrupowane według klientów

---

## Moduł Obsługi Wyników

### `ResultsVisualizer`
**Wizualizacja wyników testów**
- **Cel**: Wyświetla i zapisuje wyniki testów w różnych formatach
- **Zależności**: `ResultsFileManager`, `ChartGenerator`, `pandas`
- **Funkcjonalność**:
  - Konwertuje wyniki do DataFrame
  - Generuje wykresy porównawcze
  - Wyświetla tabele wyników
  - Zapisuje dane do CSV/JSON

### `ResultsFileManager`
**Zarządzanie plikami wyników**
- **Cel**: Zarządza zapisem i organizacją plików wyników
- **Zależności**: `pandas`, `json`
- **Funkcjonalność**:
  - Tworzy strukturę folderów wyników
  - Zapisuje dane do CSV i JSON
  - Generuje ścieżki do wykresów
  - Organizuje wyniki według typów indeksów

### `ChartGenerator`
**Generator wykresów**
- **Cel**: Tworzy wykresy porównawcze wydajności
- **Zależności**: `matplotlib`, `pandas`, `numpy`
- **Funkcjonalność**:
  - Generuje wykresy słupkowe porównań
  - Tworzy histogramy czasów wykonania
  - Generuje wykresy porównań między iteracjami
  - Dodaje etykiety i opisy do wykresów

### `OperationResult`
**Struktura danych wyników operacji**
- **Cel**: Przechowuje wyniki pojedynczej operacji
- **Funkcjonalność**:
  - Zawiera informacje o operacji (typ, czas, liczba rekordów)
  - Metadane (baza danych, typ indeksu, iteracja)
  - Konwersja do słownika dla serializacji

---

## Komponenty Wspólne

### `ConfigManager`
**Zarządzanie konfiguracją aplikacji**
- **Cel**: Centralne zarządzanie konfiguracją z różnych źródeł
- **Zależności**: `os` (zmienne środowiskowe)
- **Funkcjonalność**:
  - Singleton pattern
  - Ładuje konfigurację z argumentów CLI i zmiennych środowiskowych
  - Generuje connection stringi dla baz danych
  - Przechowuje wszystkie parametry aplikacji

### `ConnectionPool` (abstrakcyjna)
**Bazowa klasa puli połączeń**
- **Cel**: Definiuje interfejs dla pul połączeń
- **Funkcjonalność**:
  - Zarządza pulą połączeń z thread-safety
  - Udostępnia i zwalnia połączenia
  - Zamyka wszystkie połączenia

### `QueryExecutor` (abstrakcyjna)
**Bazowa klasa executora zapytań**
- **Cel**: Definiuje interfejs dla asynchronicznego wykonywania zapytań
- **Zależności**: `ThreadPoolExecutor`, `Future`
- **Funkcjonalność**:
  - Wykonuje zapytania w puli wątków
  - Zarządza cyklem życia połączeń
  - Zwraca Future objects

### `Repository` (abstrakcyjna)
**Bazowy interfejs repository**
- **Cel**: Definiuje wspólny interfejs dla operacji na danych
- **Funkcjonalność**:
  - CRUD operations (create, read, update, delete)
  - Zarządzanie indeksami
  - Czyszczenie kolekcji/tabel

### `IndexManager` (abstrakcyjna)
**Zarządzanie indeksami baz danych**
- **Cel**: Definiuje interfejs dla tworzenia indeksów
- **Funkcjonalność**:
  - Tworzenie różnych typów indeksów
  - Mapowanie typów indeksów na metody

### `RetryDecorator`
**Decorator dla ponawiania operacji**
- **Cel**: Dodaje mechanizm retry do metod
- **Funkcjonalność**:
  - Ponawia operacje w przypadku błędów
  - Konfigurowalny liczba prób i delay
  - Loguje błędy i próby

### `IndexType` (Enum)
**Typy indeksów**
- **Cel**: Definiuje dostępne typy indeksów
- **Wartości**: `NO_INDEXES`, `FOREIGN_KEY`, `ALL`

### `RecordType` (Enum)
**Typy rekordów**
- **Cel**: Definiuje typy generowanych rekordów
- **Wartości**: `BIG` (pełne dane), `SMALL` (tylko wartość numeryczna)

### `DatabaseType` (Enum)
**Typy baz danych**
- **Cel**: Identyfikuje typ bazy danych
- **Wartości**: `MONGO`, `MYSQL`

### `ProgressLogger`
**System logowania**
- **Cel**: Zapewnia ujednolicone logowanie w całej aplikacji
- **Funkcjonalność**:
  - Różne poziomy logowania (info, error, warning)
  - Formatowanie wiadomości z iteracjami
  - Konfigurowalny poziom szczegółowości

---

## Podsumowanie Aplikacji

### Cel Aplikacji
System do **porównania wydajności baz danych MongoDB i MySQL** w różnych scenariuszach testowych.

### Główne Funkcjonalności
1. **Testowanie wydajności** - Pomiar czasów operacji CRUD
2. **Różne typy indeksów** - Testy z indeksami i bez
3. **Wielokrotne iteracje** - Statystyczna wiarygodność wyników
4. **Wielu klientów** - Symulacja obciążenia równoległego
5. **Różne typy danych** - Małe i duże rekordy
6. **Wizualizacja wyników** - Wykresy i raporty
7. **Konfigurowalność** - Parametry przez CLI i zmienne środowiskowe

### Architektura
- **Wzorzec Repository** - Abstrakcja dostępu do danych
- **Wzorzec Strategy** - Różne implementacje dla różnych baz
- **Wzorzec Factory** - Tworzenie testerów i połączeń
- **Dependency Injection** - Przekazywanie zależności
- **Thread Pool** - Asynchroniczne wykonywanie zapytań

### Technologie
- **Python 3.12** - Język programowania
- **MongoDB 4.6+** - Baza NoSQL
- **MySQL 8.0+** - Baza relacyjna
- **Docker** - Konteneryzacja baz danych
- **Pandas** - Analiza danych
- **Matplotlib** - Generowanie wykresów
- **PyMongo** - Driver MongoDB
- **PyMySQL** - Driver MySQL

### Zastosowanie
Aplikacja jest idealna do:
- **Prac inżynierskich** - Analiza wydajności baz danych
- **Benchmarkingu** - Porównanie różnych rozwiązań
- **Optymalizacji** - Wybór odpowiedniej bazy danych
- **Badań naukowych** - Analiza wpływu indeksów na wydajność
- **Projektów komercyjnych** - Decyzje architektoniczne

### Wartość Naukowa
- **Empiryczne dane** o wydajności baz danych
- **Wpływ indeksów** na różne operacje
- **Skalowanie** z liczbą rekordów i klientów
- **Porównanie** NoSQL vs SQL
- **Metodologia** powtarzalnych testów wydajności

---

## Szczegółowe Funkcjonalności Testowe

### 1. Testowanie Operacji CRUD

#### **INSERT (Wstawianie danych)**
**Co testuje:**
- Czas wstawiania dużych partii danych (bulk insert)
- Wydajność przy różnych rozmiarach batch'y
- Wpływ indeksów na szybkość wstawiania

**Parametry testowe:**
- Liczba rekordów: 100 - 100,000+
- Rozmiar batch'a: konfigurowalne
- Typy danych: pełne rekordy vs proste wartości numeryczne

**Co można udowodnić:**
- MongoDB jest szybsze przy bulk insert bez indeksów
- MySQL ma stały overhead transakcyjny
- Indeksy spowalniają operacje INSERT w obu bazach

#### **SELECT (Pobieranie danych)**
**Co testuje:**
- Czas pobierania wszystkich rekordów dla klienta
- Wydajność filtrowania po client_id
- Wpływ indeksów na szybkość zapytań

**Parametry testowe:**
- Filtrowanie po kluczu obcym (client_id)
- Różne rozmiary zbiorów danych
- Z indeksem i bez indeksu

**Co można udowodnić:**
- Indeksy dramatycznie przyspieszają SELECT w MySQL
- MongoDB ma lepszą wydajność bez indeksów przy małych zbiorach
- Różnica wydajności rośnie z rozmiarem danych

#### **UPDATE (Aktualizacja danych)**
**Co testuje:**
- Czas aktualizacji wszystkich rekordów klienta
- Wydajność operacji SET vs INCREMENT
- Wpływ indeksów na szybkość aktualizacji

**Typy aktualizacji:**
- Proste rekordy: INCREMENT wartości numerycznej
- Pełne rekordy: SET wieku i imienia

**Co można udowodnić:**
- MongoDB ma przewagę w operacjach UPDATE
- Indeksy pomagają w lokalizacji rekordów do aktualizacji
- Różne typy aktualizacji mają różną wydajność

#### **DELETE (Usuwanie danych)**
**Co testuje:**
- Czas usuwania wszystkich rekordów klienta
- Wydajność operacji DELETE z filtrem
- Wpływ indeksów na szybkość usuwania

**Co można udowodnić:**
- MongoDB szybsze w operacjach DELETE
- Indeksy przyspieszają lokalizację rekordów do usunięcia
- MySQL ma większy overhead przy usuwaniu

### 2. Testowanie Typów Indeksów

#### **NO_INDEXES (Bez indeksów)**
**Co testuje:**
- Wydajność "surową" bazy danych
- Skanowanie pełnych tabel/kolekcji
- Baseline dla porównań

**Co można udowodnić:**
- MongoDB ma przewagę przy braku indeksów
- Operacje są wolniejsze ale bardziej przewidywalne
- Różnice w architekturze storage engine

#### **FOREIGN_KEY (Indeks klucza obcego)**
**Co testuje:**
- Wpływ indeksu na client_id
- Przyspieszenie operacji filtrowania
- Koszt utrzymania indeksu

**Co można udowodnić:**
- Indeksy drastycznie przyspieszają SELECT/UPDATE/DELETE
- Koszt INSERT wzrasta przez utrzymanie indeksu
- ROI indeksów zależy od typu operacji

### 3. Testowanie Skalowalności

#### **Liczba Rekordów**
**Zakresy testowe:** 100, 1K, 10K, 100K, 1M+
**Co można udowodnić:**
- Jak wydajność skaluje się z rozmiarem danych
- Punkty przełamania wydajności
- Różnice w krzywych skalowalności między bazami

#### **Liczba Klientów (Równoległość)**
**Zakresy testowe:** 1, 2, 5, 10, 20+ klientów
**Co można udowodnić:**
- Wydajność przy obciążeniu równoległym
- Bottlenecki w connection pooling
- Różnice w obsłudze współbieżności

#### **Rozmiar Batch'y**
**Zakresy testowe:** 100, 1K, 5K, 10K rekordów na batch
**Co można udowodnić:**
- Optymalny rozmiar batch'a dla każdej bazy
- Trade-off między pamięcią a wydajnością
- Różnice w obsłudze dużych transakcji

### 4. Testowanie Typów Danych

#### **BIG Records (Pełne rekordy)**
**Zawartość:** imię, nazwisko, email, adres, wiek, client_id
**Rozmiar:** ~200-300 bajtów na rekord
**Co można udowodnić:**
- Wydajność przy realistycznych danych
- Wpływ rozmiaru rekordu na operacje
- Różnice w kompresji danych

#### **SMALL Records (Proste rekordy)**
**Zawartość:** wartość numeryczna, client_id
**Rozmiar:** ~20-30 bajtów na rekord
**Co można udowodnić:**
- Maksymalna wydajność przy minimalnych danych
- Overhead bazy danych vs rozmiar danych
- Różnice w storage efficiency

### 5. Analiza Statystyczna

#### **Wielokrotne Iteracje**
**Funkcjonalność:**
- Każdy test powtarzany N razy
- Obliczanie średnich, median, odchyleń
- Wykrywanie anomalii wydajnościowych

**Co można udowodnić:**
- Stabilność wydajności w czasie
- Wariancja czasów wykonania
- Statystyczna istotność różnic

#### **Wizualizacja Wyników**
**Typy wykresów:**
- Wykresy słupkowe porównań średnich
- Histogramy rozkładu czasów
- Wykresy liniowe trendów między iteracjami

**Co można udowodnić:**
- Wizualne różnice w wydajności
- Rozkłady czasów wykonania
- Trendy i anomalie

---

## Możliwe Wnioski i Dowody Naukowe

### 1. Wydajność Operacyjna
**Hipotezy do sprawdzenia:**
- MongoDB jest szybsze w operacjach INSERT i DELETE
- MySQL ma przewagę w operacjach SELECT z indeksami
- Operacje UPDATE są szybsze w MongoDB
- Indeksy zawsze przyspieszają SELECT ale spowalniają INSERT

### 2. Skalowalność
**Hipotezy do sprawdzenia:**
- MongoDB lepiej skaluje się z liczbą rekordów
- MySQL lepiej radzi sobie z wieloma równoległymi klientami
- Istnieją punkty przełamania gdzie jedna baza wyprzedza drugą
- Rozmiar batch'a ma różny wpływ na różne bazy

### 3. Efektywność Indeksów
**Hipotezy do sprawdzenia:**
- ROI indeksów zależy od proporcji operacji read/write
- Indeksy mają większy wpływ w MySQL niż MongoDB
- Koszt utrzymania indeksów jest wyższy w MySQL
- Punkt równowagi między korzyściami a kosztami indeksów

### 4. Charakterystyki Storage
**Hipotezy do sprawdzenia:**
- MongoDB ma lepszą kompresję danych
- MySQL ma bardziej przewidywalną wydajność
- Różnice w overhead'zie storage engine
- Wpływ rozmiaru rekordu na wydajność

### 5. Architektoniczne
**Hipotezy do sprawdzenia:**
- Document-based storage vs relacyjny ma różne charakterystyki
- Connection pooling działa inaczej w różnych bazach
- Transakcyjność wpływa na wydajność MySQL
- Schema-less design daje przewagę MongoDB

---

## Metodologia Badawcza

### Kontrola Zmiennych
- **Sprzęt:** Identyczne środowisko testowe
- **Sieć:** Lokalne połączenia (eliminacja latencji)
- **Konfiguracja:** Porównywalne ustawienia baz danych
- **Dane:** Identyczne zestawy testowe

### Pomiary
- **Precyzja:** Pomiary w milisekundach
- **Źródło:** Natywne narzędzia profilowania baz
- **Powtarzalność:** Wielokrotne iteracje
- **Izolacja:** Czyszczenie danych między testami

### Walidacja
- **Weryfikacja danych:** Sprawdzanie poprawności operacji
- **Monitoring zasobów:** Kontrola zużycia CPU/pamięci
- **Logowanie:** Szczegółowe logi wszystkich operacji
- **Reprodukowalność:** Możliwość powtórzenia testów

Ta aplikacja dostarcza solidnych, empirycznych danych do porównania wydajności baz danych MongoDB i MySQL w kontrolowanych warunkach, co czyni ją idealną podstawą do pracy inżynierskiej lub badań naukowych.
