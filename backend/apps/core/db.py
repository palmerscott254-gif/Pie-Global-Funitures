import threading
from django.db import connections


_db_initialized = False
_db_lock = threading.Lock()


def ensure_db_connection():
    """
    Lazily initialize default DB connection once per process.

    Returns:
        True if this call initialized the connection for the first time.
        False if connection was already initialized.
    """
    global _db_initialized

    if _db_initialized:
        return False

    with _db_lock:
        if _db_initialized:
            return False

        connections['default'].ensure_connection()
        _db_initialized = True
        return True
