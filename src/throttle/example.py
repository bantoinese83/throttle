import logging
import os
import time
from io import BytesIO

import pandas as pd
import requests
from PIL import Image

from throttle import Throttle, throttle_decorator

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

# Create test_data directory if it doesn't exist
test_data_dir = "test_data"
os.makedirs(test_data_dir, exist_ok=True)


def create_test_data(filename, data):
    """Creates a test data file."""
    filepath = os.path.join(test_data_dir, filename)
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write(data)
        logging.info(f"Created test data file: {filename}")
    else:
        logging.info(f"Test data file '{filename}' already exists. Skipping creation.")


def download_file(url, progress_loader, success_count, error_count, max_retries=3):
    """Downloads a file with retry logic."""
    for attempt in range(max_retries):
        try:
            logging.debug(f"Attempting to download {url} (attempt {attempt + 1})")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            total_size = int(response.headers.get('content-length', 0))
            with open(os.path.join(test_data_dir, os.path.basename(url)), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            logging.info(f"Successfully downloaded file: {url}")
            success_count[0] += 1
            return
        except requests.exceptions.RequestException as e:
            logging.error(f"Download error for {url}: {e}")
            error_count[0] += 1
            if attempt == max_retries - 1:
                logging.error(f"Maximum retries exceeded for {url}. Giving up.")
                return
            time.sleep(1)  # Wait for a second before retrying


def process_data_item(row, loader, success_count, error_count):
    """Processes a data item from a CSV file."""
    try:
        # Process the data item here
        time.sleep(0.5)
        logging.info(f"Processed data item: {row}")
        success_count[0] += 1
    except Exception as e:
        logging.error(f"Error processing data item: {e}")
        error_count[0] += 1
    finally:
        loader.update()


def process_csv_data(filename):
    success_count = [0]
    error_count = [0]
    filepath = os.path.join(test_data_dir, filename)
    if not os.path.exists(filepath):
        logging.error(f"CSV file '{filename}' not found in '{test_data_dir}'.")
        return
    df = pd.read_csv(filepath)

    def custom_callback(progress_loader):
        for index, row in df.iterrows():
            process_data_item(row, progress_loader, success_count, error_count)
        logging.info(f"Processing completed with {success_count[0]} successes and {error_count[0]} errors.")

    with Throttle(total=len(df), desc="Processing CSV data", style="bar", color="blue", bar_length=10) as loader:
        custom_callback(loader)


@throttle_decorator(total=3, desc="Downloading files", style="bar", color="green", bar_length=10)
def download_multiple_files(urls, throttle_loader=None):
    for url in urls:
        # Simulate file download
        time.sleep(1)
        if throttle_loader:
            throttle_loader.update()
        print(f"Downloaded {url}")
    logging.info("Download tasks completed.")


def generate_thumbnails(image_urls, thumbnail_dir, width, height):
    """Generates thumbnails for a list of image URLs."""
    success_count = [0]
    error_count = [0]

    with Throttle(total=len(image_urls), desc="Generating Thumbnails", style="time_clock",
                  color="blue") as loader:
        for image_url in image_urls:
            try:
                # Download the image first
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


# Create test data
create_test_data("data.csv",
                 "col1,col2\n1,value1\n2,value2\n3,value3\n4,value4\n5,value5\n6,value6\n7,value7\n8,value8\n9,"
                 "value9\n10,value10")
download_urls = [
    "https://raw.githubusercontent.com/python/cpython/main/LICENSE",  # Text file
    "https://github.com/python/cpython/archive/refs/heads/main.zip",  # Zip file
    "https://www.python.org/doc/versions/3.10.0/whatsnew/3.10.0.html",  # PDF file
]

images_urls = [
    "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png",
]

if __name__ == "__main__":
    # Download multiple files using decorator
    download_multiple_files(download_urls)
    logging.info("Download tasks completed.")

    # Process CSV data with custom callback
    csv_filename = os.path.join(test_data_dir, "data.csv")
    process_csv_data(csv_filename)
    logging.info("CSV processing task completed.")

    # Generate thumbnails for images
    thumbnail_directory = os.path.join(test_data_dir, "thumbnails")
    os.makedirs(thumbnail_directory, exist_ok=True)
    generate_thumbnails(images_urls, thumbnail_directory, 100, 100)
    logging.info("Thumbnail generation task completed.")

    logging.info("All tasks completed.")
