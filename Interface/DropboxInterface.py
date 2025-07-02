import requests
import zipfile

def get_direct_download_url(dropbox_url):
    return dropbox_url.replace("?dl=0", "?raw=1").replace("?dl=1", "?raw=1")

def convert_dropbox_to_direct(url):
    if "dropbox.com" in url:
        url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com")
        url = url.replace("?dl=0", "").replace("?dl=1", "").replace("?raw=1", "")
    return url

def force_dropbox_folder_download(url: str) -> str:
    """Converts Dropbox folder link to ZIP download link"""
    if "dropbox.com" in url and "/scl/fo/" in url:
        if "dl=0" in url:
            url = url.replace("dl=0", "dl=1")
        elif "dl=1" not in url:
            if "?" in url:
                url += "&dl=1"
            else:
                url += "?dl=1"
    else:
        raise ValueError("This doesn't appear to be a Dropbox shared folder link.")
    return url

def download_modpack(url, save_path):
    r = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(r.content)

def unzip_modpack(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
