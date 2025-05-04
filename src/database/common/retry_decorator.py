import time
import logging
from functools import wraps
from ..utils.logging_config import ProgressLogger


class RetryDecorator:
    @staticmethod
    def retry_on_error(max_retries: int = 3, delay_factor: float = 0.5):
        def decorator(fn):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                for i in range(max_retries):
                    try:
                        return fn(*args, **kwargs)
                    except Exception as e:
                        ProgressLogger.error(f'Error (attempt {i+1}/{max_retries}): {e}')
                        if i == max_retries-1:
                            raise
                        time.sleep(delay_factor * (2**i))
            return wrapped
        return decorator
