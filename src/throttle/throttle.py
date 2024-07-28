import logging
import sys
import time
from enum import Enum, auto
from threading import Thread, Lock
from typing import Callable, List, Optional, Any


class ProgressState(Enum):
    """Represents the state of the progress indicator."""
    RUNNING = auto()
    STOPPED = auto()


class Throttle:
    """
    A versatile progress indicator library for Python, providing multiple styles
    and customization options to visualize the progress of your tasks.

    Args:
        total (int): The total number of items or steps in the process.
        unit (str, optional): The unit of progress (e.g., 'items', 'steps', 'bytes').
                                Defaults to "items".
        desc (str, optional): A short description of the process being tracked.
                                Defaults to "Progress".
        bar_length (int, optional): The length of the progress bar in characters.
                                    Defaults to 20.
        refresh_rate (float, optional): How often the progress indicator is updated
                                        (in seconds).
                                        Default to 0.1.
        spinner (bool, optional): If True, uses a spinning animation instead of a bar.
                                    Defaults to False.
        style (str, optional): The style of the progress indicator.
        Options are 'bar',
                                'dots', 'time_clock'.
                                Defaults to "bar".
        color (str, optional): The color of the progress bar ('blue', 'green', 'red').
                                Color support may vary depending on your terminal.
                                Defaults to "blue".
        fill_char (str, optional): The character used to fill the progress bar.
                                    Defaults to "#".
        empty_char (str, optional): The character used for the empty part of the
                                    progress bar. Defaults to "".
        render_callback (Optional[Callable[[int, int, str, str, str], str]], optional):
                                            A custom function to render the progress
                                            indicator.
                                            If provided, this overrides
                                            the default rendering.
                                            The callback
                                            function should take five arguments:
                                                - completed: The current progress count.
                                                - total: The total progress count.
                                                - desc: The description of the task.
                                                - fill_char: The fill character.
                                                - empty_char: The empty character.
                                            Defaults to None.
        update_callback (Optional[Callable[[int], None]], optional):
                                            A custom function to be called whenever
                                            the progress is updated.
                                            The callback
                                            function should take one argument:
                                                - completed: The current progress count.
                                            Defaults to None.

    Raises:
        ValueError: Of invalid style, color, fill_char, or empty_char are provided.

    Example Usage:
        ```python
        from throttle import time

        # Simple progress bar
        with Throttle(total=100, desc="Processing") as throttle:
            for i in range(100):
                # Your code here
                time.sleep(0.1)
                throttle.update()

        # Progress bar with custom rendering
        def my_render_callback(completed, total, desc, fill_char, empty_char):
            percentage = int ((completed / total) * 100)
            return f"{desc}: [{'|' * percentage}{'.'
            * (100 - percentage)}] {percentage}%"

        with Throttle(total=50, desc="Custom Rendering", render_callback=my_render_callback) as t:
            for i in range(50):
                # Your code here
                time.sleep(0.2)
                t.update()
        ```
    """
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

        if total <= 0:
            raise ValueError("Total number of items must be greater than 0. 🤔")

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

        # Clock Emojis for Progress Indicator
        self.clock_emojis = [
            "🕝", "🕞", "🕟", "🕠", "🕡", "🕢", "🕒", "🕓", "🕔", "🕕",
            "🕖", "🕗", "🕛", "🕧", "🕜", "🕣", "🕘", "🕤", "🕙", "🕥",
            "🕚", "🕦"
        ]

    def render(self) -> str:
        """Renders the progress indicator based on the chosen style.

        This method determines the appropriate rendering function based on
        the current style and calls it to get the formatted progress string.

        Returns:
            str: The formatted progress indicator string.
        """
        if self.spinner:
            return self._default_render_spinner()
        elif self.style == "bar":
            return self._default_render_bar()
        elif self.style == "dots":
            return self._default_render_dots()
        elif self.style == "time_clock":
            return self._default_render_time_clock()
        else:
            return self._default_render_bar()  # Default to bar

    def _validate_input(self, style, color, fill_char, empty_char):
        """Validates the input parameters for the Throttle instance."""
        if style not in self.VALID_STYLES:
            raise ValueError(f"Invalid style: {style}. 🤔 Valid styles are: {self.VALID_STYLES}")
        if color not in self.VALID_COLORS:
            raise ValueError(f"Invalid color: {color}. 🎨 Valid colors are: {self.VALID_COLORS}")
        if not fill_char or len(fill_char) != 1:
            raise ValueError(f"Invalid fill_char: {fill_char}. 🚧 Fill character must be a single character.")
        if not empty_char or len(empty_char) != 1:
            raise ValueError(f"Invalid empty_char: {empty_char}. 🚧 Empty character must be a single character.")

    def update(self, amount: int = 1):
        """
        Updates the progress counter.

        Args:
            amount (int, optional): The amount by which to increment the progress.
                                    Default to 1.
        """
        with self.lock:
            self.completed += amount
            if self.update_callback:
                self.update_callback(self.completed)

    def _default_render_bar(self) -> str:
        """Default rendering for the bar style progress indicator."""
        progress = int((self.completed / self.total) * self.bar_length)
        filled_bar = "[" + self.fill_char * progress + self.empty_char * (
                self.bar_length - progress) + "]"
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
        """Default rendering for the spinner style progress indicator."""
        return f"{self.desc}: {self.spinner_chars[self.spinner_index]}"

    def _default_render_dots(self) -> str:
        """Default rendering for the dots style progress indicator."""
        dots = "." * (self.completed % 4)
        return f"{self.desc}: {dots}"

    def _default_render_time_clock(self) -> str:
        """Default rendering for the time clock style progress indicator."""
        # Calculate the clock emoji index based on progress
        clock_index = int((self.completed / self.total) * len(self.clock_emojis)) % len(
            self.clock_emojis)
        return f"{self.desc}: {self.clock_emojis[clock_index]}"

    def _render_progress(self):
        """Handles rendering the progress indicator in a separate thread."""
        while self.running:
            with self.lock:
                if self.render_callback:
                    output = self.render_callback(self.completed, self.total, self.desc,
                                                  self.fill_char,
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
                self.spinner_index = (self.spinner_index + 1) % len(
                    self.spinner_chars)
            time.sleep(self.refresh_rate)

    def close(self):
        """Stops the progress indicator and cleans up the console output."""
        self.running = False
        if self.render_thread:
            self.render_thread.join()
        sys.stdout.write("\n")
        sys.stdout.flush()

    def start(self):
        """Starts the progress indicator rendering in a separate thread."""
        self.render_thread = Thread(target=self._render_progress)
        self.render_thread.daemon = True
        self.render_thread.start()

    def __enter__(self):
        """Starts the progress indicator when used in a `with` statement."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the progress indicator when exiting a `with` block."""
        self.close()

    def with_function(self, func: Callable[[Any, 'Throttle'], None], data: List[Any], *args, **kwargs):
        """
        Executes a function with integrated progress tracking.

        This method is designed to automatically update the progress indicator
        as the provided function `func` iterates through the given `data`.

        Args:
            func (Callable[[Any, 'Throttle'], None]): The function to execute.
                                                        It should accept a data item
                                                        and a Throttle instance as
                                                        arguments.
            data (List[Any]): The list of data items to process.
            *args: Additional positional arguments to pass to `func`.
            **kwargs: Additional keyword arguments to pass to `func`.

        Raises:
            ValueError: If the provided data list is empty.
        """
        if not data:
            raise ValueError("Data list is empty. 😕 Please provide some data to process.")

        try:
            for i, item in enumerate(data):
                func(item, self)
                self.update()

                # Optional: Log progress at regular intervals
                if i % 10 == 0:  # Log every 10 items (adjust as needed)
                    logging.info(f"Processed {i + 1}/{self.total} items.")

                time.sleep(0.1)  # Consider making this delay configurable
        except Exception as e:
            self.close()  # Ensure the progress indicator is closed on error
            print(f"ERROR:root:An error occurred during processing: {e}")
            raise

        self.close()


def throttle_decorator(total: int, **kwargs):
    """
    Decorator to easily add a progress indicator to a function.

    This decorator simplifies the process of integrating a Throttle
    progress indicator into your functions.

    Args:
        total (int): The total number of steps or items the decorated function
                    will process.
        **kwargs: Additional keyword arguments to customize the Throttle instance
                (see Throttle class documentation for options).

    Returns:
        Callable: The decorated function.

    Example Usage:
        ```python
        from throttle import throttle_decorator
        import time

        @throttle_decorator(total=10, desc="Downloading", style="bar", color="green")
        def my_function(data, throttle_loader=None):
            for item in data:
                # Do some work here
                time.sleep(1)
                if throttle_loader:
                    throttle_loader.update()

        data_to_process = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        my_function(data_to_process)
        ```
    """

    def decorator(func: Callable):
        def wrapper(*args, **func_kwargs):
            with Throttle(total, **kwargs) as loader:
                result = func(*args, throttle_loader=loader, **func_kwargs)
            return result

        return wrapper

    return decorator
