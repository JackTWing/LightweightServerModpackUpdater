import json
import sys
import os

main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
# Add the parent directory to sys.path
sys.path.append(main_dir)

def get_metadata(path):
    if not os.path.isfile(path):
        return None

    with open(path, 'r') as f:
        data = json.load(f)

    metadata_data = data.get("modset")
    return metadata_data