import sys
import time
from typing import Any

from src.throttle import throttle_decorator, Throttle


def my_example_function(data: Any, progress_loader: Throttle) -> None:
    """Simulates a function that processes data."""
    sys.stdout.write(f"Processing {data} ")
    sys.stdout.flush()
    time.sleep(0.5)
    progress_loader.update()


@throttle_decorator(total=10, desc="Processing data", style="bar", color="blue")
def process_data(data, throttle_loader=None):
    for item in data:
        # Simulate data processing
        time.sleep(1)
        if throttle_loader:
            throttle_loader.update()
        print(f"Processed {item}")
