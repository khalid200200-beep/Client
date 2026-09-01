import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

d = r"C:\Users\khalid\Downloads"
print(f"Items in {d}:")
for item in os.listdir(d):
    full = os.path.join(d, item)
    if os.path.isfile(full):
        print(f"FILE: {item} ({os.path.getsize(full)} bytes)")
    else:
        print(f"DIR: {item}")
