import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

target_names = [
    "distribution.cer",
    "SUDRA_Client_App_Store.mobileprovision",
    "SUDRA_Captain_App_Store.mobileprovision",
    "AuthKey_GJS534KL8F.p8"
]

dest_dir = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"
os.makedirs(dest_dir, exist_ok=True)

search_dirs = [
    r"C:\Users\khalid\.gemini",
    r"C:\Users\khalid\AppData\Local\Temp",
    r"C:\Users\khalid\AppData\Local\Google\Chrome",
    r"C:\Users\khalid\AppData\Local\Microsoft\Edge",
    r"C:\Users\khalid\Downloads"
]

print("Searching for downloaded Apple files...")

found_map = {}
for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    for root, dirs, files in os.walk(s_dir):
        for f in files:
            for t in target_names:
                if f.lower() == t.lower() or (t.startswith("AuthKey_") and f.startswith("AuthKey_") and f.endswith(".p8")):
                    full_p = os.path.join(root, f)
                    if t not in found_map:
                        found_map[t] = full_p
                        dest_f = os.path.join(dest_dir, f)
                        shutil.copy2(full_p, dest_f)
                        print(f"✅ FOUND & COPIED {t} from: {full_p} -> {dest_f}")

print(f"\nTotal files processed: {len(found_map)} of {len(target_names)}")
