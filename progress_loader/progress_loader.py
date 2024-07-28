import sys
import time
from enum import Enum, auto
from threading import Thread, Lock
from typing import Callable, List, Optional, Any


class ProgressState(Enum):
    """Represents the state of the progress bar."""
    RUNNING = auto()
    STOPPED = auto()


class ProgressLoader:
    VALID_STYLES = ["bar", "dots", "time_clock"]
    VALID_COLORS = ["blue", "green", "red"]

    def __init__(
            self,
            total: int,
            unit: str = "items",
            desc: str = "Progress",
            bar_length: int = 20,
            refresh_rate: float = 0.1,
            spinner: bool = False,
            style: str = "bar",
            color: str = "blue",
            fill_char: str = "#",
            empty_char: str = " ",
            render_callback: Optional[Callable[[int, int, str, str, str], str]] = None,
            update_callback: Optional[Callable[[int], None]] = None,
    ):
        # Input Validation
        self._validate_input(style, color, fill_char, empty_char)

        self.total = total
        self.unit = unit
        self.desc = desc
        self.bar_length = bar_length
        self.completed = 0
        self.refresh_rate = refresh_rate
        self.lock = Lock()
        self.running = True
        self.render_thread = None
        self.spinner = spinner
        self.spinner_chars = ["-", "\\", "|", "/"]
        self.spinner_index = 0
        self.style = style
        self.color = color
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.render_callback = render_callback
        self.update_callback = update_callback

        # Clock Emojis for Progress Bar
        self.clock_emojis = [
            "🕝", "🕞", "🕟", "🕠", "🕡", "🕢", "🕒", "🕓", "🕔", "🕕",
            "🕖", "🕗", "🕛", "🕧", "🕜", "🕣", "🕘", "🕤", "🕙", "🕥",
            "🕚", "🕦"
        ]

    def _validate_input(self, style, color, fill_char, empty_char):
        """Validates the input parameters."""
        if style not in self.VALID_STYLES:
            raise ValueError(f"Invalid style: {style}. 🤔 Valid styles are: {self.VALID_STYLES}")
        if color not in self.VALID_COLORS:
            raise ValueError(f"Invalid color: {color}. 🎨 Valid colors are: {self.VALID_COLORS}")
        if not fill_char or len(fill_char) != 1:
            raise ValueError(f"Invalid fill_char: {fill_char}. 🚧 Fill character must be a single character.")
        if not empty_char or len(empty_char) != 1:
            raise ValueError(f"Invalid empty_char: {empty_char}. 🚧 Empty character must be a single character.")

    def update(self, amount: int = 1):
        """Updates the progress counter by the specified amount."""
        with self.lock:
            self.completed += amount
            if self.update_callback:
                self.update_callback(self.completed)

    def _default_render_bar(self) -> str:
        """Default rendering for the progress bar."""
        progress = int((self.completed / self.total) * self.bar_length)
        filled_bar = "[" + self.fill_char * progress + self.empty_char * (self.bar_length - progress) + "]"
        percentage = int((self.completed / self.total) * 100)

        # Add color support (if available)
        if self.color == "blue":
            filled_bar = f"\033[94m{filled_bar}\033[0m"  # Blue
        elif self.color == "green":
            filled_bar = f"\033[92m{filled_bar}\033[0m"  # Green
        elif self.color == "red":
            filled_bar = f"\033[91m{filled_bar}\033[0m"  # Red

        return f"{self.desc}: {filled_bar} {percentage}% ({self.completed}/{self.total} {self.unit})"

    def _default_render_spinner(self) -> str:
        """Default rendering for the spinner animation."""
        return f"{self.desc}: {self.spinner_chars[self.spinner_index]}"

    def _default_render_dots(self) -> str:
        """Default rendering for the dots style loader."""
        dots = "." * (self.completed % 4)
        return f"{self.desc}: {dots}"

    def _default_render_time_clock(self) -> str:
        """Default rendering for the time clock style loader."""
        # Calculate the clock emoji index based on progress
        clock_index = int((self.completed / self.total) * len(self.clock_emojis)) % len(self.clock_emojis)
        return f"{self.desc}: {self.clock_emojis[clock_index]}"

    def _render_progress(self):
        """Renders the progress bar, spinner, or other style in a separate thread."""
        while self.running:
            with self.lock:
                if self.render_callback:
                    output = self.render_callback(self.completed, self.total, self.desc, self.fill_char,
                                                  self.empty_char)
                elif self.spinner:
                    output = self._default_render_spinner()
                elif self.style == "bar":
                    output = self._default_render_bar()
                elif self.style == "dots":
                    output = self._default_render_dots()
                elif self.style == "time_clock":
                    output = self._default_render_time_clock()
                else:
                    output = self._default_render_bar()  # Default to bar

                sys.stdout.write(f"\r{output}")
                sys.stdout.flush()
                self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            time.sleep(self.refresh_rate)

    def close(self):
        """Stops the progress bar rendering and cleans up the console."""
        self.running = False
        if self.render_thread:
            self.render_thread.join()
        sys.stdout.write("\n")
        sys.stdout.flush()

    def start(self):
        """Starts the progress bar rendering in a separate thread."""
        self.render_thread = Thread(target=self._render_progress)
        self.render_thread.daemon = True
        self.render_thread.start()

    def __enter__(self):
        """Starts the progress bar when entering a `with` block."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the progress bar when exiting a `with` block."""
        self.close()

    def with_function(self, func: Callable[[Any, 'ProgressLoader'], None], data: List[Any], *args, **kwargs):
        """Executes a function with progress tracking."""
        if not data:
            raise ValueError("Data list is empty. 😕 Please provide some data to process.")
        try:
            for item in data:
                func(item, self)
                self.update()
                time.sleep(0.1)
        except Exception as e:
            sys.stdout.write(f"\n{str(e)}\n")
            self.close()
            raise e

        self.close()


