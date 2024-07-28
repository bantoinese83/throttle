# ███████▒▒▒ 70%
# Throttle: A Python Progress Indicator Library

Tired of watching your code run without any feedback? ⏳ The `throttle` library makes it easy to add progress bars,
spinners, clocks, and dots to your Python scripts, so you can see the progress of long-running operations.

### Features

* **Multiple Styles:**
  * **Bar Style:** Classic progress bar with percentage and completed/total items.
  * **Spinner Style:** A simple spinning animation for visual feedback.
  * **Dots Style:** A minimalist style with dots that increment as progress is made.
  * **Clock Style:** A clock-style progress bar where the hands move as progress is made.
* **Customization:**
  * **Color:** Choose from blue, green, or red (or leave blank for the default).
  * **Description:** Add a custom description to the progress indicator.
  * **Fill and Empty Characters:** Customize the appearance of the bar with different characters.
  * **Refresh Rate:** Control how often the progress indicator updates.
* **Flexibility:**
  * **Manual Updates:** Update the progress indicator directly with the `update()` method.
  * **Decorator:** Easily apply a progress indicator to any function with the `progress_decorator` decorator.
  * **Callback Functions:** Customize the rendering of the progress indicator with custom callback functions.

## Getting Started

To get started with the `throttle` library, simply install it via pip:

```bash
pip install throttle
```

```python
# Import the necessary components
from throttle import Throttle, progress_decorator

# Create a progress bar
throttle = Throttle(total=10, desc="My Progress", style="bar", color="blue")

# Start the progress bar
throttle.start()

# Update the progress
throttle.update() # Increment the progress by 1
throttle.update(amount=3) # Increment the progress by 3

# Stop the progress bar
throttle.close()
```

### Usage

```python
from throttle import Throttle, my_example_function, process_data

test_data = list(range(1, 11))

# Bar style progress bar (blue)
with Throttle(total=10, desc="Processing data", style="bar", color="blue") as test_throttle:
  test_throttle.with_function(my_example_function, test_data)

# Spinner style progress bar
with Throttle(total=10, desc="Processing data", spinner=True) as test_throttle:
  test_throttle.with_function(my_example_function, test_data)

# Dots style progress bar (custom fill/empty characters)
with Throttle(total=10, desc="Processing data", style="dots", fill_char="*", empty_char=".") as test_throttle:
  test_throttle.with_function(my_example_function, test_data)

# Clock style progress bar 
with Throttle(total=10, desc="Processing data", style="clock") as test_throttle:
  test_throttle.with_function(my_example_function, test_data)

# Manual updates (bar style)
test_throttle = Throttle(total=5, desc="Loading", style="bar", color="green")
test_throttle.start()
for i in range(5):
  test_throttle.update()
  time.sleep(0.5)
test_throttle.close()
```

### Using the progress_decorator

```python
from throttle import progress_decorator, process_data

test_data = list(range(1, 11))

@throttle_decorator(total=10, desc="Processing data", style="bar", color="blue")
def process_data(data: List[int], throttle: Throttle):
  for item in data:
    my_example_function(item, throttle)

process_data(test_data)
```

### Custom Callback Functions

```python
from throttle import Throttle, my_example_function, process_data

test_data = list(range(1, 11))

def custom_callback(throttle):
  print(f"Progress: {throttle.progress}/{throttle.total}")
  print(f"Percentage: {throttle.percentage:.2f}%")
  print(f"Elapsed Time: {throttle.elapsed_time:.2f}s")
  print(f"Estimated Time Remaining: {throttle.eta:.2f}s")

  # Custom logic here

with Throttle(total=10, desc="Processing data", style="bar", color="blue",
              callback=custom_callback) as test_throttle:
  test_throttle.with_function(my_example_function, test_data)
``` 
### Customizing the Progress Bar Appearance

```python
from throttle import Throttle

with Throttle(total=10, desc='Custom Progress Bar', style='bar', color='red', fill_char='*', empty_char='.') as throttle:
  for i in range(10):
    throttle.update()
    time.sleep(0.5)

print("Progress bar completed")
```

# Real-World Examples 🌎

### 1. Downloading Files

```python
from throttle import Throttle
import requests

def download_file(url, filename, throttle):
  with requests.get(url, stream=True) as response:
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    with open(filename, 'wb') as file:
      for chunk in response.iter_content(chunk_size=8192):
        if chunk:
          file.write(chunk)
          throttle.update(len(chunk))

url = "https://example.com/large_file.zip"
filename = "large_file.zip"

with Throttle(total=total_size, unit='bytes', desc='Downloading File') as throttle:
  download_file(url, filename, throttle)

print(f"File downloaded: {filename}")
```

### 2. Processing a Large Dataset

```python
from throttle import progress_decorator, Throttle
import pandas as pd

@throttle_decorator(total=len(data), desc='Processing Data')
def process_data(data: pd.DataFrame, throttle: Throttle):
  for index, row in data.iterrows():
    # Process each row of the DataFrame
    # ...
    throttle.update()

data = pd.read_csv("large_dataset.csv")
process_data(data)
```

### 3. Running Multiple Tasks Concurrently

```python
from throttle import Throttle
from threading import Thread

def long_running_task(task_id, throttle):
  for i in range(10):
    # Simulate some work
    time.sleep(0.5)
    throttle.update()
  print(f"Task {task_id} completed")

with Throttle(total=30, desc='Running Tasks') as throttle:
  threads = [Thread(target=long_running_task, args=(i, throttle)) for i in range(3)]
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()

print("All tasks completed")
```

### 4. Custom Callback Function Long Running Task

```python
from throttle import Throttle
import time

def long_running_task(total, throttle):
  for i in range(total):
    # Simulate some work
    time.sleep(0.5)
    throttle.update()

def custom_callback(throttle):
  print(f"Progress: {throttle.progress}/{throttle.total}")
  print(f"Percentage: {throttle.percentage:.2f}%")
  print(f"Elapsed Time: {throttle.elapsed_time:.2f}s")
  print(f"Estimated Time Remaining: {throttle.eta:.2f}s")
  print("-" * 20)

with Throttle(total=10, desc='Running Task', callback=custom_callback) as throttle:
  long_running_task(10, throttle)

print("Task completed")
```

### 6. Generating Thumbnails

```python
from throttle import Throttle
import requests
from PIL import Image
from io import BytesIO
import os
import logging

def generate_thumbnails(image_urls, thumbnail_dir, width, height):
  success_count = [0]
  error_count = [0]

  with Throttle(total=len(image_urls), desc="Generating Thumbnails", style="time_clock",
                color="blue") as throttle:
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
        throttle.update()

  logging.info(f"Thumbnail generation completed with {success_count[0]} successes and {error_count[0]} errors.")
```




#### `MANIFEST.in`

```plaintext
include README.md