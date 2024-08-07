import os
import shutil
import subprocess
import time
import requests
import importlib.util

HOST_SCRIPTS_DIR = "/subaligner-bazarr"
CONTAINER_SCRIPTS_DIR = "/opt/subaligner-bazarr"
REPO_URL = "https://github.com/tarzoq/subaligner-bazarr"
FILE = "addtosynclist.bash"
START = "start.py"
FILES_TO_CHECK = [FILE, "main.py", "requirements.txt", START]


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
        print("Bazarr connection successful!!!\n")
        
        print("Fetching updates...")
        try:
            # Enable sparse checkout
            subprocess.run(["/usr/bin/git", "-C", CONTAINER_SCRIPTS_DIR, "config", "core.sparsecheckout", "true"], check=True)
            
            # Define which files to check out
            with open(os.path.join(CONTAINER_SCRIPTS_DIR, ".git/info/sparse-checkout"), "w") as f:
                for file in FILES_TO_CHECK:
                    f.write(f"{file}\n")
                    
            # Fetch the latest changes
            subprocess.run(["/usr/bin/git", "-C", CONTAINER_SCRIPTS_DIR, "fetch", "origin", "main"], check=True)
            
            # Check if there are any changes
            result = subprocess.run(["/usr/bin/git", "-C", CONTAINER_SCRIPTS_DIR, "diff", "--quiet", "HEAD", "origin/main"], capture_output=True)
            
            if result.returncode != 0:
                # There are changes, so pull them
                subprocess.run(["/usr/bin/git", "-C", CONTAINER_SCRIPTS_DIR, "pull", "origin", "main"], check=True)
                print("Updates installed successfully!!!\n")
                
                # Check if there are any changes
                result = subprocess.run(["/usr/bin/git", "-C", CONTAINER_SCRIPTS_DIR, "diff", "--quiet", "HEAD", "origin/main", "--", START], capture_output=True)
                
                if result.returncode != 0:
                    print("WARNING: Init script updated, restart container to apply updates!\n")
                
            else:
                print("Files are already up to date!!!\n")       
            
        except subprocess.CalledProcessError:
            print("Update check failed...\n")
        
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