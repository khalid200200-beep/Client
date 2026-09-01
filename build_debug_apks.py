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

temp_base = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_build"
os.makedirs(temp_base, exist_ok=True)

def kill_java():
    subprocess.run(["taskkill", "/F", "/IM", "java.exe"], capture_output=True)

def copy_project_to_ascii_dir(src_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        for d in ['.git', 'build', '.dart_tool', '.idea']:
            if d in dirs: dirs.remove(d)
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dest_dir, rel_path) if rel_path != '.' else dest_dir
        os.makedirs(target_root, exist_ok=True)
        for file in files:
            src_file = os.path.join(root, file)
            target_file = os.path.join(target_root, file)
            try:
                shutil.copy2(src_file, target_file)
            except Exception:
                pass

def main():
    print("==================================================")
    print("🔨 بناء حزم التطوير (Debug APKs) للعميل والسائق")
    print("==================================================")

    output_dir = os.path.abspath("android_apks")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Customer Debug APK
    kill_java()
    c_src = os.path.abspath("client_app")
    c_temp = os.path.join(temp_base, "client_app")
    copy_project_to_ascii_dir(c_src, c_temp)

    print("\n📦 1. بناء Debug APK لتطبيق العميل...")
    res_c = subprocess.run([FLUTTER_BAT, "build", "apk", "--debug", "--no-tree-shake-icons"], cwd=c_temp, env=env, capture_output=True, text=True, errors='ignore')
    if res_c.returncode == 0:
        dbg_apk = os.path.join(c_temp, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
        dest = os.path.join(output_dir, "Sudra_Client_App_debug.apk")
        shutil.copy2(dbg_apk, dest)
        print(f"✅ Customer Debug APK: {dest} ({os.path.getsize(dest)/(1024*1024):.2f} MB)")
    else:
        print("❌ Failed Customer Debug:", res_c.stderr[-500:])

    # 2. Driver Debug APK
    kill_java()
    d_src = os.path.abspath("driver_app")
    d_temp = os.path.join(temp_base, "driver_app")
    copy_project_to_ascii_dir(d_src, d_temp)

    print("\n📦 2. بناء Debug APK لتطبيق السائق...")
    res_d = subprocess.run([FLUTTER_BAT, "build", "apk", "--debug", "--no-tree-shake-icons"], cwd=d_temp, env=env, capture_output=True, text=True, errors='ignore')
    if res_d.returncode == 0:
        dbg_apk = os.path.join(d_temp, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
        dest = os.path.join(output_dir, "Sudra_Driver_App_debug.apk")
        shutil.copy2(dbg_apk, dest)
        print(f"✅ Driver Debug APK: {dest} ({os.path.getsize(dest)/(1024*1024):.2f} MB)")
    else:
        print("❌ Failed Driver Debug:", res_d.stderr[-500:])

    print("\n==================================================")
    print("📁 قائمة الحزم المتوفرة بالكامل:")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.apk'):
            f_path = os.path.join(output_dir, f)
            print(f"  🔹 {f} ({os.path.getsize(f_path)/(1024*1024):.2f} MB)")
    print("==================================================")

if __name__ == '__main__':
    main()
