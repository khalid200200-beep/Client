import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

downloads = r"C:\Users\khalid\Downloads"
signing_dir = r"C:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"
os.makedirs(signing_dir, exist_ok=True)

target_p8 = os.path.join(downloads, "AuthKey_KDDV3TG35U.p8")
if os.path.exists(target_p8):
    shutil.copy2(target_p8, os.path.join(signing_dir, "AuthKey_KDDV3TG35U.p8"))
    print(f"✅ Found and copied: {target_p8}")
else:
    print(f"Checking for any AuthKey_*.p8 in {downloads}:")
    for f in os.listdir(downloads):
        if f.startswith("AuthKey_") and f.endswith(".p8"):
            src = os.path.join(downloads, f)
            dest = os.path.join(signing_dir, f)
            shutil.copy2(src, dest)
            print(f"✅ Found & copied: {src} -> {dest}")
