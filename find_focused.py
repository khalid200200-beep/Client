import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

roots = [
    r"C:\Users\khalid\.gemini\antigravity-ide\brain\88e3ef87-a08a-42a2-b7c4-637137f477dc",
    r"C:\Users\khalid\.gemini\antigravity-ide",
    r"C:\Users\khalid\Downloads\تطبيق"
]

for root_dir in roots:
    if not os.path.exists(root_dir):
        continue
    for r, d, files in os.walk(root_dir):
        for f in files:
            if f.endswith('.p8') or f.endswith('.cer') or f.endswith('.mobileprovision'):
                print(f"FOUND: {os.path.join(r, f)}")
