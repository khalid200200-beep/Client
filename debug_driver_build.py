import subprocess
import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

JAVA_HOME = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"
ANDROID_HOME = r"C:\Users\khalid\Android\Sdk"
FLUTTER_BAT = r"C:\Users\khalid\flutter\bin\flutter.bat"

env = os.environ.copy()
env["JAVA_HOME"] = JAVA_HOME
env["ANDROID_HOME"] = ANDROID_HOME
env["PATH"] = f"{JAVA_HOME}\\bin;{ANDROID_HOME}\\platform-tools;{ANDROID_HOME}\\cmdline-tools\\latest\\bin;C:\\Users\\khalid\\flutter\\bin;" + env.get('PATH', '')

driver_temp = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_build\driver_app"

print("1. Running flutter clean and pub get...")
subprocess.run([FLUTTER_BAT, "clean"], cwd=driver_temp, env=env)
subprocess.run([FLUTTER_BAT, "pub", "get"], cwd=driver_temp, env=env)

print("2. Running flutter build apk --release...")
p = subprocess.run([FLUTTER_BAT, "build", "apk", "--release", "--verbose"], cwd=driver_temp, env=env, capture_output=True, text=True, errors='ignore')

print("Returncode:", p.returncode)
if p.returncode == 0:
    client_apk = os.path.join(driver_temp, "build", "app", "outputs", "flutter-apk", "app-release.apk")
    dest_driver_apk = os.path.abspath(r"android_apks\Sudra_Driver_App.apk")
    shutil.copy2(client_apk, dest_driver_apk)
    print("SUCCESS: Copied to", dest_driver_apk)
else:
    print("STDOUT ERROR:\n", p.stdout[-2500:] if p.stdout else '')
    print("STDERR ERROR:\n", p.stderr[-2500:] if p.stderr else '')
