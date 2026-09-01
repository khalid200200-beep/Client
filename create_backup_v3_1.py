import os
import sys
import zipfile
import shutil

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r"c:\Users\khalid\Downloads\تطبيق فلاتر"
BACKUP_NAME_1 = "SUDRA_Project_Source_v3.1.zip"
BACKUP_NAME_2 = "نسخة_رقم3_1_الهوية_الجديدة_والصور_المتعددة_واستعادة_كلمة_المرور.zip"

EXCLUDE_DIRS = {'.git', 'build', '.dart_tool', '.idea', '.gradle', 'scratch', '.system_generated'}
EXCLUDE_EXTS = {'.log', '.tmp'}

def make_backup():
    print("==================================================")
    print("📦 بدء أرشفة وحفظ المشروع بالإصدار الجديد 3.1 (v3.1)")
    print("==================================================")

    zip_path_1 = os.path.join(ROOT_DIR, BACKUP_NAME_1)
    
    with zipfile.ZipFile(zip_path_1, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        # 1. Folders to include
        include_folders = ['client_app', 'driver_app', 'backend_php', 'server_deploy', 'android_apks', 'web_preview']
        for folder in include_folders:
            folder_path = os.path.join(ROOT_DIR, folder)
            if not os.path.exists(folder_path):
                continue
            print(f"  Adding directory: {folder}...")
            for root, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                        continue
                    abs_file = os.path.join(root, file)
                    rel_file = os.path.relpath(abs_file, ROOT_DIR)
                    zipf.write(abs_file, rel_file)

        # 2. Key files at root
        for item in os.listdir(ROOT_DIR):
            abs_item = os.path.join(ROOT_DIR, item)
            if os.path.isfile(abs_item):
                if item.endswith('.zip') or item.endswith('.log'):
                    continue
                zipf.write(abs_item, item)
                
    size_mb = os.path.getsize(zip_path_1) / (1024 * 1024)
    print(f"✅ تم إنشاء النسخة الاحتياطية الأولى: {zip_path_1} ({size_mb:.2f} MB)")

    # Create the Arabic named copy
    zip_path_2 = os.path.join(ROOT_DIR, BACKUP_NAME_2)
    shutil.copy2(zip_path_1, zip_path_2)
    print(f"✅ تم إنشاء النسخة بالاسم العربي: {zip_path_2} ({size_mb:.2f} MB)")

    print("\n==================================================")
    print(f"🎉 تم حفظ وإصدار النسخة 3.1 بنجاح تام!")
    print("==================================================")

if __name__ == '__main__':
    make_backup()
