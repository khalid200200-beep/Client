import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

target_file = "AuthKey_KDDV3TG35U.p8"
signing_dir = r"C:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"

search_dirs = [
    r"C:\Users\khalid\.gemini",
    r"C:\Users\khalid\AppData",
    r"C:\Users\khalid\Downloads",
    r"C:\Users\khalid\Desktop"
]

found = False
for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    for root, dirs, files in os.walk(s_dir):
        if target_file in files:
            full_p = os.path.join(root, target_file)
            dest_p = os.path.join(signing_dir, target_file)
            shutil.copy2(full_p, dest_p)
            print(f"✅ FOUND & COPIED: {full_p} -> {dest_p}")
            found = True
            break
    if found:
        break

if not found:
    print(f"Searching for any .p8 file...")
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for root, dirs, files in os.walk(s_dir):
            for f in files:
                if f.endswith('.p8'):
                    full_p = os.path.join(root, f)
                    print(f"Found P8: {full_p}")
