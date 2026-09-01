import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

downloads = r"C:\Users\khalid\Downloads"
print("Scanning Downloads for .p8 files:")
for f in os.listdir(downloads):
    if f.endswith(".p8") or "AuthKey" in f:
        print(f"FOUND: {f}")
