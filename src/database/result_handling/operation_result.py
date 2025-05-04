from dataclasses import dataclass
from datetime import datetime

@dataclass
class OperationResult:
    database: str
    operation: str
    records: int
    time: float
    timestamp: datetime
    timing_method: str
    indexes_type: str
    threads: int
    iteration: int
