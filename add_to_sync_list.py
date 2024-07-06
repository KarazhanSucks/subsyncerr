import csv
import os
import sys
import time
from datetime import datetime
import re
import requests

# Define the output file path
csv_file = '/scripts/unsynced.csv'

# API key
API_KEY = 'a2fe6181cefc9e93214a6b84ce8ec736'
API_BASE_URL = "http://localhost:6767/api"

# Get the variables from command-line arguments
reference_file, sub_file, sub_code2, sub_code3, sub_id, provider, series_id, episode_id = sys.argv[1:]

# Function to check subtitle filename
def check_subtitle_filename(filename):
    pattern = r'(hi|sdh|cc)\.[^.]+$'
    return re.search(pattern, filename.lower()) is not None

# Function to blacklist subtitle
def blacklist_subtitle(is_movie):
    if is_movie:
        url = f"{API_BASE_URL}/movies/blacklist?radarrid={episode_id}"
    else:
        url = f"{API_BASE_URL}/episodes/blacklist?seriesid={series_id}&episodeid={episode_id}"
    
    headers = {
        "X-API-KEY": f"{API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "provider": provider,
        "subs_id": sub_id,
        "language": sub_code2,
        "subtitles_path": sub_file
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        time.sleep(1)
        return True
    except requests.RequestException as e:
        print(f"\u2022API request failed: {str(e)}")
        return False

# Function to download new subtitle
def download_new_subtitle(is_movie):
    if is_movie:
        url = f"{API_BASE_URL}/movies/subtitles?radarrid={episode_id}"
    else:
        url = f"{API_BASE_URL}/episodes/subtitles?seriesid={series_id}&episodeid={episode_id}"
    
    headers = {
        "X-API-KEY": f"{API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "language": sub_code2,
        "forced": False,
        "hi": False
    }
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        time.sleep(1)
        return True
    except requests.RequestException as e:
        print(f"\u2022API request failed: {str(e)}")
        return False

# Check if the subtitle should be blacklisted
if check_subtitle_filename(sub_file):
    # Determine if it's a movie based on whether series_id is an empty string
    is_movie = series_id == ""

    if blacklist_subtitle(is_movie):
        print("Successfully blacklisted subtitle")
        # Attempt to download a new subtitle
        if download_new_subtitle(is_movie):
            print("& requested a new subtitle!")
        else:
            print("BUT failed to request a new subtitle...")
    else:
        print(f"Failed to blacklist subtitle: {sub_file}")
else:
    # Prepare the data to be written
    data = [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        reference_file,
        sub_file,
        sub_code2,
        sub_code3,
        sub_id,
        provider,
        series_id,
        episode_id
    ]

    try:
        # Check if the file exists, if not create it with headers
        if not os.path.isfile(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])

        # Append the new data to the CSV file
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
            
        print(f"Successfully added to list!")    
        time.sleep(2)
    except Exception as e:
        print("Something went wrong...")
        print(f"Error: {str(e)}")