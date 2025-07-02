import shutil
import os
import subprocess
import requests
import sys
import tempfile

import GlobalVars as gv

def move_mods(source_mods_folder, minecraft_mods_folder):
    for file in os.listdir(source_mods_folder):
        shutil.copy(os.path.join(source_mods_folder, file), minecraft_mods_folder)

def clean_up(paths):
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def get_installed_loader_versions(minecraft_dir):
    versions_dir = os.path.join(minecraft_dir, "versions")
    forge_versions = []
    neoforge_versions = []

    if not os.path.isdir(versions_dir):
        return forge_versions, neoforge_versions

    for folder_name in os.listdir(versions_dir):
        if "forge" in folder_name.lower():
            forge_versions.append(folder_name)
        elif "neoforge" in folder_name.lower():
            neoforge_versions.append(folder_name)

    return forge_versions, neoforge_versions

def is_loader_version_installed(modloader, mc_version, loader_version, installed_versions):
    if modloader.lower() == "forge":
        # Exact match for Forge
        target = f"{mc_version}-forge-{loader_version}"
        return target in installed_versions

    elif modloader.lower() == "neoforge":
        # Convert Minecraft version to neoforge version prefix
        mc_major_minor = mc_version.split(".")[0:2]  # ['1', '21']
        neoforge_prefix = f"{int(mc_major_minor[0])}{int(mc_major_minor[1])}."  # e.g., '21.'

        for v in installed_versions:
            if v.startswith("neoforge-"):
                version_str = v.replace("neoforge-", "")
                if version_str == loader_version:
                    return True
        return False
    
def install_modloader(modloader, mc_version, loader_version, minecraft_dir=None):
    if minecraft_dir is None:
        minecraft_dir = os.path.expanduser("~/.minecraft")

    temp_dir = tempfile.mkdtemp()
    print(f"Installing {modloader} for MC {mc_version} ({loader_version})...")

    try:
        if modloader.lower() == "forge":
            # Forge download URL format
            forge_installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{loader_version}/forge-{mc_version}-{loader_version}-installer.jar"
            installer_path = os.path.join(temp_dir, "forge_installer.jar")
            print(f"Downloading Forge installer: {forge_installer_url}")
            _download_file(forge_installer_url, installer_path)

            print("Running Forge installer...")
            try:
                subprocess.run([_get_java_exec(), '-jar', installer_path, '--installClient'], check=True)
                # subprocess.run([_get_java_exec(), "-jar", installer_path, "--installClient", f"--installDir={minecraft_dir}"], check=True)
            except FileNotFoundError:
                print("❌ Java not found. Please install Java and ensure it's in your PATH.")

        elif modloader.lower() == "neoforge":
            # NeoForge download URL format (always latest endpoint from Maven)
            group = "net/neoforged/neoforge"
            artifact = f"neoforge-{loader_version}-installer"
            neoforge_url = f"https://maven.neoforged.net/releases/{group}/{loader_version}/{artifact}.jar"
            installer_path = os.path.join(temp_dir, "neoforge_installer.jar")
            print(f"Downloading NeoForge installer: {neoforge_url}")
            _download_file(neoforge_url, installer_path)

            print("Running NeoForge installer...")
            try:
                subprocess.run([_get_java_exec(), '-jar', installer_path, '--installClient'], check=True)
                # subprocess.run([_get_java_exec(), "-jar", installer_path, "--installClient", f"--installDir={minecraft_dir}"], check=True)
            except FileNotFoundError:
                print("❌ Java not found. Please install Java and ensure it's in your PATH.")

        else:
            raise ValueError("Unsupported modloader: must be 'forge' or 'neoforge'")

        print("✅ Modloader installation complete.")

    except Exception as e:
        print(f"❌ Modloader installation failed: {e}")
    finally:
        shutil.rmtree(temp_dir)

def _download_file(url, save_path):
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception(f"Failed to download: {url} (HTTP {r.status_code})")
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

def _get_java_exec():
    if gv.override_sys_java:
        return gv.get_java_path_safe()
    else:
        return "java" if sys.platform != "win32" else "java.exe"

def install_mods_to_minecraft(extract_dir):
    mods_source_dir = extract_dir
    mods_dest_dir = gv.mods_dir

    if not os.path.isdir(mods_source_dir):
        raise FileNotFoundError(f"❌ 'mods' folder not found in extracted pack: {mods_source_dir}")

    mod_files = [f for f in os.listdir(mods_source_dir) if f.endswith(".jar")]
    if not mod_files:
        print("⚠️ No mod .jar files found in extracted directory.")
        return

    print(f"Installing {len(mod_files)} mod(s) to: {mods_dest_dir}")
    for mod_file in mod_files:
        src = os.path.join(mods_source_dir, mod_file)
        dst = os.path.join(mods_dest_dir, mod_file)
        shutil.copy2(src, dst)
        print(f"  ✅ {mod_file}")

    print("✅ Mod installation complete.")

def get_loader_version_namespace(modloader, mc_version, loader_version, installed_versions):
    print(f"Debug: {modloader}, {mc_version}, {loader_version}, {installed_versions}")
    modloader = modloader.lower()

    if modloader == "forge":
        target = f"{mc_version}-forge-{loader_version}"
        return target if target in installed_versions else None

    elif modloader == "neoforge":
        for v in installed_versions:
            if v.startswith("neoforge-") and v.replace("neoforge-", "") == loader_version:
                return v

    return None

def clear_mods_folder():
    mods_dir = gv.mods_dir

    if not os.path.isdir(mods_dir):
        print(f"❌ Mods directory not found: {mods_dir}")
        return

    removed = 0
    for file in os.listdir(mods_dir):
        file_path = os.path.join(mods_dir, file)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                removed += 1
                print(f"Removed: {file}")
            except Exception as e:
                print(f"⚠️ Failed to delete {file}: {e}")

    print(f"✅ Cleared {removed} file(s) from mods directory.")