import functools
import json
import os
from datetime import datetime, timedelta


class Cache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def cache_result(self, timeout_minutes: int = 60):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                cache_file = os.path.join(self.cache_dir, f"{key}.json")

                if os.path.exists(cache_file):
                    with open(cache_file, "r", encoding="utf-8") as handle:
                        cached = json.load(handle)
                    expiry = datetime.fromisoformat(cached["timestamp"]) + timedelta(minutes=timeout_minutes)
                    if expiry > datetime.now():
                        return cached["result"]

                result = func(*args, **kwargs)
                with open(cache_file, "w", encoding="utf-8") as handle:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "result": result,
                    }, handle)
                return result

            return wrapper

        return decorator
