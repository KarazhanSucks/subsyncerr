import sys
import os
import csv
import time
import subprocess
import requests
import json
import re
from datetime import datetime

API_KEY = os.getenv("API_KEY", "None")
BAZARR_URL = os.getenv("BAZARR_URL", "http://localhost:6767")
SUBCLEANER = os.getenv("SUBCLEANER", "false").lower() == "true"
SLEEP = os.getenv("SLEEP", "300")

print(f"API_KEY: {API_KEY}")
print(f"BAZARR_URL: {BAZARR_URL}")
print(f"SUBCLEANER: {SUBCLEANER}")
print(f"SLEEP: {SLEEP}\n")

def run_command(command, sub_file):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_output(sub_file, command, output.decode('utf-8'), timestamp)
    return output.decode('utf-8'), error.decode('utf-8')

def log_output(sub_file, command, output, timestamp):
    if 'subcleaner' in command:
        log_folder = '/subaligner-bazarr/logs/subcleaner'
    elif 'subaligner' in command:
        log_folder = '/subaligner-bazarr/logs/subaligner'
    elif 'subsync' in command:
        log_folder = '/subaligner-bazarr/logs/subsync'
    else:
        log_folder = '/subaligner-bazarr/logs'
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    os.makedirs(log_folder, exist_ok=True)
    cleaned_sub_file = re.sub(r'[\\/*?:"<>|]', " - ", sub_file)
    filename = f"{timestamp}{cleaned_sub_file}.log"
    log_path = os.path.join(log_folder, filename)
    
    with open(log_path, 'w') as log_file:
        log_file.write(f"Command: {command}\n\n")
        log_file.write("Output:\n")
        log_file.write(output)
        
    time.sleep(0.1)

def replace_language_code(file_path):
    base, ext = os.path.splitext(file_path)
    new_base = re.sub(r'\.([a-z]{2})(\.(hi|cc|sdh))?$', '', base)
    
    en_path = f"{new_base}.en{ext}"
    en_hi_path = f"{new_base}.en.hi{ext}"
    en_cc_path = f"{new_base}.en.cc{ext}"
    en_sdh_path = f"{new_base}.en.sdh{ext}"
    
    if os.path.exists(en_path):
        return en_path
    elif os.path.exists(en_hi_path):
        return en_hi_path
    elif os.path.exists(en_cc_path):
        return en_cc_path
    elif os.path.exists(en_sdh_path):
        return en_sdh_path
    else:
        return None
    
def extract_filename(sub_file):
    # Extract just the filename without path and extension
    filename = os.path.basename(sub_file)
    filename = os.path.splitext(filename)[0]
    
    # Remove .hi, .cc, or .sdh if present
    filename = re.sub(r'\.([a-z]{2})(\.(hi|cc|sdh))?$', '', filename)
    
    return filename
    
def create_csv_file(csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])
    
    os.chmod(csv_file, 0o666)
    
def create_error_file(error_file):
    os.makedirs(os.path.dirname(error_file), exist_ok=True)
    with open(error_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])

def has_error(output, sub_file):
    # Extract the filename
    filename = extract_filename(sub_file)
    
    # Remove the filename from the output
    cleaned_output = output.replace(sub_file, '').replace(filename, '')
    
    #Check for "Error" or "ERROR" in the cleaned output
    return "Error" in cleaned_output or "ERROR" in cleaned_output

