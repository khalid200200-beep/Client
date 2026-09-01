import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMP_DIR = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_verify"

def run_cmd(cmd, cwd):
    print(f"\n--- Running: {cmd} in {cwd} ---")
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print("STDOUT:\n", res.stdout)
    if res.stderr:
        print("STDERR:\n", res.stderr)
    return res.returncode

def copy_project(src, dest):
    if os.path.exists(dest):
        try:
            shutil.rmtree(dest)
        except Exception:
            pass
    os.makedirs(dest, exist_ok=True)
    for item in os.listdir(src):
        if item in ['.dart_tool', 'build', '.git']:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

# 1. Verify Client App
print("=== 1. Checking Client App ===")
client_src = r"c:\Users\khalid\Downloads\تطبيق فلاتر\client_app"
client_dest = os.path.join(TEMP_DIR, "client_app")
copy_project(client_src, client_dest)

run_cmd("flutter pub get", client_dest)
ret1 = run_cmd("flutter analyze", client_dest)
print(f"Client App Analyze Result: {ret1}")

# 2. Verify Driver App
print("\n=== 2. Checking Driver App ===")
driver_src = r"c:\Users\khalid\Downloads\تطبيق فلاتر\driver_app"
driver_dest = os.path.join(TEMP_DIR, "driver_app")
copy_project(driver_src, driver_dest)

run_cmd("flutter pub get", driver_dest)
ret2 = run_cmd("flutter analyze", driver_dest)
print(f"Driver App Analyze Result: {ret2}")

if ret1 == 0 and ret2 == 0:
    print("\n✅ All Flutter Dart Code passed analysis with 0 errors!")
else:
    print(f"\n❌ Analysis failed with codes: client={ret1}, driver={ret2}")
