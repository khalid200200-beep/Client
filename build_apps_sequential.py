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
env["GRADLE_OPTS"] = "-Dorg.gradle.daemon=false -Dorg.gradle.jvmargs=\"-Xmx1024m -XX:MaxMetaspaceSize=256m\""
env["PATH"] = f"{JAVA_HOME}\\bin;{ANDROID_HOME}\\platform-tools;{ANDROID_HOME}\\cmdline-tools\\latest\\bin;C:\\Users\\khalid\\flutter\\bin;" + env.get('PATH', '')

temp_base = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_build"
os.makedirs(temp_base, exist_ok=True)

def kill_java():
    subprocess.run(["taskkill", "/F", "/IM", "java.exe"], capture_output=True)

def copy_to_temp(src_name):
    src_dir = os.path.abspath(src_name)
    dest_dir = os.path.join(temp_base, src_name)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, ignore_errors=True)
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
    return dest_dir

def main():
    print("==================================================")
    print("🚀 بدء بناء واختبار تطبيقات Flutter (Sequential Mode)")
    print("==================================================")

    output_dir = os.path.abspath("android_apks")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Customer App
    print("\n📦 1. بناء تطبيق العميل (Customer App)...")
    kill_java()
    c_dir = copy_to_temp("client_app")

    p_get_c = subprocess.run([FLUTTER_BAT, "pub", "get"], cwd=c_dir, env=env, capture_output=True, text=True, errors='ignore')
    p_ana_c = subprocess.run([FLUTTER_BAT, "analyze"], cwd=c_dir, env=env, capture_output=True, text=True, errors='ignore')
    print("Analyze Customer App:\n", p_ana_c.stdout[:500] if p_ana_c.stdout else p_ana_c.stderr[:500])

    p_rel_c = subprocess.run([FLUTTER_BAT, "build", "apk", "--release", "--no-tree-shake-icons"], cwd=c_dir, env=env, capture_output=True, text=True, errors='ignore')
    print("Returncode Customer Release:", p_rel_c.returncode)
    if p_rel_c.returncode == 0:
        src_apk = os.path.join(c_dir, "build", "app", "outputs", "flutter-apk", "app-release.apk")
        dest_apk = os.path.join(output_dir, "Sudra_Client_App.apk")
        if os.path.exists(src_apk):
            shutil.copy2(src_apk, dest_apk)
            print(f"✅ Customer App APK: {dest_apk} ({os.path.getsize(dest_apk)/(1024*1024):.2f} MB)")
    else:
        print("Error Customer:\n", p_rel_c.stderr[-1000:] if p_rel_c.stderr else p_rel_c.stdout[-1000:])

    # 2. Driver App
    print("\n📦 2. بناء تطبيق السائق (Driver App)...")
    kill_java()
    d_dir = copy_to_temp("driver_app")

    p_get_d = subprocess.run([FLUTTER_BAT, "pub", "get"], cwd=d_dir, env=env, capture_output=True, text=True, errors='ignore')
    p_ana_d = subprocess.run([FLUTTER_BAT, "analyze"], cwd=d_dir, env=env, capture_output=True, text=True, errors='ignore')
    print("Analyze Driver App:\n", p_ana_d.stdout[:500] if p_ana_d.stdout else p_ana_d.stderr[:500])

    p_rel_d = subprocess.run([FLUTTER_BAT, "build", "apk", "--release", "--no-tree-shake-icons"], cwd=d_dir, env=env, capture_output=True, text=True, errors='ignore')
    print("Returncode Driver Release:", p_rel_d.returncode)
    if p_rel_d.returncode == 0:
        src_apk = os.path.join(d_dir, "build", "app", "outputs", "flutter-apk", "app-release.apk")
        dest_apk = os.path.join(output_dir, "Sudra_Driver_App.apk")
        if os.path.exists(src_apk):
            shutil.copy2(src_apk, dest_apk)
            print(f"✅ Driver App APK: {dest_apk} ({os.path.getsize(dest_apk)/(1024*1024):.2f} MB)")
    else:
        print("Error Driver:\n", p_rel_d.stderr[-1000:] if p_rel_d.stderr else p_rel_d.stdout[-1000:])

    print("\n==================================================")
    print("📁 قائمة الحزم الجاهزة في مجلد android_apks:")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.apk'):
            f_path = os.path.join(output_dir, f)
            print(f"  🔹 {f} ({os.path.getsize(f_path)/(1024*1024):.2f} MB)")
    print("==================================================")

if __name__ == '__main__':
    main()
