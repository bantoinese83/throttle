## 🎉 Throttle: A Simple Python Progress Bar Library 🎉

Tired of watching your code run without any feedback? ⏳ The `throttle` library makes it easy to add progress bars,
spinners, clock and dots to your Python scripts, so you can see the progress of long-running operations.

### Features

* **Multiple Styles:**
    * **Bar Style:** Classic progress bar with percentage and completed/total items.
    * **Spinner Style:** A simple spinning animation for visual feedback.
    * **Dots Style:** A minimalist style with dots that increment as progress is made.
    * **Clock Style:** A clock-style progress bar that the hands move as progress is made.
* **Customization:**
    * **Color:** Choose from blue, green, or red (or leave blank for default).
    * **Description:** Add a custom description to the progress bar.
    * **Fill and Empty Characters:** Customize the appearance of the bar with different characters.
    * **Refresh Rate:** Control how often the progress bar updates.
* **Flexibility:**
    * **Manual Updates:** Update the progress bar directly with the `update()` method.
    * **Decorator:** Easily apply a progress bar to any function with the `progress_decorator` decorator.
    * **Callback Functions:** Customize the rendering of the progress bar with custom callback functions.

## Getting Started

To get started with the `throttle` library, simply install it via pip:

Install the library:

```bash
pip install throttle
```

```python
Import the necessary components:
from throttle import ProgressLoader, progress_decorator
#Create a progress bar:
progress_bar = ProgressLoader(total=10, desc="My Progress", style="bar", color="blue")

#Start the progress bar:
progress_bar.start()

#Update the progress:
progress_bar.update() # Increment the progress by 1
progress_bar.update(amount=3) # Increment the progress by 3

#Stop the progress bar:
progress_bar.close()
```

### Usage

```python
from throttle import ProgressLoader, my_example_function, process_data

test_data = list(range(1, 11))

# Bar style progress bar (blue)
with ProgressLoader(total=10, desc="Processing data", style="bar", color="blue") as test_loader:
    test_loader.with_function(my_example_function, test_data)

# Spinner style progress bar
with ProgressLoader(total=10, desc="Processing data", spinner=True) as test_loader:
    test_loader.with_function(my_example_function, test_data)

# Dots style progress bar (custom fill/empty characters)
with ProgressLoader(total=10, desc="Processing data", style="dots", fill_char="*", empty_char=".") as test_loader:
    test_loader.with_function(my_example_function, test_data)

# Clock style progress bar 
with ProgressLoader(total=10, desc="Processing data", style="clock") as test_loader:
    test_loader.with_function(my_example_function, test_data)

# Manual updates (bar style)
test_loader = ProgressLoader(total=5, desc="Loading", style="bar", color="green")
test_loader.start()
for i in range(5):
    test_loader.update()
    time.sleep(0.5)
test_loader.close()
```

### Using the progress_decorator

```python
from throttle import progress_decorator, process_data

test_data = list(range(1, 11))


@progress_decorator(total=10, desc="Processing data", style="bar", color="blue")
def process_data(data: List[int], progress_loader: ProgressLoader):
    for item in data:
        my_example_function(item, progress_loader)


process_data(test_data)
```

### Custom Callback Functions

```python
from throttle import ProgressLoader, my_example_function, process_data

test_data = list(range(1, 11))


def custom_callback(progress_loader):
    print(f"Progress: {progress_loader.progress}/{progress_loader.total}")
    print(f"Percentage: {progress_loader.percentage:.2f}%")
    print(f"Elapsed Time: {progress_loader.elapsed_time:.2f}s")
    print(f"Estimated Time Remaining: {progress_loader.eta:.2f}s")

    # Custom logic here


with ProgressLoader(total=10, desc="Processing data", style="bar", color="blue",
                    callback=custom_callback) as test_loader:
    test_loader.with_function(my_example_function, test_data)
``` 

# Real-World Examples 🌎

### 1. Downloading Files

```python
from throttle import ProgressLoader
import requests


def download_file(url, filename, progress_loader):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    progress_loader.update(len(chunk))


url = "https://example.com/large_file.zip"
filename = "large_file.zip"

with ProgressLoader(total=total_size, unit='bytes', desc='Downloading File') as loader:
    download_file(url, filename, loader)

print(f"File downloaded: {filename}")
```

### 2. Processing a Large Dataset

```python
from throttle import progress_decorator, ProgressLoader
import pandas as pd


@progress_decorator(total=len(data), desc='Processing Data')
def process_data(data: pd.DataFrame, progress_loader: ProgressLoader):
    for index, row in data.iterrows():
        # Process each row of the DataFrame
        # ...
        progress_loader.update()


data = pd.read_csv("large_dataset.csv")
process_data(data)
```

### 3. Running Multiple Tasks Concurrently

```python
from throttle import ProgressLoader
from threading import Thread


def long_running_task(task_id, progress_loader):
    for i in range(10):


# Simulate some work
time.sleep(0.5)
progress_loader.update()
print(f"Task {task_id} completed")

with ProgressLoader(total=30, desc='Running Tasks') as loader:
    threads = [Thread(target=long_running_task, args=(i, loader)) for i in range(3)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print("All tasks completed")
```

### 4. Custom Callback Function Long Running Task

```python
from throttle import ProgressLoader
import time

def long_running_task(total, progress_loader):
    for i in range(total):
        # Simulate some work
        time.sleep(0.5) 
        progress_loader.update()

def custom_callback(progress_loader):
    print(f"Progress: {progress_loader.progress}/{progress_loader.total}")
    print(f"Percentage: {progress_loader.percentage:.2f}%")
    print(f"Elapsed Time: {progress_loader.elapsed_time:.2f}s")
    print(f"Estimated Time Remaining: {progress_loader.eta:.2f}s")
    print("-" * 20)

with ProgressLoader(total=10, desc='Running Task', callback=custom_callback) as loader:
    long_running_task(10, loader)

print("Task completed")
```

### 5. Customizing the Progress Bar Appearance

```python
from throttle import ProgressLoader

with ProgressLoader(total=10, desc='Custom Progress Bar', style='bar', color='red', fill_char='*', empty_char='.') as loader:
    for i in range(10):
        loader.update()
        time.sleep(0.5)
        
print("Progress bar completed")
```

### 6. Generating Thumbnails

```python
def generate_thumbnails(image_urls, thumbnail_dir, width, height):
    success_count = [0]
    error_count = [0]

    with ProgressLoader(total=len(image_urls), desc="Generating Thumbnails", style="time_clock",
                        color="blue") as loader:
        for image_url in image_urls:
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                thumbnail_path = os.path.join(thumbnail_dir, os.path.basename(image_url))
                image.thumbnail((width, height))
                image.save(thumbnail_path)
                logging.info(f"Generated thumbnail: {thumbnail_path}")
                success_count[0] += 1
            except Exception as e:
                logging.error(f"Error generating thumbnail for {image_url}: {e}")
                error_count[0] += 1
            finally:
                loader.update()

    logging.info(f"Thumbnail generation completed with {success_count[0]} successes and {error_count[0]} errors.")

```
#### `MANIFEST.in`

```plaintext
include README.md