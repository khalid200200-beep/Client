import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

JAVA_HOME = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"
ANDROID_HOME = r"C:\Users\khalid\Android\Sdk"
FLUTTER_BAT = r"C:\Users\khalid\flutter\bin\flutter.bat"

env = os.environ.copy()
env["JAVA_HOME"] = JAVA_HOME
env["ANDROID_HOME"] = ANDROID_HOME
env["PATH"] = f"{JAVA_HOME}\\bin;{ANDROID_HOME}\\platform-tools;{ANDROID_HOME}\\cmdline-tools\\latest\\bin;C:\\Users\\khalid\\flutter\\bin;" + env.get('PATH', '')

driver_temp = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_build\driver_app\android"

# Run gradle assembleRelease directly with --stacktrace
p = subprocess.run([os.path.join(driver_temp, "gradlew.bat"), "assembleRelease", "--stacktrace"], cwd=driver_temp, env=env, capture_output=True, text=True, errors='ignore')

print("Returncode:", p.returncode)
print("STDOUT tail:\n", p.stdout[-3000:] if p.stdout else '')
print("STDERR tail:\n", p.stderr[-3000:] if p.stderr else '')
