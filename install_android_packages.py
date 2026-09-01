import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

sdk_root = r"C:\Users\khalid\Android\Sdk"
java_home = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"
sdkmanager = os.path.join(sdk_root, "cmdline-tools", "latest", "bin", "sdkmanager.bat")

env = os.environ.copy()
env["JAVA_HOME"] = java_home
env["ANDROID_HOME"] = sdk_root
env["PATH"] = f"{os.path.join(java_home, 'bin')};{os.path.join(sdk_root, 'cmdline-tools', 'latest', 'bin')};{env.get('PATH', '')}"

print("Installing Android Platform 34 and Build Tools 34.0.0...")
p = subprocess.Popen(
    [sdkmanager, "--install", "platform-tools", "platforms;android-34", "build-tools;34.0.0"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    env=env
)
# Send 'y' for license agreements if prompted
stdout, _ = p.communicate(input="y\ny\ny\ny\ny\ny\n")
print(stdout)

print("Configuring Flutter Android SDK and Licenses...")
flutter_bat = r"C:\Users\khalid\flutter\bin\flutter.bat"
subprocess.run([flutter_bat, "config", "--android-sdk", sdk_root], env=env, check=True)

# Accept flutter android licenses
p2 = subprocess.Popen(
    [flutter_bat, "doctor", "--android-licenses"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    env=env
)
stdout2, _ = p2.communicate(input="y\ny\ny\ny\ny\ny\ny\ny\n")
print(stdout2)
print("Android SDK Configuration Complete!")
