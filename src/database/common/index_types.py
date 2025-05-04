from enum import Enum


class IndexType(Enum):
    ALL = "all"
    NO_INDEXES = "no_indexes"
    FOREIGN_KEY = "foreign_key"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls(value.lower())
        except ValueError:
            return None

    @classmethod
    def get_all_types(cls):
        return [index_type.value for index_type in cls if index_type != cls.ALL]

    def __str__(self):
        return self.value
