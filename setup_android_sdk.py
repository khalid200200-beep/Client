import urllib.request
import zipfile
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

sdk_root = r"C:\Users\khalid\Android\Sdk"
cmdline_dir = os.path.join(sdk_root, "cmdline-tools", "latest")
os.makedirs(cmdline_dir, exist_ok=True)

zip_path = os.path.join(sdk_root, "cmdline-tools.zip")
url = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"

print(f"Downloading Android Commandline Tools from {url}...")
urllib.request.urlretrieve(url, zip_path)
print("Downloaded! Unzipping...")

temp_extract = os.path.join(sdk_root, "temp_extract")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_extract)

extracted_inner = os.path.join(temp_extract, "cmdline-tools")
for item in os.listdir(extracted_inner):
    s = os.path.join(extracted_inner, item)
    d = os.path.join(cmdline_dir, item)
    if os.path.exists(d):
        if os.path.isdir(d):
            shutil.rmtree(d)
        else:
            os.remove(d)
    shutil.move(s, d)

shutil.rmtree(temp_extract, ignore_errors=True)
if os.path.exists(zip_path):
    os.remove(zip_path)

print(f"Android SDK Commandline Tools installed successfully at: {cmdline_dir}")
