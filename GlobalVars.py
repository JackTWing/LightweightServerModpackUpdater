import os
import sys

# Set Up Global Paths
user_path = os.path.expanduser("~")
user_path.replace("\\","/")

must_config_file_path = False

launcher_exec = "C:\\XboxGames\\Minecraft Launcher\\Content\\Minecraft.exe" # for Windows
"""Directory path of the "Minecraft.exe" file"""
if not os.path.exists(launcher_exec):
    must_config_file_path = True

# minecraft_dir = user_path + "/.minecraft"  # Linux/macOS
minecraft_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")
"""Directory path of the ".minecraft" folder"""
if not os.path.exists(minecraft_dir):
    must_config_file_path = True

mods_dir = os.path.join(minecraft_dir, "mods")
"""Directory path of the "mods" folder"""

installed_versions_dir = os.path.join(minecraft_dir, "versions")
"""Directory path pf the "versions" folder"""

jre_path = os.path.join(os.path.dirname(sys.executable), "jre", "bin", "java.exe")

# def get_java_path_safe():
# # WARNING: WILL NO LONGER WORK AS OF 2/11/26
#     if getattr(sys, 'frozen', False):
#         # Running in PyInstaller .exe bundle
#         base_path = sys._MEIPASS  # Temp folder PyInstaller extracts to
#     else:
#         # Running as plain script
#         base_path = os.path.dirname(os.path.abspath(__file__))

#     java_exe_path = os.path.join(base_path, "jre", "bin", "java.exe")
#     return java_exe_path

# Constants for widgets
default_font = "Georgia"
default_widget_offset = 10
default_hightlight_width = 2
default_button_width = 10

base_app_width = 570
base_app_height = 200

minecraft_green_color = "#00a914"

continuous_metadata_settings_update = True
