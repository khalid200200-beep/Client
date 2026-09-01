import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

search_roots = [
    r"C:\Users\khalid\Downloads",
    r"C:\Users\khalid\.gemini",
    r"C:\Users\khalid\AppData\Local\Temp",
    r"C:\Users\khalid\AppData\Local\Google\Chrome\User Data",
    r"C:\Users\khalid"
]

print("Searching for AuthKey_GJS534KL8F.p8 and .cer files...")

found_files = []
for root_path in search_roots:
    if not os.path.exists(root_path):
        continue
    for root, dirs, files in os.walk(root_path):
        # Ignore deep node_modules or large git folders
        if 'node_modules' in root or '.git' in root:
            continue
        for f in files:
            if f.startswith("AuthKey_") or f.endswith(".cer") or f.endswith(".mobileprovision"):
                full_path = os.path.join(root, f)
                found_files.append(full_path)
                print(f"FOUND: {full_path}")

print(f"\nTotal files found: {len(found_files)}")
