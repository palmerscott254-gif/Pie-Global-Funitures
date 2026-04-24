import time
import threading


PROCESS_START_MONOTONIC = time.perf_counter()
_first_request_seen = False
_state_lock = threading.Lock()


def mark_request_and_get_state():
    """
    Mark first request and return startup state.

    Returns:
        (is_cold_request, uptime_ms)
    """
    global _first_request_seen
    uptime_ms = (time.perf_counter() - PROCESS_START_MONOTONIC) * 1000

    with _state_lock:
        if not _first_request_seen:
            _first_request_seen = True
            return True, uptime_ms

    return False, uptime_ms


def get_startup_state():
    """Return lightweight startup state without triggering heavy work."""
    return {
        'is_cold_start': not _first_request_seen,
        'uptime_ms': round((time.perf_counter() - PROCESS_START_MONOTONIC) * 1000, 2),
    }
