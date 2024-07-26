import os
import shutil
import subprocess
import time
import requests
import importlib.util

HOST_SCRIPTS_DIR = "/subaligner-bazarr"
CONTAINER_SCRIPTS_DIR = "/opt/subaligner-bazarr"
FILE = "addtosynclist.bash"

# Import variables from main.py
spec = importlib.util.spec_from_file_location("main", os.path.join(CONTAINER_SCRIPTS_DIR, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

print(f"API_KEY: {main.API_KEY}")
print(f"BAZARR_URL: {main.BAZARR_URL}")
print(f"SUBCLEANER: {main.SUBCLEANER}")
print(f"SLEEP: {main.SLEEP}\n")

def bazarr_status(max_retries=5, delay=10):
    url = f"{main.BAZARR_URL}/api/system/status"
    
    headers = {
        "X-API-KEY": f"{main.API_KEY}"
        }
    
    print("Attempting connection to Bazarr API...")
    
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

# Copy scripts to host directory
if os.path.isdir(HOST_SCRIPTS_DIR):
    if bazarr_status():
        print("Bazarr connection successful!!!")
        
        if os.path.isfile(os.path.join(CONTAINER_SCRIPTS_DIR, FILE)):
            shutil.copy2(os.path.join(CONTAINER_SCRIPTS_DIR, FILE), HOST_SCRIPTS_DIR)
            os.chmod(os.path.join(HOST_SCRIPTS_DIR, FILE), 0o755)  # This is equivalent to chmod +x
        else:
            print(f"Warning: {FILE} not found in {CONTAINER_SCRIPTS_DIR}")

        if os.path.isfile(os.path.join(HOST_SCRIPTS_DIR, FILE)):
            print("Scripts are in place!!!\n")
        else:
            print(f"ERROR: \"{os.path.join(HOST_SCRIPTS_DIR, FILE)}\" not found")

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
        print(f"ERROR: Bazarr connection unsuccessful, please check the containers following environment varibles: \"BAZARR_URL\" & \"API_KEY\"!")
else:
    print(f"ERROR: Make sure the container has the container path \"{HOST_SCRIPTS_DIR}\" allocated...")