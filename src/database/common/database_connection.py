from abc import abstractmethod


class DatabaseConnection:
    @abstractmethod
    def get_cursor(self):
        pass
    
    @abstractmethod
    def close_connection(self):
        pass
    
    @abstractmethod
    def is_connected(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
    
    def __del__(self):
        try:
            self.close_connection()
        except Exception:
            pass
