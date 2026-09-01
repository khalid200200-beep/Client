import os
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4"
ZIP_PATH = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4.zip"

EXCLUDE_DIRS = {'.git', 'build', '.dart_tool', '.idea', '.gradle', 'scratch', '.system_generated', '__pycache__'}
EXCLUDE_EXTS = {'.log', '.tmp'}

print(f"Creating updated zip archive from: {ROOT_DIR}")
print(f"Target zip: {ZIP_PATH}")

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                continue
            abs_file = os.path.join(root, file)
            rel_file = os.path.relpath(abs_file, os.path.dirname(ROOT_DIR))
            zipf.write(abs_file, rel_file)

size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
print(f"✅ Successfully updated: {ZIP_PATH} ({size_mb:.2f} MB)")