def progress_decorator(total: int, **kwargs):
    """Decorator for adding a progress loader to a function."""

    def decorator(func: Callable):
        def wrapper(*args, **func_kwargs):
            with ProgressLoader(total, **kwargs) as loader:
                result = func(*args, progress_loader=loader, **func_kwargs)
            return result

        return wrapper

    return decorator


def my_example_function(data: Any, progress_loader: ProgressLoader) -> None:
    """Simulates a function that processes data."""
    sys.stdout.write(f"Processing {data} ")
    sys.stdout.flush()
    time.sleep(0.5)
    progress_loader.update()


@progress_decorator(total=10, desc="Processing data", style="bar", color="blue")
def process_data(data: List[int], progress_loader: ProgressLoader):
    for item in data:
        my_example_function(item, progress_loader)


if __name__ == "__main__":
    test_data = list(range(1, 11))

    # Using with_function (bar style)
    with ProgressLoader(total=10, desc="Processing data", style="bar", color="blue") as test_loader:
        test_loader.with_function(my_example_function, test_data)

    # Using with_function with spinner
    with ProgressLoader(total=10, desc="Processing data", spinner=True) as test_loader:
        test_loader.with_function(my_example_function, test_data)

    # Using with_function with dot style
    with ProgressLoader(total=10, desc="Processing data", style="dots", fill_char="*", empty_char=".") as test_loader:
        test_loader.with_function(my_example_function, test_data)

    # Using update directly (bar style)
    test_loader = ProgressLoader(total=5, desc="Loading", style="bar", color="green")
    test_loader.start()
    for i in range(5):
        test_loader.update()
        time.sleep(0.5)
    test_loader.close()

    # Using decorator
    process_data(test_data)

    # Using Time Clock Style
    with ProgressLoader(total=10, desc="Time Clock Progress", style="time_clock") as time_clock_loader:
        time_clock_loader.with_function(my_example_function, test_data)
