import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

search_roots = [
    r"C:\Users\khalid\Downloads",
    r"C:\Users\khalid\.gemini",
    r"C:\Users\khalid\AppData\Local\Temp",
    r"C:\Users\khalid\AppData\Local\Microsoft\Windows\INetCache"
]

now = time.time()
print("Searching for files created in last 15 minutes...")

for s_root in search_roots:
    if not os.path.exists(s_root):
        continue
    for root, dirs, files in os.walk(s_root):
        for f in files:
            if f.endswith('.cer') or f.endswith('.mobileprovision') or f.endswith('.p8') or 'distribution' in f.lower() or 'sudra' in f.lower():
                full = os.path.join(root, f)
                try:
                    mtime = os.path.getmtime(full)
                    if (now - mtime) < 1800: # last 30 min
                        print(f"FOUND RECENT: {full} ({os.path.getsize(full)} bytes)")
                except:
                    pass