def add_to_error_list(error_file, reference_file, sub_file, sub_code2, sub_code3, sub_id, provider, series_id, episode_id):
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
        # Check if failed.csv exists, if not create it with headers
        if not os.path.isfile(error_file):
            with open(error_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])

        # Append the new data to the CSV file
        with open(error_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
            
        time.sleep(0.1)
    except Exception as e:
        print("ERROR: Something went wrong...")
        print(f"\u2022Error: {str(e)}")

def blacklist_subtitle(is_movie, series_id, episode_id, provider, sub_id, sub_code2, sub_file):
    if is_movie:
        url = f"{BAZARR_URL}/api/movies/blacklist?radarrid={episode_id}"
    else:
        url = f"{BAZARR_URL}/api/episodes/blacklist?seriesid={series_id}&episodeid={episode_id}"
    
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        time.sleep(0.1)
        return True
    except requests.RequestException as e:
        print(f"\u2022API-request failed: {str(e)}")
        return False

def download_new_subtitle(is_movie, series_id, episode_id, sub_code2):
    if is_movie:
        url = f"{BAZARR_URL}/api/movies/subtitles?radarrid={episode_id}"
    else:
        url = f"{BAZARR_URL}/api/episodes/subtitles?seriesid={series_id}&episodeid={episode_id}"
    
    payload = {
        "language": sub_code2,
        "forced": False,
        "hi": False
    }
    
    headers = {
        "X-API-KEY": f"{API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        time.sleep(2)
        return True
    except requests.RequestException as e:
        print(f"\u2022API-request failed: {str(e)}")
        return False
    
def process_non_english_counterpart(csv_file, english_sub_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        subtitles = list(reader)
        
    for subtitle in subtitles[1:]:
        if subtitle[1] == english_sub_file:
            non_english_subs = [sub for sub in subtitles[1:] if sub[1] == subtitle[1] and sub[2] != english_sub_file]
            for non_english_sub in non_english_subs:
                add_to_error_list(error_file, *non_english_sub[1:9])
                remove_from_list(csv_file, non_english_sub[2])

def remove_from_list(csv_file, sub_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        subtitles = list(reader)
    
    header = subtitles[0]
    original_count = len(subtitles)
    subtitles = [sub for sub in subtitles[1:] if sub[2] != sub_file]
    new_count = len(subtitles) + 1  # +1 for the header

    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(subtitles)
        
    time.sleep(0.5)
    
def process_subtitles(csv_file, error_file):
    processed_count = 0 
    
    while True:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read and skip the header row
            subtitles = list(reader)
            
        if not subtitles:
            with open(error_file, 'r') as file:
                reader = csv.reader(file)
                next(reader) # Skip header
                error_list = list(reader)
                
            for subtitle in error_list:
                current_count = len(error_list)
                processed_count += 1
                print(f"Processed: {processed_count}, Remaining: {current_count}")
                time.sleep(0.1)
                print(f"Processing subtitle: {subtitle[2]}")
                time.sleep(0.1)
                
                if subtitle[3] == 'en': # Check if it's an English subtitle
                    if blacklist_subtitle(subtitle[7] == "", subtitle[7], subtitle[8], subtitle[6], subtitle[5], subtitle[3], subtitle[2]):
                        print("Successfully blacklisted subtitle, requesting new subtitle!")
                        new_subtitle = download_new_subtitle(subtitle[7] == "", subtitle[7], subtitle[8], subtitle[3])
                        if new_subtitle:
                            print("Successfully downloaded new subtitle, adding to list!")
                            error_list.remove(subtitle)
                            non_english_subs = [sub for sub in error_list if sub[1] == subtitle[1] and sub[3] != 'en']
                            for non_english_sub in non_english_subs:
                                error_list.remove(non_english_sub)
                                print("Moving non-English subtitle entry back to unsynced.csv!")
                                with open(csv_file, 'a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow(non_english_sub)
                            print()
                        else:
                            print("No new subtitles found, removing from logs/failed.csv...")
                            error_list.remove(subtitle)
                            non_english_subs = [sub for sub in error_list if sub[1] == subtitle[1] and sub[3] != 'en']
                            for non_english_sub in non_english_subs:
                                error_list.remove(non_english_sub)
                                print("Moving non-English subtitle entry back to unsynced.csv!")
                                with open(csv_file, 'a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow(non_english_sub)
                            print()
                    else:
                        print("ERROR: Failed to blacklist subtitle, keeping in logs/failed.csv...\n")
                else:
                    print("Non-English subtitle, skipping!\n")
                    time.sleep(0.5)
                    
                time.sleep(0.1)
                                    
                # Write back the updated error list
                with open(error_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])
                    writer.writerows(error_list)
            
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)  # Read and skip the header row
                subtitles = list(reader)
                
            if not subtitles:
                break
            
        current_count = len(subtitles)
        
        subtitle = subtitles[0]  # Get and remove the first subtitle
        reference_file, sub_file, sub_code2, sub_code3, sub_id, provider, series_id, episode_id = subtitle[1:9]
        is_movie = series_id == ""  # Assume it's a movie if series_id is ""
        
        english_sub_path = replace_language_code(sub_file)
        english_subtitle = next((sub for sub in subtitles if sub[2] == english_sub_path), None)
        
        processed_count += 1
        print(f"Processed: {processed_count}, Remaining: {current_count}")
        time.sleep(0.1)

        if sub_code2 != 'en':
            # This is a non-English subtitle
            if english_subtitle:
                process_subtitle(english_subtitle[7] == "", english_subtitle[1:9], csv_file)
            elif english_sub_path:
                sync_to_english(subtitle[1:9], english_sub_path, csv_file)
            else:
                print("No English subtitle found. Processing with subaligner...")
                process_subtitle(is_movie, subtitle[1:9], csv_file)
        else:
            # This is an English subtitle
            process_subtitle(is_movie, subtitle[1:9], csv_file)

        time.sleep(0.1)  # Add a small delay between processing subtitles

def process_subtitle(is_movie, subtitle, csv_file):
    reference_file, sub_file, sub_code2, sub_code3, sub_id, provider, series_id, episode_id = subtitle
    
    print(f"Processing subtitle: {sub_file}")
    time.sleep(0.1)

    if SUBCLEANER:
        print("Running subcleaner...")
        subcleaner_command = f"/usr/bin/python3 /opt/subcleaner/subcleaner.py \"{sub_file}\""
        run_command(subcleaner_command, sub_file)

    print("Running subaligner...")
    if sub_code2 == "en":
        subaligner_command = f"/usr/local/bin/subaligner -m dual -v \"{reference_file}\" -s \"{sub_file}\" -o \"{sub_file}\" -so -mpt 1250"
    else:
        subaligner_command = f"/usr/local/bin/subaligner -m dual -v \"{reference_file}\" -s \"{sub_file}\" -o \"{sub_file}\" -so -mpt 1250 -sil \"{sub_code3}\""

    output, error = run_command(subaligner_command, sub_file)
    
    if has_error(output + error, sub_file):
        print("ERROR: Something went wrong...")
        if blacklist_subtitle(is_movie, series_id, episode_id, provider, sub_id, sub_code2, sub_file):
            print("Successfully blacklisted subtitle, requesting new subtitle!")
            remove_from_list(csv_file, sub_file)
            new_subtitle = download_new_subtitle(is_movie, series_id, episode_id, sub_code2)
            if new_subtitle:
                print("Successfully downloaded new subtitle, adding to list!\n")           
            else:
                print("No new subtitles found, removing from list...")
                add_to_error_list(error_file, reference_file, sub_file, sub_code2, sub_code3, sub_id, provider, series_id, episode_id)
                remove_from_list(csv_file, sub_file)
                print("Moving subtitle entry to logs/failed.csv!")
                if sub_code2 == 'en':
                    process_non_english_counterpart(csv_file, reference_file)
                    print("Moving non-English subtitle entry to logs/failed.csv!\n")
                else:
                    print()
        else:
            print("ERROR: Failed to blacklist subtitle...")
            add_to_error_list(error_file, reference_file, sub_file, sub_code2, sub_code3, sub_id, provider, series_id, episode_id)
            remove_from_list(csv_file, sub_file)
            print("Moving subtitle entry to logs/failed.csv!")
            if sub_code2 == 'en':
                process_non_english_counterpart(csv_file, reference_file)
                print("Moving non-English subtitle entry to logs/failed.csv!\n")
            else:
                print()
            
    else:
        print("Successfully synced subtitle, removing from list!\n")
        remove_from_list(csv_file, sub_file)

def sync_to_english(subtitle, english_sub_path, csv_file):
    sub_file, sub_code3 = subtitle[1], subtitle[3]
    
    print(f"Processing non-English subtitle: {sub_file}")
    
    if SUBCLEANER:
        print("Running subcleaner...")
        subcleaner_command = f"/usr/bin/python3 /opt/subcleaner/subcleaner.py \"{sub_file}\""
        run_command(subcleaner_command, sub_file)

    print("Running subsync...")
    subsync_command = f"/usr/local/bin/subsync --cli sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{english_sub_path}\" --ref-lang \"eng\" --ref-stream-by-type \"sub\" --out \"{sub_file}\" --window-size 100 --overwrite"
    run_command(subsync_command, sub_file)
    
    print("Successfully synced non-English subtitle, removing from list!\n")
    remove_from_list(csv_file, sub_file)

if __name__ == "__main__":
    csv_file = '/subaligner-bazarr/unsynced.csv'
    error_file = '/subaligner-bazarr/logs/failed.csv'
    
    # Check if unsynced.csv exists, if not create it with headers
    if not os.path.isfile(csv_file):
        create_csv_file(csv_file)
        
    # Check if failed.csv exists, if not create it with headers
    if not os.path.isfile(error_file):
        create_error_file(error_file)
        
    while True:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"{timestamp}: Checking for subtitles...")
        time.sleep(0.1)
        
        process_subtitles(csv_file, error_file)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"{timestamp}: List is clear!!!\n")
        time.sleep(float(SLEEP))