import zipfile
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

root_dir = os.path.abspath(os.path.dirname(__file__))
exclude_dirs = {".dart_tool", "build", ".git", ".idea", ".gradle", "__pycache__"}

def zip_folder(folder_name, zip_name):
    zip_path = os.path.join(root_dir, zip_name)
    src_path = os.path.join(root_dir, folder_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(src_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                fpath = os.path.join(root, file)
                arcname = os.path.relpath(fpath, root_dir)
                zipf.write(fpath, arcname)
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Created {zip_name} ({size_mb:.2f} MB)")

# 1. Package Client App
zip_folder("client_app", "client_app_flutter_ready.zip")

# 2. Package Driver App
zip_folder("driver_app", "driver_app_flutter_ready.zip")

# 3. Package Full Master Code
master_zip_path = os.path.join(root_dir, "sudra_full_project_source_code.zip")
with zipfile.ZipFile(master_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for folder in ["client_app", "driver_app", "backend_php", "web_preview", "server_deploy", "lib"]:
        src_path = os.path.join(root_dir, folder)
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in files:
                    fpath = os.path.join(root, file)
                    arcname = os.path.relpath(fpath, root_dir)
                    zipf.write(fpath, arcname)
    for f in ["PROJECT_DOCUMENTATION_FOR_DEVELOPER.md", "DEPLOYMENT_INFO.md", "DEPLOYMENT_GUIDE.md", "README.md", "pubspec.yaml"]:
        fpath = os.path.join(root_dir, f)
        if os.path.exists(fpath):
            zipf.write(fpath, f)

master_size = os.path.getsize(master_zip_path) / (1024 * 1024)
print(f"Created sudra_full_project_source_code.zip ({master_size:.2f} MB)")
