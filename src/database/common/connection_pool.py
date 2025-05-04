import threading
from ..utils.logging_config import ProgressLogger


class ConnectionPool:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self._lock = threading.Lock()
        self._connections = []
        ProgressLogger.print(f'Initialized connection pool (size={pool_size})')

    def create_connection(self):
        raise NotImplementedError

    def get_connection(self):
        with self._lock:
            for conn in self._connections:
                if conn.is_connected():
                    self._connections.remove(conn)
                    return conn
            if len(self._connections) < self.pool_size:
                conn = self.create_connection()
                ProgressLogger.print('Created new connection')
                return conn
            ProgressLogger.error(f'Connection limit reached ({self.pool_size})')
            return self.create_connection()

    def release_connection(self, conn):
        if not conn:
            return
        with self._lock:
            if conn.is_connected() and len(self._connections) < self.pool_size:
                self._connections.append(conn)
                return
        conn.close_connection()
        ProgressLogger.print('Closed connection')

    def close_all(self):
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close_connection()
                except Exception as e:
                    ProgressLogger.error(f'Error closing connection: {e}')
            self._connections.clear()
            ProgressLogger.print('Closed all connections')
