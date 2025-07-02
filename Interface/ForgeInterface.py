import re
import requests
import subprocess
import xml.etree.ElementTree as ET
from tkinter import messagebox

FORGE_METADATA_URL = "https://files.minecraftforge.net/net/minecraftforge/forge/maven-metadata.json"
MAVEN_CONNECT_ERR_MSG = "Unable to fetch data: Maven connection unavailible.\nCheck your Internet connection, use a VPN, or check maven outages"

def get_forge_versions(mc_version=None):
    response = requests.get(FORGE_METADATA_URL)
    if response.status_code == 200:
        data = response.json()
        if mc_version:
            # Return Forge versions for selected MC version
            return data.get(mc_version, [])
        else:
            # Return all versions for all MC versions
            versions = []
            for versions_list in data.values():
                versions.extend(versions_list)
            return versions
    else:
        print(f"Error fetching Forge versions: {response.status_code}")
        messagebox.showerror("Maven Connection Error", MAVEN_CONNECT_ERR_MSG)
        return []

def get_forge_installer_url(forge_version):

    if not forge_version:
        print("Error: Forge version must be specified.")
        return None
    
    base_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge_version}/"
    installer_url = base_url + f"forge-{forge_version}-installer.jar"
    return installer_url

def download_forge(forge_version, save_path="forge-installer.jar"):
    installer_url = get_forge_installer_url(forge_version)
    print(f"Downloading Forge from: {installer_url}")
    if not installer_url:
        return None
    
    response = requests.get(installer_url, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Forge {forge_version} downloaded as {save_path}")
        return save_path
    else:
        print(f"Error downloading Forge: {response.status_code}")
        return None

def install_forge(installer_path, mode="client"):
    if mode not in ["server", "client"]:
        print("Invalid mode! Choose 'server' or 'client'.")
        return
    
    install_cmd = ["java", "-jar", installer_path, f"--install{mode.capitalize()}"]
    try:
        subprocess.run(install_cmd, check=True)
        print(f"Forge {mode} installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Forge: {e}")

# ======================================================================================
# Neoforge Methods Below:
# ======================================================================================

NEOFORGE_METADATA_URL = "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"

def get_neoforge_versions(mc_version_raw):
    match = re.search(r'^\d+\.(.+)', mc_version_raw)  # match everything after first num and decimal
    mc_version = match.group(1) if match else mc_version_raw
    
    response = requests.get(NEOFORGE_METADATA_URL)
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        versions = [version.text for version in root.findall(".//version")]

        # Filter versions that start with selected MC version
        mc_version_releases = [version for version in versions if version.startswith(mc_version)]

        if not mc_version_releases:
            print(f"No NeoForge versions found for Minecraft {mc_version}")
            return None
        
        # Sort versions numerically
        mc_version_releases_sorted = sorted(mc_version_releases, key=lambda x: list(map(int, re.findall(r'\d+', x))), reverse=True)

        # Find latest / recommended versions
        latest_version = mc_version_releases_sorted[0]  # newest version
        recommended_version = None

        for version in mc_version_releases_sorted:
            if "-beta" not in version and "-rc" not in version:  # ignore betas and release candidates
                recommended_version = version
                break

        return {
            "all_versions": mc_version_releases_sorted,
            "latest": latest_version,
            "recommended": recommended_version or latest_version  # Default to latest if no stable version exists
        }
    else:
        print(f"Error fetching NeoForge versions: {response.status_code}")
        messagebox.showerror("Maven Connection Error", MAVEN_CONNECT_ERR_MSG)
        return {"all_versions": [], "latest_version": None, "recommended_version": None}

def get_neoforge_installer_url(version):
    return f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{version}/neoforge-{version}-installer.jar"

def download_neoforge(neoforge_version, save_path="neoforge-installer.jar"):
    installer_url = get_neoforge_installer_url(neoforge_version)
    if not installer_url:
        return None
    response = requests.get(installer_url, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"NeoForge {neoforge_version} downloaded as {save_path}")
        return save_path
    else:
        print(f"Error downloading NeoForge: {response.status_code}")
        return None

def install_neoforge(installer_path, mode="client"):
    if mode not in ["server", "client"]:
        print("Invalid mode! Choose 'server' or 'client'.")
        return
    
    install_cmd = ["java", "-jar", installer_path, f"--install{mode.capitalize()}"]
    try:
        subprocess.run(install_cmd, check=True)
        print(f"NeoForge {mode} installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing NeoForge: {e}")