import gc
from typing import List, Dict, Any
from .data_generator import DataGenerator


class MultiClientDataGenerator:

    @classmethod
    def generate_data_for_clients(cls, total_count: int, num_clients: int, record_type: str = 'big') -> List[List[Dict[str, Any]]]:

        base_users = DataGenerator.generate_people_list(total_count, client_id=0, record_type=record_type)

        results: List[List[Dict[str, Any]]] = []
        for client_id in range(num_clients):
            batch = [
                {**user, 'client_id': client_id}
                for user in base_users
            ]
            results.append(batch)

        gc.collect()
        return results
