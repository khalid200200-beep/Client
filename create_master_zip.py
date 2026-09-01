import zipfile
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

root_dir = os.path.abspath(os.path.dirname(__file__))
zip_filename = os.path.join(root_dir, "sudra_full_project_source_code.zip")

dirs_to_include = [
    "client_app",
    "driver_app",
    "backend_php",
    "web_preview",
    "server_deploy",
    "lib"
]

files_to_include = [
    "PROJECT_DOCUMENTATION_FOR_DEVELOPER.md",
    "DEPLOYMENT_INFO.md",
    "DEPLOYMENT_GUIDE.md",
    "README.md",
    "pubspec.yaml"
]

# Exclude large cache folders like .dart_tool, build, .git
exclude_dirs = {".dart_tool", "build", ".git", ".idea", ".gradle"}

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for d in dirs_to_include:
        dir_path = os.path.join(root_dir, d)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                # filter out excluded dirs
                dirs[:] = [dr for dr in dirs if dr not in exclude_dirs]
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, root_dir)
                    zipf.write(file_path, arcname)
    
    for f in files_to_include:
        fpath = os.path.join(root_dir, f)
        if os.path.exists(fpath):
            zipf.write(fpath, f)

size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
print(f"Zip created successfully: {zip_filename}")
print(f"File Size: {size_mb:.2f} MB")
