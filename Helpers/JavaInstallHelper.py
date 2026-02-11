import shutil
import os
import subprocess
import requests
import sys
import tempfile
import requests
import re

import GlobalVars as gv

def clean_up(paths):
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def get_latest_jre8_url():
    # The official manual page always contains the latest BundleIds
    manual_url = "https://www.java.com/en/download/manual.jsp"
    response = requests.get(manual_url)
    
    # regex looks for the specific "BundleId=" pattern used for windows offline and extracts the full direct download URL
    match = re.search(r'https://javadl\.oracle\.com/webapps/download/AutoDL\?BundleId=[\w_]+', response.text)
    
    if match:
        return match.group(0)
    else:
        # Fallback to current link (will break eventually) if scraping fails
        return "https://javadl.oracle.com/webapps/download/AutoDL?BundleId=252907_0d06828d282343ea81775b28020a7cd3"

def download_java(url, target_directory, filename="jre8_installer.exe"):
    """
    Downloads the file from the given URL and saves it to target_directory.
    """
    # Create directory if it doesn't exist
    if not os.path.exists(target_directory):
        os.makedirs(target_directory, exist_ok=True)
        print(f"Created directory: {target_directory}")

    # Define full path for the file
    file_path = os.path.join(target_directory, filename)

    print(f"Downloading to: {file_path}")
    
    # Stream download to avoid loading everything into memory
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # check for HTTP errors
        with open(file_path, 'wb') as f:
            # use shutil to pipe raw stream directly to file
            shutil.copyfileobj(response.raw, f)
            
    print("Download finished!")
    return file_path

def do_install_jre_silent(installer_path):
    # /s : Performs a completely silent installation
    # SPONSORS=0 : Bypasses any third-party offers (like browser toolbars)
    # REMOVEOUTOFDATEJRES=1 : Cleans up old, insecure JRE versions
    # AUTO_UPDATE=0 : Disables the automatic update prompt
    
    cmd = [
        installer_path, 
        "/s", 
        "SPONSORS=0", 
        "REMOVEOUTOFDATEJRES=1", 
        "AUTO_UPDATE=0"
    ]
    
    try:
        print("Starting silent installation...")
        subprocess.run(cmd, check=True)
        print("Java JRE installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Installation failed with error: {e}")
    
def install_java():

    temp_dir = tempfile.mkdtemp()
    print(f"Installing base Java...")

    try: 
        java_url = get_latest_jre8_url()
        installer_path = download_java(java_url, temp_dir)

        print("Running Java installer silently...")
        do_install_jre_silent(installer_path)
        print("✅ Java installation complete.")

    except Exception as e:
        print(f"❌ Java installation failed: {e}")
    finally:
        shutil.rmtree(temp_dir)