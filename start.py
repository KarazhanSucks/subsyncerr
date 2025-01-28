import os
import shutil
import subprocess
import time
import requests
import importlib.util

os.environ["PYTHONUNBUFFERED"] = "1"

HOST_SCRIPTS_DIR = "/subsyncerr"
CONTAINER_SCRIPTS_DIR = "/opt/subsyncerr"
FILE = "addtosynclist.bash"

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Import variables from main.py
spec = importlib.util.spec_from_file_location("main", os.path.join(CONTAINER_SCRIPTS_DIR, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

print("Welcome to Tarzoq's \"subsyncerr\", please check out the repository on GitHub if you encounter any issues: https://github.com/Tarzoq/subsyncerr\n")

time.sleep(1)

print(f"API_KEY: {main.API_KEY}")
print(f"BAZARR_URL: {main.BAZARR_URL}")
print(f"SLEEP: {main.SLEEP}")
print(f"SUBCLEANER: {main.SUBCLEANER}")
print(f"WINDOW_SIZE: {main.WINDOW_SIZE}\n")

time.sleep(1)

print("REMINDER: CPU-pinning for this container is highly recommended, subsync WILL hog all resources it can get!\n")

def bazarr_status(max_retries=5, delay=10):
    url = f"{main.BAZARR_URL}/api/system/status"
    
    headers = {
        "X-API-KEY": f"{main.API_KEY}",
        "Content-Type": "application/json"
        }
    
    print("Attempting connection to Bazarr API...")
    time.sleep(1)
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            time.sleep(0.1)
            return True     
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1: # If it's not the last attempt
                print(f"Retrying in {delay} seconds...\n")
                time.sleep(delay)
            else:
                print("\nAll attempts failed...\n")
                return False
        
    return False

def list_metadata(is_movie):
    iterations = 8
    
    if is_movie:
        url = f"{main.BAZARR_URL}/api/movies?start=0&length={iterations}"
    else:
        url = f"{main.BAZARR_URL}/api/series?start=0&length={iterations}"
    
    headers = {
        "X-API-KEY": f"{main.API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code not in [200]:
            response.raise_for_status()
            
        time.sleep(1)
            
        response_body = response.json()
        paths = [item["path"] for item in response_body["data"]]
        
        for path in paths:  # paths is whatever length the iterations-variable for the length from the bazarr-api is
            if os.path.exists(path):
                break
            
        if (not os.path.exists(path)) or (not os.access(path, os.R_OK)) or (not os.access(path, os.W_OK)):
            return False
        
        if is_movie:
            if not list_metadata(False):
                return False
            
        return True
    except requests.RequestException as e:
        print(f"\u2022ERROR, API-request failed: {str(e)}")
        return False
    
def bazarr_path():
    url = f"{main.BAZARR_URL}/api/files?path=%2Fsubsyncerr"
    
    headers = {
        "X-API-KEY": f"{main.API_KEY}",
        "Content-Type": "application/json"
    }
    
    if os.path.isdir(HOST_SCRIPTS_DIR):
        os.makedirs(os.path.join(HOST_SCRIPTS_DIR, 'logs'), exist_ok=True)
    else:
        return False
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code not in [200]:
            response.raise_for_status()
            
        time.sleep(1)
            
        response_body = response.json()
            
        if response_body == []:
            return False
            
        return True
    except requests.RequestException as e:
        print(f"\u2022ERROR, API-request failed: {str(e)}")
        return False
    
if DEBUG:
    while True:
        print("Debug environment-variable detected, not running main.py!")
        time.sleep(1800)
        print()

if bazarr_path():
    if bazarr_status():
        print("Bazarr connection successful!!!")
        time.sleep(0.1)
        if list_metadata(True):
            print("The allocated TV and Movie paths along with their required permissions successfully verified!!!")
            time.sleep(0.1)
            if os.path.isfile(os.path.join(CONTAINER_SCRIPTS_DIR, FILE)):
                shutil.copy2(os.path.join(CONTAINER_SCRIPTS_DIR, FILE), HOST_SCRIPTS_DIR)
                os.chmod(os.path.join(HOST_SCRIPTS_DIR, FILE), 0o755)  # This is equivalent to chmod +x
                
                if os.path.isfile(os.path.join(HOST_SCRIPTS_DIR, FILE)):
                    print("Files are in place, initializing script!!!\n")
                    time.sleep(0.1)

                    # Run the Python script and tee the output
                    with open("mainlog", "w") as log_file:
                        process = subprocess.Popen(
                            ["/usr/bin/python3", "-u", os.path.join(CONTAINER_SCRIPTS_DIR, "main.py")],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True
                        )
                        for line in process.stdout:
                            print(line, end="")
                            log_file.write(line)
                            
                        process.wait()
                else:
                    print(f"\nERROR: \"{os.path.join(HOST_SCRIPTS_DIR, FILE)}\" not found")
            else:
                print(f"\nWarning: {FILE} not found in {CONTAINER_SCRIPTS_DIR}, something is wrong...")
        else:
            print("\nERROR: Make sure this container and Bazarr share the same media path allocations + that they have read and write permissions...")
    else:
        print("\nERROR: Bazarr connection unsuccessful, please check the containers following environment variables: \"API_KEY\" & \"BAZARR_URL\"...")
else:
    print(f"\nERROR: Make sure this container and Bazarr has the container-path \"{HOST_SCRIPTS_DIR}\" allocated...")