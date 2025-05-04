# Projekt porównania wydajności baz danych

Projekt i implementacja narzędzia do analizy porównawczej wydajności systemów bazodanowych

### Wymagane oprogramowanie

- **Docker** i **Docker Compose** - do uruchomienia kontenerów z bazami danych
- **Python 3.12+** - do uruchomienia aplikacji
- **Poetry** - do zarządzania zależnościami

### Instalacja wymagań na Ubuntu/Debian

```bash
# Instalacja Dockera i Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# Instalacja Pythona 3.12 (jeśli nie jest dostępny w standardowych repozytoriach)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Instalacja Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Dodanie Poetry do PATH (dodaj to do ~/.bashrc lub ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

## Konfiguracja projektu

1. Sklonuj repozytorium (lub pobierz jako ZIP i rozpakuj):
```bash
git clone https://github.com/twojrepozytorium/database-comparison.git
cd database-comparison
```

2. Uruchom bazy danych w kontenerach Docker:
```bash
docker compose up -d
```

3. Zainstaluj zależności projektu za pomocą Poetry:
```bash
poetry install
```

4. Dodaj plik .env w głównym folderze przykładowe wartości do obrazów uruchomionych w docker

```
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=root
MONGO_PASSWORD=example
MONGO_DB=testdb

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=example
MYSQL_DB=testdb
```

5. Uruchom projekt:
```bash
poetry run python src/main.py
```

## Opcje uruchomienia

Program można uruchomić z różnymi opcjami, które pozwalają dostosować parametry testów wydajnościowych.

### Podstawowe opcje

```bash
domyśle wartości do uruchomienia testóœ można zmienić w pliku main lub uruchamiając program z konsoli

# Domyślne uruchomienie (10000 rekordów, obie bazy danych, wszystkie typy indeksów)
poetry run python src/main.py

# Uruchomienie testów dla 1000 rekordów
poetry run python src/main.py --records 1000

# Uruchomienie testów tylko dla indeksu
poetry run python src/main.py --indexes-type foreign_key

# Uruchomienie testów bez indeksów
poetry run python src/main.py --indexes-type no_indexes

# Uruchomienie testów z włączonym logowaniem postępu
poetry run python src/main.py --log-progress True

# Uruchomienie testów z większą liczbą iteracji
poetry run python src/main.py --iterations 5

# Uruchomienie testów z określoną liczbą klientów
# Każdy klient przetwarza pełną liczbę rekordów (4 klientów x 100000 rekordów = 400000 rekordów w bazie)
poetry run python src/main.py --clients 4

# Uruchomienie testów z określonym rozmiarem partii rekordów
poetry run python src/main.py --batch-size 10000

# Uruchomienie testów z określonym rozmiarem puli połączeń MySQL
poetry run python src/main.py --mysql-pool-size 16

# Uruchomienie testów z określonym rozmiarem puli połączeń MongoDB
poetry run python src/main.py --mongo-pool-size 100
```

## Zapisywanie wyników

Wszystkie wyniki testów są automatycznie zapisywane do folderu `results` w osobnych podfolderach dla każdego pomiaru.

## Logowanie

Aplikacja używa systemu logowania ProgressLogger, który wyświetla informacje o postępie testów. Możesz włączyć lub wyłączyć logowanie za pomocą opcji `--log-progress`:
