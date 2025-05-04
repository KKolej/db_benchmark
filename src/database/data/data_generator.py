import random
from dataclasses import dataclass
from typing import Generator, List, Dict, Any
from ..common.record_types import RecordType

@dataclass
class FullRecord:
    first_name: str
    last_name: str
    email: str
    address: str
    age: int
    client_id: int = 0

@dataclass
class SimpleRecord:
    value: int
    client_id: int = 0

class DataGenerator:

    first_names = [
        "Jan", "Anna", "Piotr", "Maria", "Krzysztof", "Agnieszka", "Tomasz", "Magdalena",
        "Marek", "Ewa", "Andrzej", "Barbara", "Rafał", "Joanna", "Grzegorz", "Małgorzata",
        "Michał", "Monika", "Paweł", "Elżbieta"
    ]

    last_names = [
        "Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski",
        "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski", "Mazur",
        "Wojciechowski", "Kwiatkowski", "Krawczyk", "Kaczmarek", "Piotrowski", "Grabowski"
    ]

    addresses = [
        "ul. Kwiatowa 10, 00-001 Warszawa", "ul. Leśna 5, 30-001 Kraków",
        "ul. Polna 8, 40-001 Katowice", "ul. Słoneczna 12, 50-001 Wrocław",
        "ul. Mickiewicza 7, 60-001 Poznań", "ul. Piłsudskiego 3, 70-001 Gdańsk",
        "ul. Kościuszki 15, 80-001 Łódź", "ul. 3 Maja 9, 90-001 Lublin",
        "ul. Jana Pawła II 20, 10-001 Szczecin", "ul. Reymonta 11, 20-001 Bydgoszcz"
    ]

    _name_combinations = None
    _email_cache = {}

    @classmethod
    def _initialize_cache(cls):
        if cls._name_combinations is None:
            cls._name_combinations = [(first, last) for first in cls.first_names for last in cls.last_names]
            for first, last in cls._name_combinations:
                email_key = (first, last)
                if email_key not in cls._email_cache:
                    cls._email_cache[email_key] = f"{first.lower()}.{last.lower()}@example.com"

    @classmethod
    def generate_email(cls, first_name: str, last_name: str) -> str:
        if cls._name_combinations is None:
            cls._initialize_cache()
        email_key = (first_name, last_name)
        if email_key in cls._email_cache:
            return cls._email_cache[email_key]
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        cls._email_cache[email_key] = email
        return email



    @classmethod
    def generate_people_list(cls, count: int, client_id: int, record_type: str) -> List[Dict[str, Any]]:
        if record_type.lower() == RecordType.SMALL.value:
            return cls._generate_simple_records(count, client_id)
        if cls._name_combinations is None:
            cls._initialize_cache()
        result = []
        name_combinations = cls._name_combinations
        addresses = cls.addresses
        email_cache = cls._email_cache
        for _ in range(count):
            first_name, last_name = random.choice(name_combinations)
            result.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': email_cache[(first_name, last_name)],
                'address': random.choice(addresses),
                'age': random.randint(18, 80),
                'client_id': client_id
            })
        return result

    @classmethod
    def _generate_simple_records(cls, count: int, client_id: int) -> List[Dict[str, Any]]:
        result = []
        for _ in range(count):
            result.append({
                'value': random.randint(1, 1000000),
                'client_id': client_id
            })
        return result

    @classmethod
    def generate_records_stream(cls, count: int, client_id: int, record_type: str) -> Generator[Dict[str, Any], None, None]:
        if record_type.lower() == RecordType.SMALL.value:
            for _ in range(count):
                yield {
                    'value': random.randint(1, 1000000),
                    'client_id': client_id
                }
            return
        if cls._name_combinations is None:
            cls._initialize_cache()
        name_combinations = cls._name_combinations
        addresses = cls.addresses
        email_cache = cls._email_cache
        for _ in range(count):
            first_name, last_name = random.choice(name_combinations)
            yield {
                'first_name': first_name,
                'last_name': last_name,
                'email': email_cache[(first_name, last_name)],
                'address': random.choice(addresses),
                'age': random.randint(18, 80),
                'client_id': client_id
            }