import os
import shutil
import tkinter as tk
from tkinter import messagebox

from Interface.DropboxInterface import *
from Interface.ForgeInterface import *
from Helpers.ModpackSyncHelper import *
from Helpers.JSONManipulationHelper import *
from GlobalVars import *

settings = {}
modpack_url = ""
already_setup = False

def resource_path(relative_path):
    """ Get absolute path to resource (for dev and PyInstaller) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def ensure_user_settings_file():
    """
    Ensure that a writable copy of the default settings file exists in the Minecraft directory.
    If not, copy it from the bundled resource.
    """
    bundled_settings = resource_path("lightweight_updater_settings.txt")
    writable_path = os.path.join(gv.minecraft_dir, "lightweight_updater_settings.txt")

    if not os.path.exists(writable_path):
        try:
            shutil.copy(bundled_settings, writable_path)
            print(f"✅ Copied default settings to: {writable_path}")
        except Exception as e:
            print(f"❌ Failed to copy settings file: {e}")

    return writable_path

def load_settings(path):
    settings = {}
    if not os.path.isfile(path):
        return settings

    with open(path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                settings[key.strip()] = value.strip()
    return settings

def save_settings(path, settings):
    with open(path, 'w') as f:
        for key, value in settings.items():
            f.write(f"{key} = {value}\n")

def write_and_save_settings(URL):
    if URL != "":
        settings["Modpack_URL"] = URL
    settings["MC_Version"] = settings.get("MC_Version")
    settings["Modloader"] = settings.get("Modloader")
    settings["Modloader_Version"] = settings.get("Modloader_Version")
    settings["MC_Version_Namespace"] = settings.get("MC_Version_Namespace")
    save_settings(settings_path, settings)

def save_single_setting(path, key, value):
    """
    Updates a single setting in the settings file without overwriting others.
    If the key does not exist, it is added.  This was a bit complicated...
    """
    # Load current settings
    if not os.path.exists(path):
        settings = {}
    else:
        with open(path, 'r') as f:
            lines = f.readlines()
            settings = {}
            for line in lines:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    settings[k.strip()] = v.strip()

    # Update the single value
    settings[key] = value

    # Save updated settings
    with open(path, 'w') as f:
        for k, v in settings.items():
            f.write(f"{k} = {v}\n")


settings_path = ensure_user_settings_file()
settings = load_settings(settings_path)

# Gets the updated packs / versions
def setup():
    global settings
    global modpack_url
    global settings_path
    global mc_launch_version
    global already_setup

    messagebox.showinfo("Confirm: Update Modpack", "This function will update the modpack and possibly reinstall Neo/Forge Modloaders.  This may take up to a minute or two, but usually less.  Click OK to confirm.")

    settings_path = os.path.join(os.getcwd(), "lightweight_updater_settings.txt")
    settings = load_settings(settings_path)

    modpack_url = settings.get("Modpack_URL", "")

    temp_dir = os.path.join(os.getcwd(), "temp_download")
    os.makedirs(temp_dir, exist_ok=True)
    temp_zip_file = os.path.join(temp_dir, "modpack.zip")

    forge_versions, neoforge_versions = get_installed_loader_versions(gv.minecraft_dir)
    installed_versions = forge_versions + neoforge_versions
    print(installed_versions)

    print(modpack_url)
    try:
        print(f"Starting modpack download from {modpack_url}...")
        pack_url = force_dropbox_folder_download(modpack_url)
    except ValueError as e:
        print(f"❌ Dropbox URL error (Please specify Dropbox URL!): {e}")
        return
    
    print(pack_url)
    download_modpack(pack_url, temp_zip_file)
    extract_dir = os.path.join(temp_dir, "extract")
    os.makedirs(extract_dir, exist_ok=True)
    print(f"Unzipping modpack: {temp_zip_file}")
    unzip_modpack(temp_zip_file, extract_dir)

    metadata_file_path = os.path.join(extract_dir, "custom_launcher_metadata.json")
    set_data = get_metadata(metadata_file_path)

    mc_version = set_data.get("mc_version")
    modloader = set_data.get("modloader")
    modloader_version = set_data.get("modloader_version")
    if gv.continuous_metadata_settings_update == True:
        settings["MC_Version"] = mc_version
        settings["Modloader"] = modloader
        settings["Modloader_Version"] = modloader_version

    already_setup = True

    if not is_loader_version_installed(modloader, mc_version, modloader_version, installed_versions):
        print("❌ Modloader is missing.")
        install_modloader(modloader, mc_version, modloader_version, gv.minecraft_dir)
        messagebox.showinfo("Install Complete", "Modloader installation complete.  You may need to launch Minecraft: Java twice in order to play the game.")

    clear_mods_folder()
    install_mods_to_minecraft(extract_dir)

    mc_launch_version = get_loader_version_namespace(modloader, mc_version, modloader_version, installed_versions)
    settings["MC_Version_Namespace"] = mc_launch_version
    save_settings(settings_path, settings)

    # Clean temp and start:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    messagebox.showinfo("Update Complete", "Pack update has been completed.")
    return None

"""
-----------------------------------------------------------------

Main app - Flows downwards (mostly)

----------------------------------------------------------------- 
"""

# setup()

settings_path = os.path.join(os.getcwd(), "lightweight_updater_settings.txt")
settings = load_settings(settings_path)
print(f"Loaded Settings: {settings}")
# mc_launch_version = settings["MC_Version_Namespace"]
already_setup = True

app = tk.Tk()
app.title("Minecraft: Java -  Server Pack Updater")
app.configure(background="grey")
app.geometry(str(gv.base_app_width) + "x" + str(gv.base_app_height))
app.minsize(width=570, height=180)

# Frame for containing all the main app elements
anti_grid_main_frame = tk.Frame(app, bg="grey")
anti_grid_main_frame.pack(side=tk.BOTTOM)
main_frame = tk.Frame(anti_grid_main_frame, bg="grey")
main_frame.grid()

settings_frame = tk.Frame(main_frame, bg="lightgrey")

URL_label = tk.Label(settings_frame, text="Dropbox URL:", font=gv.default_font, bg="lightgrey")
URL_enter = tk.Entry(settings_frame, font=gv.default_font, bg="darkgrey", width=40, relief="ridge", bd=5)
if already_setup:
    packurl = settings.get("Modpack_URL")
    if packurl is None:
        print("Modpack URL is not set.  Defaulting to https://dropbox.com")
        packurl = "https://dropbox.com"
    URL_enter.insert(0, packurl)

URL_label.pack(side=tk.TOP, anchor="nw")
URL_enter.pack(side=tk.TOP, anchor="sw")

settings_frame.pack(side=tk.TOP, anchor="center")

btn_save_settings = tk.Button(settings_frame, width=gv.default_button_width, bg="light blue", text="Save Settings", font=gv.default_font, command=lambda: write_and_save_settings(URL_enter.get()))
btn_save_settings.pack(side=tk.TOP, padx=5, anchor="center", expand=True)

update_label = tk.Label(settings_frame, text="This button updates to the latest server modpack and version:", font=gv.default_font, bg="lightgrey")
update_label.pack(side=tk.TOP, padx=5, anchor="center", expand=True)
btn_update = tk.Button(settings_frame, width=gv.default_button_width, bg="light blue", text="Do Update", font=gv.default_font, command=lambda: setup())
btn_update.pack(side=tk.BOTTOM, padx=5, anchor="center", expand=True)

def close_app():
    app.quit()
    return None

app.mainloop()