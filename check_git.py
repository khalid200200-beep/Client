import subprocess
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

cwd = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4"

# Check git status
res = subprocess.run(["git", "status"], cwd=cwd, capture_output=True, text=True)
print("Git status:", res.stdout, res.stderr)
