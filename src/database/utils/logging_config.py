import logging
import threading
import builtins

_current_iteration = "0"
_iteration_lock = threading.Lock()
_show_progress = True
_original_print = builtins.print

class IterationFilter(logging.Filter):
    def filter(self, record):
        with _iteration_lock:
            record.iteration = _current_iteration
        return True

class ProgressLogger:
    @staticmethod
    def print(args):
        ProgressLogger.important_info(args)

    @staticmethod
    def important_info(message, iteration=None):
        it = iteration if iteration is not None else _current_iteration
        _original_print(f"[INFO] [Iteracja {it}] {message}")

    @staticmethod
    def error(message, iteration=None):
        it = iteration if iteration is not None else _current_iteration
        _original_print(f"[ERROR] [Iteracja {it}] {message}")

    @staticmethod
    def warn(message, iteration=None):
        it = iteration if iteration is not None else _current_iteration
        _original_print(f"[WARN] [Iteracja {it}] {message}")


def configure_logging(show_progress=True):
    global _show_progress
    _show_progress = show_progress

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    fmt = ('[%(levelname)s] [Iteracja %(iteration)s] %(message)s' if show_progress
           else '[%(levelname)s] %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(fmt))
    console_handler.addFilter(IterationFilter())

    root_logger.setLevel(logging.INFO if show_progress else logging.WARNING)
    root_logger.addHandler(console_handler)

    builtins.print = custom_print if show_progress else ProgressLogger.print


def set_current_iteration(iteration):
    global _current_iteration
    with _iteration_lock:
        _current_iteration = str(iteration)


def custom_print(*args, **kwargs):
    if not _show_progress:
        return
    with _iteration_lock:
        it = _current_iteration
    if args:
        first = str(args[0])
        if not first.startswith('[Iteracja') and not first.startswith('[INFO]') and not first.startswith('[BŁĄD]'):
            args = (f"[Iteracja {it}] {first}",) + args[1:]
    _original_print(*args, **kwargs)
