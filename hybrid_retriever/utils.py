import time
import functools

def measure_latency(func):
    """Decorator to measure execution time of retrieval methods."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        latency = time.monotonic() - start
        return result, latency
    return wrapper
