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
env["PATH"] = f"{JAVA_HOME}\\bin;{ANDROID_HOME}\\platform-tools;{ANDROID_HOME}\\cmdline-tools\\latest\\bin;C:\\Users\\khalid\\flutter\\bin;{env.get('PATH', '')}"

def run_cmd(args, cwd=None):
    print(f"\n>> Running: {' '.join(args)} in {cwd or '.'}")
    res = subprocess.run(args, cwd=cwd, env=env, text=True, errors='ignore')
    if res.returncode != 0:
        print(f"❌ Command failed with return code {res.returncode}")
        return False
    return True

def copy_project_to_ascii_dir(src_dir, dest_dir):
    print(f"Syncing source {src_dir} -> {dest_dir}...")
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, ignore_errors=True)
    shutil.copytree(src_dir, dest_dir, ignore=shutil.ignore_patterns('build', '.dart_tool'))

def main():
    print("==================================================")
    print("🚀 بدء بناء وتصدير تطبيق السائق (Driver App APK)")
    print("==================================================")

    output_dir = os.path.abspath("android_apks")
    os.makedirs(output_dir, exist_ok=True)

    temp_base = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_build"
    os.makedirs(temp_base, exist_ok=True)

    driver_src = os.path.abspath("driver_app")
    driver_temp = os.path.join(temp_base, "driver_app")
    copy_project_to_ascii_dir(driver_src, driver_temp)

    print(f"\n📦 بناء تطبيق السائق (Driver App APK)...")
    if run_cmd([FLUTTER_BAT, "pub", "get"], cwd=driver_temp):
        if run_cmd([FLUTTER_BAT, "build", "apk", "--release"], cwd=driver_temp):
            driver_apk = os.path.join(driver_temp, "build", "app", "outputs", "flutter-apk", "app-release.apk")
            if os.path.exists(driver_apk):
                dest_driver_apk = os.path.join(output_dir, "Sudra_Driver_App.apk")
                shutil.copy2(driver_apk, dest_driver_apk)
                size_mb = os.path.getsize(dest_driver_apk) / (1024 * 1024)
                print(f"✅ تم تصدير تطبيق السائق بنجاح: {dest_driver_apk} ({size_mb:.2f} MB)")

    print("\n==================================================")
    print("📁 قائمة التطبيقات الجاهزة في مجلد android_apks:")
    for f in os.listdir(output_dir):
        if f.endswith('.apk'):
            f_path = os.path.join(output_dir, f)
            print(f"  🔹 {f} ({os.path.getsize(f_path)/(1024*1024):.2f} MB)")
    print("==================================================")

if __name__ == '__main__':
    main()
