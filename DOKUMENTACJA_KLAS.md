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
