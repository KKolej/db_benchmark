# Dokumentacja Klas - System Porównania Wydajności Baz Danych

## Spis Treści
1. [Czym jest ta Aplikacja](#czym-jest-ta-aplikacja)
2. [Wykaz zastosowanych technologii](#wykaz-zastosowanych-technologii)
3. [Klasy Główne](#klasy-główne)
4. [Moduł MongoDB](#moduł-mongodb)
5. [Moduł MySQL](#moduł-mysql)
6. [Moduł Testowania](#moduł-testowania)
7. [Moduł Generowania Danych](#moduł-generowania-danych)
8. [Moduł Obsługi Wyników](#moduł-obsługi-wyników)
9. [Komponenty Wspólne](#komponenty-wspólne)
10. [Podsumowanie Aplikacji](#podsumowanie-aplikacji)

---

## Czym jest ta Aplikacja

### Wprowadzenie i Cel Aplikacji

**System Porównania Wydajności Baz Danych** to zaawansowana aplikacja naukowa i inżynierska, zaprojektowana specjalnie do przeprowadzania kompleksowych analiz porównawczych wydajności między dwoma fundamentalnie różnymi typami systemów bazodanowych: **MongoDB** (baza dokumentowa NoSQL) oraz **MySQL** (relacyjna baza danych SQL). Aplikacja stanowi solidne narzędzie badawcze, które umożliwia empiryczne porównanie charakterystyk wydajnościowych tych systemów w kontrolowanych warunkach testowych.

### Znaczenie Naukowe i Praktyczne

W dzisiejszym świecie technologii informacyjnych, wybór odpowiedniego systemu bazodanowego ma kluczowe znaczenie dla sukcesu projektów informatycznych. Różnice między bazami NoSQL a SQL nie ograniczają się jedynie do modelu danych - obejmują również fundamentalne różnice w architekturze, mechanizmach przechowywania danych, strategiach indeksowania oraz charakterystykach wydajnościowych. Ta aplikacja wypełnia lukę w dostępnych narzędziach badawczych, dostarczając precyzyjnych, powtarzalnych i statystycznie wiarygodnych pomiarów wydajności.

### Architektura i Filozofia Projektowa

Aplikacja została zaprojektowana zgodnie z najlepszymi praktykami inżynierii oprogramowania, wykorzystując zaawansowane wzorce projektowe i nowoczesną architekturę modułową. Główne założenia projektowe obejmują:

**1. Modularność i Rozszerzalność**
System został zbudowany w oparciu o luźno powiązane moduły, z których każdy odpowiada za konkretny aspekt funkcjonalności. Architektura umożliwia łatwe dodawanie nowych typów baz danych, metod testowania czy sposobów wizualizacji wyników bez konieczności modyfikacji istniejącego kodu.

**2. Abstrakcja i Polimorfizm**
Wykorzystanie wzorców Repository, Strategy i Factory pozwala na jednolite traktowanie różnych systemów bazodanowych przy zachowaniu ich specyficznych charakterystyk. Abstrakcyjne klasy bazowe definiują wspólne interfejsy, podczas gdy konkretne implementacje dostosowują się do specyfiki każdej bazy danych.

**3. Konfigurowalność i Elastyczność**
System oferuje szerokie możliwości konfiguracji poprzez argumenty wiersza poleceń oraz zmienne środowiskowe. Użytkownicy mogą dostosować wszystkie aspekty testów: od liczby rekordów i iteracji, przez typy indeksów, aż po parametry połączeń z bazami danych.

**4. Wiarygodność Statystyczna**
Aplikacja implementuje zaawansowane mechanizmy zapewniające wiarygodność statystyczną wyników, w tym wielokrotne iteracje testów, kontrolę zmiennych środowiskowych oraz szczegółowe logowanie wszystkich operacji.

### Funkcjonalności Podstawowe

**Testowanie Operacji CRUD**
System przeprowadza kompleksowe testy wszystkich podstawowych operacji bazodanowych:
- **CREATE (INSERT)** - Pomiar wydajności wstawiania danych w różnych konfiguracjach batch'y
- **READ (SELECT)** - Analiza czasów pobierania danych z filtrowaniem i bez
- **UPDATE** - Testowanie modyfikacji istniejących rekordów
- **DELETE** - Pomiar wydajności usuwania danych

**Analiza Wpływu Indeksów**
Aplikacja testuje różne scenariusze indeksowania:
- **NO_INDEXES** - Testy bez indeksów, pokazujące "surową" wydajność
- **FOREIGN_KEY** - Analiza wpływu indeksów na klucze obce
- **ALL** - Kompleksowe testowanie wszystkich typów indeksów

**Symulacja Obciążenia Rzeczywistego**
System umożliwia symulację różnych scenariuszy obciążenia:
- Różne liczby równoległych klientów (1-20+)
- Skalowalne rozmiary zbiorów danych (100 - 1,000,000+ rekordów)
- Różne rozmiary batch'y dla operacji bulk

### Funkcjonalności Zaawansowane

**Generowanie Danych Testowych**
Aplikacja zawiera zaawansowany system generowania realistycznych danych testowych:
- **Pełne rekordy** zawierające imiona, nazwiska, adresy email, adresy zamieszkania i wiek
- **Proste rekordy** z wartościami numerycznymi dla testów maksymalnej wydajności
- **Cachowanie** kombinacji danych dla optymalizacji wydajności generowania
- **Deterministyczne generowanie** zapewniające powtarzalność testów

**System Pomiaru Wydajności**
Implementacja wykorzystuje natywne narzędzia profilowania każdej bazy danych:
- **MongoDB** - System profilowania MongoDB z precyzyjnymi pomiarami czasów operacji
- **MySQL** - PERFORMANCE_SCHEMA dla dokładnego pomiaru wydajności zapytań
- **Precyzja pomiarów** - Pomiary w milisekundach z kontrolą overhead'u systemu

**Zarządzanie Połączeniami**
Zaawansowany system zarządzania połączeniami z bazami danych:
- **Connection Pooling** - Optymalizacja wydajności poprzez pule połączeń
- **Asynchroniczne wykonywanie** - ThreadPoolExecutor dla równoległego przetwarzania
- **Retry mechanizmy** - Automatyczne ponawianie operacji w przypadku błędów
- **Graceful shutdown** - Bezpieczne zamykanie połączeń i zasobów

### Wizualizacja i Analiza Wyników

**Generowanie Wykresów**
System automatycznie generuje różnorodne wizualizacje wyników:
- **Wykresy słupkowe** porównujące średnie czasy wykonania operacji
- **Histogramy** pokazujące rozkłady czasów wykonania
- **Wykresy liniowe** przedstawiające trendy między iteracjami
- **Wykresy porównawcze** z automatycznymi obliczeniami różnic procentowych

**Eksport Danych**
Wszystkie wyniki są automatycznie eksportowane w formatach:
- **CSV** - Dla dalszej analizy w narzędziach statystycznych
- **JSON** - Dla integracji z innymi systemami
- **PNG** - Wysokiej jakości wykresy gotowe do publikacji

**Organizacja Wyników**
Inteligentny system organizacji wyników:
- Automatyczne tworzenie struktury folderów według typów indeksów
- Timestamping wszystkich wyników
- Metadane zawierające pełną konfigurację testów

### Zastosowania Praktyczne

**Prace Inżynierskie i Naukowe**
Aplikacja dostarcza solidnej podstawy empirycznej dla:
- Prac dyplomowych analizujących wydajność baz danych
- Badań naukowych nad wpływem indeksów na wydajność
- Analiz porównawczych NoSQL vs SQL
- Studiów przypadków optymalizacji systemów bazodanowych

**Projekty Komercyjne**
System wspiera decyzje biznesowe poprzez:
- Benchmarking różnych rozwiązań bazodanowych
- Analizę kosztów i korzyści różnych architektur
- Planowanie skalowania systemów
- Optymalizację istniejących rozwiązań

**Edukacja i Szkolenia**
Aplikacja służy jako narzędzie edukacyjne dla:
- Demonstracji różnic między typami baz danych
- Nauczania wpływu indeksów na wydajność
- Pokazania metodologii testowania wydajności
- Praktycznego zastosowania wzorców projektowych

### Wartość Dodana i Innowacyjność

**Metodologia Badawcza**
Aplikacja implementuje zaawansowaną metodologię badawczą:
- **Kontrola zmiennych** - Identyczne warunki testowe dla obu baz
- **Izolacja testów** - Czyszczenie danych między testami
- **Powtarzalność** - Deterministyczne generowanie danych testowych
- **Walidacja** - Weryfikacja poprawności wszystkich operacji

**Precyzja Pomiarów**
System zapewnia wysoką precyzję pomiarów poprzez:
- Wykorzystanie natywnych narzędzi profilowania baz danych
- Minimalizację overhead'u systemu pomiarowego
- Kontrolę garbage collection i zarządzania pamięcią
- Szczegółowe logowanie wszystkich operacji

**Skalowalność Testów**
Aplikacja umożliwia testowanie w szerokim zakresie scenariuszy:
- Od małych zbiorów danych (100 rekordów) do dużych (1M+ rekordów)
- Od pojedynczych klientów do symulacji wysokiego obciążenia
- Różne profile danych (od prostych wartości do złożonych dokumentów)

### Technologie i Narzędzia

**Stack Technologiczny**
- **Python 3.12+** - Nowoczesny język programowania z zaawansowanymi możliwościami
- **MongoDB 4.6+** - Wiodąca baza dokumentowa NoSQL
- **MySQL 8.0+** - Zaawansowana relacyjna baza danych
- **Docker** - Konteneryzacja dla spójności środowiska testowego

**Biblioteki i Frameworki**
- **PyMongo** - Oficjalny driver MongoDB dla Pythona
- **PyMySQL** - Czysty Python driver dla MySQL
- **Pandas** - Zaawansowana analiza i manipulacja danych
- **Matplotlib** - Profesjonalne generowanie wykresów
- **Poetry** - Nowoczesne zarządzanie zależnościami

### Perspektywy Rozwoju

Aplikacja została zaprojektowana z myślą o przyszłym rozwoju i może być rozszerzona o:
- Dodatkowe systemy bazodanowe (PostgreSQL, Cassandra, Redis)
- Nowe typy testów (transakcje, agregacje, full-text search)
- Zaawansowane metryki (zużycie pamięci, I/O, CPU)
- Integrację z systemami CI/CD
- Web interface dla łatwiejszego użytkowania

Ta aplikacja reprezentuje kompleksowe podejście do analizy wydajności baz danych, łącząc solidne podstawy teoretyczne z praktyczną implementacją, co czyni ją idealnym narzędziem zarówno dla celów akademickich, jak i komercyjnych.

---

## Wykaz zastosowanych technologii

Poniżej przedstawiono wykaz wszystkich istotnych technologii zastosowanych w opracowaniu aplikacji do porównania wydajności baz danych. Lista obejmuje języki programowania, systemy bazodanowe, narzędzia konteneryzacji, biblioteki oraz frameworki wykorzystane w implementacji, wizualizacji i analizie danych.

### Języki programowania i środowiska uruchomieniowe
- **Python 3.12** - Główny język programowania aplikacji
- **Docker Compose 3.8** - Orkiestracja kontenerów

### Systemy bazodanowe
- **MongoDB 6.0** - Dokumentowa baza danych NoSQL
- **MySQL 8.0** - Relacyjna baza danych SQL

### Narzędzia konteneryzacji i wirtualizacji
- **Docker** - Platforma konteneryzacji
- **Docker Compose** - Narzędzie do definiowania i uruchamiania aplikacji wielokontenerowych

### Zarządzanie zależnościami i środowiskiem
- **Poetry** - Nowoczesne narzędzie do zarządzania zależnościami Python
- **Poetry Core** - Podstawowy system budowania dla Poetry

### Biblioteki dostępu do baz danych
- **PyMongo 4.12.0** - Oficjalny driver MongoDB dla Python
- **PyMySQL 1.1.1** - Czysty Python driver dla MySQL
- **mysql-connector-python 8.2.0** - Oficjalny MySQL Connector dla Python

### Biblioteki analizy i manipulacji danych
- **Pandas 2.2.0** - Zaawansowana biblioteka do analizy i manipulacji danych
- **NumPy 1.23+** - Fundamentalna biblioteka do obliczeń numerycznych

### Biblioteki wizualizacji i generowania wykresów
- **Matplotlib 3.8.2** - Kompleksowa biblioteka do tworzenia wykresów
- **Contourpy 1.3.1** - Biblioteka do generowania konturów (zależność Matplotlib)
- **Cycler 0.10+** - Narzędzie do cyklicznego przechodzenia przez wartości (zależność Matplotlib)
- **Fonttools 4.22.0+** - Biblioteka do manipulacji fontami (zależność Matplotlib)
- **Kiwisolver 1.3.1+** - Solver ograniczeń (zależność Matplotlib)
- **Pillow 8+** - Biblioteka do przetwarzania obrazów (zależność Matplotlib)
- **Pyparsing 2.3.1+** - Biblioteka do parsowania (zależność Matplotlib)

### Biblioteki konfiguracji i zarządzania środowiskiem
- **python-dotenv 1.1.0** - Ładowanie zmiennych środowiskowych z plików .env
- **python-dateutil 2.9.0** - Rozszerzenia dla standardowego modułu datetime

### Biblioteki bezpieczeństwa i kryptografii
- **Cryptography 44.0.2** - Kompleksowa biblioteka kryptograficzna
- **DNSpython 2.7.0** - Toolkit DNS (zależność PyMongo)

### Narzędzia systemowe i pomocnicze
- **Packaging 20.0+** - Podstawowe narzędzia do pakowania Python
- **Six 1.5+** - Biblioteka kompatybilności Python 2/3

### Specyfikacja środowiska testowego
Aplikacja została zaprojektowana i przetestowana w następującym środowisku:
- **System operacyjny**: Linux (Ubuntu/Debian)
- **Architektura**: x86_64
- **Minimalne wymagania pamięci**: 4 GB RAM
- **Zalecane wymagania pamięci**: 8+ GB RAM dla testów z dużymi zbiorami danych

### Charakterystyka technologiczna
Wybrane technologie charakteryzują się:
- **Wysoką wydajnością** - Optymalizowane biblioteki numeryczne i bazodanowe
- **Stabilnością** - Dojrzałe, szeroko stosowane w środowisku produkcyjnym
- **Kompatybilnością** - Pełna zgodność między wersjami i platformami
- **Skalowalnością** - Możliwość obsługi zarówno małych jak i dużych zbiorów danych
- **Otwartością** - Większość technologii oparta na licencjach open source

---

## Opis stosu technologicznego i uzasadnienie wybranych technologii

### Architektura stosu technologicznego

Stos technologiczny aplikacji do porównania wydajności baz danych został zaprojektowany jako wielowarstwowa architektura, w której każdy komponent pełni specyficzną rolę i współpracuje z pozostałymi elementami w sposób zapewniający maksymalną efektywność, wiarygodność pomiarów oraz łatwość rozwoju i utrzymania systemu.

#### Warstwa infrastruktury i konteneryzacji

**Docker i Docker Compose** stanowią fundament infrastruktury aplikacji, zapewniając izolację środowiska testowego oraz powtarzalność warunków eksperymentalnych. Wybór tej technologii wynika z kilku kluczowych czynników:

**Izolacja środowiska**: Kontenery Docker gwarantują, że bazy danych działają w identycznych warunkach niezależnie od systemu hosta, eliminując zmienne środowiskowe, które mogłyby wpłynąć na wyniki pomiarów. Każda baza danych działa w swoim dedykowanym kontenerze z predefiniowaną konfiguracją, co zapewnia sprawiedliwe warunki porównania.

**Powtarzalność eksperymentów**: Docker Compose umożliwia definiowanie całego środowiska testowego w formie kodu (Infrastructure as Code), co gwarantuje, że każde uruchomienie testów odbywa się w identycznych warunkach. Jest to kluczowe dla wiarygodności naukowej przeprowadzanych pomiarów.

**Łatwość wdrożenia**: Konteneryzacja eliminuje problemy związane z instalacją i konfiguracją baz danych na różnych systemach operacyjnych, znacznie upraszczając proces uruchomienia aplikacji przez innych badaczy lub użytkowników.

#### Warstwa systemów bazodanowych

**MongoDB 6.0 i MySQL 8.0** zostały wybrane jako reprezentatywne przykłady dwóch fundamentalnie różnych paradygmatów bazodanowych:

**MongoDB 6.0** reprezentuje nowoczesne bazy dokumentowe NoSQL, charakteryzujące się:
- **Elastycznym schematem**: Możliwość przechowywania dokumentów o różnej strukturze bez konieczności predefiniowania schematu
- **Natywną obsługą JSON/BSON**: Bezpośrednie mapowanie obiektów aplikacji na struktury bazodanowe
- **Horyzontalną skalowalnością**: Wbudowane mechanizmy shardingu i replikacji
- **Zaawansowanymi możliwościami agregacji**: Potężny framework agregacji umożliwiający złożone operacje analityczne

**MySQL 8.0** reprezentuje dojrzałe relacyjne bazy danych SQL, oferujące:
- **Silną spójność ACID**: Gwarancje transakcyjne zapewniające integralność danych
- **Zaawansowane mechanizmy indeksowania**: Różnorodne typy indeksów optymalizujące wydajność zapytań
- **Dojrzałe narzędzia optymalizacji**: Zaawansowany optymalizator zapytań i mechanizmy cache'owania
- **Standardizację SQL**: Zgodność ze standardami SQL zapewniająca przenośność aplikacji

Wybór tych konkretnych wersji wynika z ich stabilności, wydajności oraz reprezentatywności dla swoich kategorii. MongoDB 6.0 wprowadza znaczące ulepszenia wydajnościowe w stosunku do wcześniejszych wersji, podczas gdy MySQL 8.0 oferuje nowoczesne funkcjonalności przy zachowaniu kompatybilności wstecznej.

#### Warstwa języka programowania i środowiska uruchomieniowego

**Python 3.12** został wybrany jako główny język implementacji z następujących powodów:

**Bogaty ekosystem bibliotek**: Python oferuje najbogatszy zestaw bibliotek do analizy danych, wizualizacji oraz dostępu do baz danych, co znacznie przyspiesza rozwój aplikacji i zapewnia wysoką jakość implementacji.

**Czytelność i maintainability**: Składnia Pythona sprzyja tworzeniu czytelnego, dobrze udokumentowanego kodu, co jest kluczowe dla aplikacji naukowych, gdzie zrozumienie implementacji jest równie ważne jak wyniki.

**Wydajność dla zastosowań I/O-intensive**: Chociaż Python nie jest najszybszym językiem pod względem obliczeń CPU, aplikacje bazodanowe są głównie ograniczone przez operacje I/O, gdzie Python oferuje doskonałą wydajność dzięki asynchronicznym bibliotekom.

**Wsparcie dla wzorców projektowych**: Python doskonale wspiera zaawansowane wzorce projektowe (Repository, Strategy, Factory), które są kluczowe dla architektury aplikacji.

#### Warstwa zarządzania zależnościami

**Poetry** został wybrany jako narzędzie do zarządzania zależnościami ze względu na:

**Deterministyczne zarządzanie wersjami**: Poetry generuje pliki lock, które gwarantują identyczne wersje bibliotek na wszystkich środowiskach, co jest kluczowe dla powtarzalności eksperymentów naukowych.

**Rozdzielenie zależności**: Jasne rozdzielenie między zależnościami produkcyjnymi a deweloperskimi, co upraszcza wdrożenie i redukuje rozmiar środowiska produkcyjnego.

**Nowoczesne standardy**: Poetry implementuje najnowsze standardy PEP dla pakietów Python, zapewniając kompatybilność z przyszłymi wersjami ekosystemu.

#### Warstwa dostępu do danych

**PyMongo 4.12.0** i **PyMySQL 1.1.1** stanowią kluczowe komponenty warstwy dostępu do danych:

**PyMongo 4.12.0** - oficjalny driver MongoDB:
- **Natywna optymalizacja**: Bezpośrednia implementacja protokołu MongoDB zapewniająca maksymalną wydajność
- **Zaawansowane funkcjonalności**: Pełne wsparcie dla wszystkich funkcji MongoDB, włączając agregacje, transakcje i change streams
- **Connection pooling**: Wbudowane zarządzanie pulą połączeń optymalizujące wykorzystanie zasobów
- **Monitoring i profiling**: Integracja z narzędziami monitorowania MongoDB umożliwiająca szczegółową analizę wydajności

**PyMySQL 1.1.1** - czysty Python driver dla MySQL:
- **Brak zależności zewnętrznych**: Implementacja w czystym Pythonie eliminuje problemy z bibliotekami C/C++
- **Kompatybilność**: Pełna zgodność z MySQL Connector API przy lepszej wydajności
- **Bezpieczeństwo**: Wbudowane mechanizmy ochrony przed SQL injection
- **Elastyczność konfiguracji**: Szerokie możliwości dostrajania parametrów połączenia

#### Warstwa analizy i przetwarzania danych

**Pandas 2.2.0** i **NumPy 1.23+** tworzą fundament warstwy analitycznej:

**Pandas 2.2.0** został wybrany ze względu na:
- **Wydajność**: Znaczące ulepszenia wydajnościowe w wersji 2.x, szczególnie dla operacji na dużych zbiorach danych
- **Funkcjonalność**: Kompleksowy zestaw narzędzi do manipulacji, agregacji i analizy danych czasowych
- **Integracja**: Bezproblemowa współpraca z bibliotekami wizualizacji i eksportu danych
- **Memory efficiency**: Optymalizowane wykorzystanie pamięci kluczowe dla testów z dużymi zbiorami danych

**NumPy 1.23+** zapewnia:
- **Wydajne operacje numeryczne**: Zoptymalizowane operacje na tablicach wielowymiarowych
- **Podstawę dla innych bibliotek**: Fundament dla Pandas i Matplotlib
- **Stabilność**: Dojrzała, szeroko testowana implementacja

#### Warstwa wizualizacji

**Matplotlib 3.8.2** wraz z zależnościami tworzy kompletny system wizualizacji:

**Matplotlib 3.8.2** oferuje:
- **Profesjonalną jakość wykresów**: Możliwość tworzenia publikacyjnych wizualizacji
- **Elastyczność**: Szerokie możliwości dostosowania wyglądu wykresów
- **Różnorodność typów wykresów**: Od prostych wykresów słupkowych po złożone wizualizacje 3D
- **Eksport do różnych formatów**: PNG, PDF, SVG dla różnych zastosowań

**Zależności Matplotlib**:
- **Contourpy 1.3.1**: Generowanie konturów dla zaawansowanych wizualizacji
- **Fonttools 4.22.0+**: Zarządzanie fontami zapewniające spójny wygląd wykresów
- **Pillow 8+**: Przetwarzanie obrazów i eksport do formatów rastrowych

#### Warstwa bezpieczeństwa i konfiguracji

**Cryptography 44.0.2** i **python-dotenv 1.1.0** zapewniają bezpieczeństwo i elastyczność konfiguracji:

**Cryptography 44.0.2**:
- **Bezpieczne połączenia**: Obsługa szyfrowanych połączeń z bazami danych
- **Zgodność ze standardami**: Implementacja najnowszych standardów kryptograficznych
- **Wydajność**: Optymalizowane implementacje algorytmów kryptograficznych

**python-dotenv 1.1.0**:
- **Bezpieczne zarządzanie konfiguracją**: Oddzielenie wrażliwych danych od kodu źródłowego
- **Elastyczność środowisk**: Łatwe przełączanie między konfiguracjami dla różnych środowisk
- **Zgodność z best practices**: Implementacja wzorców twelve-factor app

### Synergiczne powiązania między komponentami

Wybrane technologie tworzą spójny ekosystem, w którym każdy komponent wzmacnia możliwości pozostałych:

**Integracja Docker + Python**: Konteneryzacja zapewnia izolację środowiska, podczas gdy Python oferuje bogaty ekosystem bibliotek do testowania wydajności baz danych.

**Synergię MongoDB/MySQL + Python drivers**: Natywne drivery zapewniają optymalną wydajność przy zachowaniu jednolitego API w warstwie aplikacji.

**Współpracę Pandas + Matplotlib**: Bezproblemowa integracja umożliwia płynne przejście od analizy danych do ich wizualizacji.

**Komplementarność Poetry + Docker**: Poetry zarządza zależnościami Python, podczas gdy Docker zapewnia izolację całego środowiska.

### Uzasadnienie architektury wielowarstwowej

Zastosowana architektura wielowarstwowa zapewnia:

**Separację odpowiedzialności**: Każda warstwa ma jasno zdefiniowane zadania, co ułatwia rozwój i utrzymanie
**Testowalność**: Możliwość niezależnego testowania każdej warstwy
**Skalowalność**: Łatwość dodawania nowych baz danych lub typów testów
**Maintainability**: Czytelna struktura ułatwiająca modyfikacje i rozszerzenia

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
