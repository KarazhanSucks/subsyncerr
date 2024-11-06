import os
import csv
import time
import subprocess
import shutil
import requests
import re
from datetime import datetime

os.environ["PYTHONUNBUFFERED"] = "1"

API_KEY = os.getenv("API_KEY", "None")
BAZARR_URL = os.getenv("BAZARR_URL", "http://localhost:6767")
SUBCLEANER = os.getenv("SUBCLEANER", "false").lower() == "true"
SLEEP = os.getenv("SLEEP", "300")
WINDOW_SIZE = os.getenv("WINDOW_SIZE", "1800")

def run_command(command, sub_file, log_command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    raw_output, raw_error = process.communicate()
    
    output = raw_output.decode('utf-8')
    error = raw_error.decode('utf-8')
    
    filename = extract_filename(sub_file)
    
    # Remove the filename from the output
    cleaned_output = output.replace(sub_file, '').replace(filename, '')
    output = output.replace("/dev/shm/tmp.srt", sub_file)
    
    if "can't open multimedia file: No such file or directory" in cleaned_output:
        return output, error, 'extension'
    
    if "Select reference language first" in cleaned_output:
        return output, error, True
    
    log_output(sub_file, log_command, output)
    return output, error, False

def log_output(sub_file, command, output):
    if 'subsync' in command:
        log_folder = '/subsync-bazarr/logs/subsync'
    elif 'subcleaner' in command:
        log_folder = '/subsync-bazarr/logs/subcleaner'
    else:
        log_folder = '/subsync-bazarr/logs'
        
    timestamp = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        
    os.makedirs(log_folder, exist_ok=True)
    cleaned_sub_file = re.sub(r'[\\/*?:"<>|]', " - ", sub_file)
    filename = f"{timestamp}{cleaned_sub_file}.log"
    log_path = os.path.join(log_folder, filename)
    
    with open(log_path, 'w', encoding="utf-8") as log_file:
        log_file.write(f"Command: {command}\n\n")
        log_file.write("Output:\n")
        log_file.write(output)
        
    time.sleep(0.1)
    
def srt_lang_detect(command, sub_file):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    raw_output = process.communicate()
    output = raw_output[0].decode('utf-8')
    
    filename = extract_filename(sub_file)
    
    # Remove the filename from the output
    cleaned_output = output.replace(sub_file, '').replace(filename, '')
    
    if "Would rename" in cleaned_output:
        return False
    else:
        return True

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
        writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'episode_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])
    
def create_retry_file(retry_file):
    os.makedirs(os.path.dirname(retry_file), exist_ok=True)
    with open(retry_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'episode_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])

def has_error(output, sub_file):
    # Extract the filename
    filename = extract_filename(sub_file)
    
    # Remove the filename from the output
    cleaned_output = output.replace(sub_file, '').replace(filename, '')
    
    if "couldn't synchronize!" in cleaned_output:
        if "progress 100%, 0 points" in cleaned_output:
            return 'nosync'
        return True
    elif "recognition model is missing" in cleaned_output:
        return 'nosync'
    else:
        return None
    
def add_to_failed_list(sub_file):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = f"{timestamp}: {sub_file}\n"

    try:
        with open(failed_file, 'a', encoding='utf-8') as f:
            f.write(data)
            
        time.sleep(0.1)
    except Exception as e:
        print("ERROR: Something went wrong...")
        print(f"\u2022Error: {str(e)}")
    
def add_to_csv_list(csv_file, reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id):
    data = [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        reference_file,
        sub_file,
        sub_code2,
        sub_code3,
        ep_code3,
        sub_id,
        provider,
        series_id,
        episode_id
    ]

    try:
        if not os.path.isfile(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'episode_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])

        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
            
        time.sleep(0.1)
    except Exception as e:
        print("ERROR: Something went wrong...")
        print(f"\u2022Error: {str(e)}")

def add_to_retry_list(retry_file, reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id):
    # Prepare the data to be written
    data = [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        reference_file,
        sub_file,
        sub_code2,
        sub_code3,
        ep_code3,
        sub_id,
        provider,
        series_id,
        episode_id
    ]

    try:
        # Check if retry.csv exists, if not create it with headers
        if not os.path.isfile(retry_file):
            with open(retry_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'episode', 'subtitles', 'subtitle_language_code2', 'subtitle_language_code3', 'episode_language_code3', 'subtitle_id', 'provider', 'series_id', 'episode_id'])

        # Append the new data to the CSV file
        with open(retry_file, 'a', newline='', encoding='utf-8') as f:
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
        if response.status_code in [404, 500]:
            return 'remove'
        if response.status_code not in [204]:
            response.raise_for_status()
            
        time.sleep(2)
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
        if response.status_code not in [200]:
            response.raise_for_status()
            
        time.sleep(2)
        return True
    except requests.RequestException as e:
        print(f"\u2022API-request failed: {str(e)}")
        return False
                
def find_non_english_counterpart(csv_file, reference_file, sub_file, move_to_failed):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        subtitles = list(reader)
        
    for subtitle in subtitles[1:]:
        if subtitle[1] == reference_file:
            while True:
                non_english_subs = [sub for sub in subtitles[1:] if sub[1] == subtitle[1] and sub[2] != sub_file]
                
                if not non_english_subs:
                    break
                
                for non_english_sub in non_english_subs:
                    remove_from_list(csv_file, non_english_sub[2])
                    
                    if move_to_failed:
                        add_to_failed_list(non_english_sub[2])
                        time.sleep(0.5)
                    
                        print(f"Removed \"{non_english_sub[3]}\"-subtitle from list and added it to failed.txt!")
                    
                    elif move_to_failed == 'retry':
                        add_to_retry_list(retry_file, *non_english_sub[1:10])
                        print(f"Moved \"{non_english_sub[3]}\"-subtitle entry to logs/retry.csv!")
                    else:
                        add_to_csv_list(csv_file, *non_english_sub[1:10])
                        
                    subtitles.remove(non_english_sub)
                    
    if move_to_failed:
        data = "\n"
        try:
            with open(failed_file, 'a', encoding='utf-8') as f:
                f.write(data)
                
            time.sleep(0.1)
        except Exception as e:
            print("ERROR: Something went wrong...")
            print(f"\u2022Error: {str(e)}")
        time.sleep(0.5)

def remove_from_list(csv_file, sub_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        subtitles = list(reader)
    
    header = subtitles[0]
    subtitles = [sub for sub in subtitles[1:] if sub[2] != sub_file]

    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(subtitles)
        
    time.sleep(0.5)
    
def remove_from_retry_list(retry_file, sub_file):
    with open(retry_file, 'r') as file:
        reader = csv.reader(file)
        retry_list = list(reader)
        
    header = retry_list[0]
    retry_list = [sub for sub in retry_list[1:] if sub[2] != sub_file[2]]

    # Write back the updated error list
    with open(retry_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(retry_list)
        
    time.sleep(0.5)
    
def process_subtitles(csv_file, retry_file):
    processed_count = 0 
    
    while True:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader) # Skip header
            subtitles = list(reader)
            
        if not subtitles:  
            while True:  
                with open(retry_file, 'r') as file:
                    reader = csv.reader(file)
                    next(reader) # Skip header
                    retry_list = list(reader)
                    
                if not retry_list:
                    break
                
                print()
                
                subtitle = retry_list[0]  # Get and remove the first subtitle
                             
                current_count = len(retry_list)
                processed_count += 1
                
                english_sub_path = replace_language_code(subtitle[2])
                english_subtitle = next((sub for sub in retry_list if sub[2] == english_sub_path), None)
                
                if subtitle[3] != 'en':
                    # This is a non-English subtitle
                    if english_subtitle:
                         subtitle[1:10] = english_subtitle[1:10]
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] Processed: {processed_count}, Remaining: {current_count}")
                time.sleep(0.1)
                print(f"Processing subtitle: {subtitle[2]}")
                time.sleep(0.1)
                
                blacklist_result = blacklist_subtitle(subtitle[8] == "", subtitle[8], subtitle[9], subtitle[7], subtitle[6], subtitle[3], subtitle[2])
                if blacklist_result == True:
                    print("Successfully blacklisted subtitle, requesting new subtitle!")
                    new_subtitle = download_new_subtitle(subtitle[8] == "", subtitle[8], subtitle[9], subtitle[3])
                    if new_subtitle:
                        remove_from_retry_list(retry_file, subtitle)
                        non_english_subs = [sub for sub in retry_list if sub[1] == subtitle[1] and sub[3] != 'en']
                        for non_english_sub in non_english_subs:
                            remove_from_retry_list(retry_file, non_english_sub)
                            print(f"Moving \"{non_english_sub[3]}\"-subtitle entry back to unsynced.csv!")
                            with open(csv_file, 'a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(non_english_sub)
                        print()
                    else:
                        print("No new subtitles found, removing from logs/retry.csv...")
                        remove_from_retry_list(retry_file, subtitle)
                        non_english_subs = [sub for sub in retry_list if sub[1] == subtitle[1] and sub[3] != 'en']
                        for non_english_sub in non_english_subs:
                            remove_from_retry_list(retry_file, non_english_sub)
                            print(f"Moving \"{non_english_sub[3]}\"-subtitle entry back to unsynced.csv!")
                            with open(csv_file, 'a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(non_english_sub)
                        print()
                        
                elif blacklist_result == 'remove':
                    print("Subtitle not found, removing from logs/retry.csv...")
                    remove_from_retry_list(retry_file, subtitle)
                    non_english_subs = [sub for sub in retry_list if sub[1] == subtitle[1] and sub[3] != 'en']
                    for non_english_sub in non_english_subs:
                        remove_from_retry_list(retry_file, non_english_sub)
                        print(f"Removing \"{non_english_sub[3]}\"-subtitle from logs/retry.csv...")
                    print()
                else:
                    print("ERROR: Failed to blacklist subtitle, keeping in logs/retry.csv...\n")
                    
                time.sleep(0.1)
            
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)  # Read and skip the header row
                subtitles = list(reader)
                
            if not subtitles:
                break
        print()    
        
        current_count = len(subtitles)
        
        subtitle = subtitles[0]  # Get and remove the first subtitle
        reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id = subtitle[1:10]
        is_movie = series_id == ""  # Assume it's a movie if series_id is ""
        
        english_sub_path = replace_language_code(sub_file)
        english_subtitle = next((sub for sub in subtitles if sub[2] == english_sub_path), None)
        
        processed_count += 1
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] Processed: {processed_count}, Remaining: {current_count}")
        time.sleep(0.1)

        if sub_code2 != 'en':
            # This is a non-English subtitle
            if english_subtitle:
                process_subtitle(english_subtitle[8] == "", english_subtitle[1:10], csv_file, None)
            elif english_sub_path:
                process_subtitle(is_movie, subtitle[1:10], csv_file, english_sub_path)
            else:
                print("No English subtitle found. Processing with subsync...")
                process_subtitle(is_movie, subtitle[1:10], csv_file, None)
        else:
            # This is an English subtitle
            process_subtitle(is_movie, subtitle[1:10], csv_file, None)

        time.sleep(0.1)  # Add a small delay between processing subtitles

def process_subtitle(is_movie, subtitle, csv_file, english_sub_path):
    reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id = subtitle
    
    if sub_code2 != 'en':
        print(f"Processing non-English subtitle: {sub_file}") 
    else:
        print(f"Processing subtitle: {sub_file}")
    time.sleep(0.1)
    
    if not os.path.isfile(sub_file):
        print("Subtitle not found in path, removing from list!\n")
        remove_from_list(csv_file, sub_file)
        time.sleep(1)
    else:
        lang_command = f"/usr/bin/python3 -u /opt/srt-lang-detect/srtlangdetect.py \"{sub_file}\""
        if srt_lang_detect(lang_command, sub_file):
            if SUBCLEANER:
                print("Running subcleaner...")
                subcleaner_command = f"/usr/bin/python3 -u /opt/subcleaner/subcleaner.py --language \"{sub_code2}\" \"{sub_file}\""
                run_command(subcleaner_command, sub_file, subcleaner_command)
            
            if not english_sub_path:
                print("Running subsync...")
    
                subsync_command = f"/usr/bin/python3 -u /usr/local/bin/subsync --cli --window-size \"{float(WINDOW_SIZE)}\" sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{reference_file}\" --ref-stream-by-type \"audio\" --out \"/dev/shm/tmp.srt\" --overwrite"
                log_command = f"/usr/bin/python3 -u /usr/local/bin/subsync --cli --window-size \"{float(WINDOW_SIZE)}\" sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{reference_file}\" --ref-stream-by-type \"audio\" --out \"{sub_file}\" --overwrite"
                output, error, fail = run_command(subsync_command, sub_file, log_command)
            
                if fail == True:
                    print(f"Audio track language unknown, trying again with \"{ep_code3}\" as reference language...")
                    time.sleep(0.1)
                        
                    subsync_command = f"/usr/bin/python3 -u /usr/local/bin/subsync --cli --window-size \"{float(WINDOW_SIZE)}\" sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{reference_file}\" --ref-stream-by-type \"audio\" --ref-lang \"{ep_code3}\" --out \"/dev/shm/tmp.srt\" --overwrite"
                    log_command = f"/usr/bin/python3 -u /usr/local/bin/subsync --cli --window-size \"{float(WINDOW_SIZE)}\" sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{reference_file}\" --ref-stream-by-type \"audio\" --ref-lang \"{ep_code3}\" --out \"{sub_file}\" --overwrite"
                    output, error, fail = run_command(subsync_command, sub_file, log_command)    
                if fail == 'extension':
                    print("ERROR: Can't open multimedia file: No such file or directory, moving to failed.txt...")
                
                    add_to_failed_list(sub_file)
                    remove_from_list(csv_file, sub_file)
                    find_non_english_counterpart(csv_file, reference_file, sub_file, True)
                    print("Moved successfully, proceeding!!!\n")
                    
                    return False        
            else:
                print("Running subsync for non-English subtitle...")
                
                subsync_command = f"/usr/bin/python3 -u /usr/local/bin/subsync --cli --window-size \"300\" sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{english_sub_path}\" --ref-stream-by-type \"sub\" --ref-lang \"eng\" --out \"/dev/shm/tmp.srt\" --overwrite"
                log_command = f"/usr/bin/python3 -u /usr/local/bin/subsync --cli --window-size \"300\" sync --sub \"{sub_file}\" --sub-lang \"{sub_code3}\" --ref \"{english_sub_path}\" --ref-stream-by-type \"sub\" --ref-lang \"eng\" --out \"{sub_file}\" --overwrite"
                output, error, fail = run_command(subsync_command, sub_file, log_command)
                
            if has_error(output + error, sub_file) == True:
                print("ERROR: Something went wrong...")
                blacklist_result = blacklist_subtitle(is_movie, series_id, episode_id, provider, sub_id, sub_code2, sub_file)
                if blacklist_result == True:
                    print("Successfully blacklisted subtitle, requesting new subtitle!")
                    remove_from_list(csv_file, sub_file)
                    new_subtitle = download_new_subtitle(is_movie, series_id, episode_id, sub_code2)
                    if new_subtitle:
                        print()
                        
                        find_non_english_counterpart(csv_file, reference_file, sub_file, False)
                                
                    else:
                        print("No new subtitles found, removing from list...")
                        add_to_retry_list(retry_file, reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id)
                        remove_from_list(csv_file, sub_file)
                        print("Moving subtitle entry to logs/retry.csv!")
                        if sub_code2 == 'en':
                            find_non_english_counterpart(csv_file, reference_file, sub_file, 'retry')
                            print()
                        else:
                            print()
                elif blacklist_result == 'remove':
                    print("Subtitle not found, removing from list...\n")
                    remove_from_list(csv_file, sub_file)
                else:
                    print("ERROR: Failed to blacklist subtitle...")
                    add_to_retry_list(retry_file, reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id)
                    remove_from_list(csv_file, sub_file)
                    
                    print("Moving subtitle entry to logs/retry.csv!")
                    
                    if sub_code2 == 'en':
                        find_non_english_counterpart(csv_file, reference_file, sub_file, 'retry')
                    print()
                        
            elif has_error(output + error, sub_file) == 'nosync':
                print("Couldn't synchronize to media file...")
                
                add_to_failed_list(sub_file)
                remove_from_list(csv_file, sub_file)
                
                if sub_code2 == 'en':
                    print("Removed English subtitle from list and added it to failed.txt!")
                else:
                    print(f"Removed \"{sub_code2}\"-subtitle from list and added it to failed.txt!")
                
                find_non_english_counterpart(csv_file, reference_file, sub_file, True)
                print()

            else:
                try:
                    shutil.copy2('/dev/shm/tmp.srt', sub_file)
                    if sub_code2 == 'en':
                        print("Successfully synced English subtitle, removing from list!\n")
                    else:
                        print(f"Successfully synced \"{sub_code2}\"-subtitle, removing from list!\n")
                        
                    remove_from_list(csv_file, sub_file)
                except Exception as e:
                    print("ERROR: Something went wrong...")
                    print(f"\u2022Error: {str(e)}")
                    if sub_code2 == 'en':
                        remove_from_list(csv_file, sub_file)
                        add_to_csv_list(csv_file, subtitle[1:10])
                    else:
                        find_non_english_counterpart(csv_file, reference_file, sub_file, False)                 
        else:
            print("ERROR: Wrong language detected in subtitle...")
            blacklist_result = blacklist_subtitle(is_movie, series_id, episode_id, provider, sub_id, sub_code2, sub_file)
            if blacklist_result == True:
                print("Successfully blacklisted subtitle, requesting new subtitle!")
                remove_from_list(csv_file, sub_file)
                new_subtitle = download_new_subtitle(is_movie, series_id, episode_id, sub_code2)
                if new_subtitle:
                    print()
                    
                    find_non_english_counterpart(csv_file, reference_file, sub_file, False)
                            
                else:
                    print("No new subtitles found, removing from list...")
                    add_to_retry_list(retry_file, reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id)
                    remove_from_list(csv_file, sub_file)
                    print("Moving subtitle entry to logs/retry.csv!")
                    if sub_code2 == 'en':
                        find_non_english_counterpart(csv_file, reference_file, sub_file, 'retry')
                        print()
                    else:
                        print()
            elif blacklist_result == 'remove':
                print("Subtitle not found, removing from list...\n")
                remove_from_list(csv_file, sub_file)
            else:
                print("ERROR: Failed to blacklist subtitle...")
                add_to_retry_list(retry_file, reference_file, sub_file, sub_code2, sub_code3, ep_code3, sub_id, provider, series_id, episode_id)
                remove_from_list(csv_file, sub_file)
                
                print("Moving subtitle entry to logs/retry.csv!")
                
                if sub_code2 == 'en':
                    find_non_english_counterpart(csv_file, reference_file, sub_file, 'retry')
                print()
                
if __name__ == "__main__":
    csv_file = '/subsync-bazarr/unsynced.csv'
    retry_file = '/subsync-bazarr/logs/retry.csv'
    failed_file = '/subsync-bazarr/failed.txt'
    
    # Check if unsynced.csv exists, if not create it with headers
    if not os.path.isfile(csv_file):
        create_csv_file(csv_file)
        
    # Check if retry.csv exists, if not create it with headers
    if not os.path.isfile(retry_file):
        create_retry_file(retry_file)
        
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp}: Checking for subtitles...")
        time.sleep(0.1)
        
        process_subtitles(csv_file, retry_file)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp}: List is clear, checking again in {SLEEP} seconds!\n")
        time.sleep(float(SLEEP))