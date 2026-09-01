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
    print("🧪 تشغيل اختبارات Flutter (flutter test)")
    print("==================================================")

    # 1. Client App Tests
    print("\n--- 1. Customer App (flutter test) ---")
    c_src = os.path.abspath("client_app")
    c_temp = os.path.join(temp_base, "client_app")
    copy_project_to_ascii_dir(c_src, c_temp)

    res_c = subprocess.run([FLUTTER_BAT, "test"], cwd=c_temp, env=env, capture_output=True, text=True, errors='ignore')
    print("STDOUT:\n", res_c.stdout)
    if res_c.stderr:
        print("STDERR:\n", res_c.stderr)
    client_test_pass = res_c.returncode == 0 and "All tests passed!" in res_c.stdout
    print(f"👉 Customer flutter test: {'PASS ✅' if client_test_pass else 'FAIL ❌'}")

    # 2. Driver App Tests
    print("\n--- 2. Driver App (flutter test) ---")
    d_src = os.path.abspath("driver_app")
    d_temp = os.path.join(temp_base, "driver_app")
    copy_project_to_ascii_dir(d_src, d_temp)

    res_d = subprocess.run([FLUTTER_BAT, "test"], cwd=d_temp, env=env, capture_output=True, text=True, errors='ignore')
    print("STDOUT:\n", res_d.stdout)
    if res_d.stderr:
        print("STDERR:\n", res_d.stderr)
    driver_test_pass = res_d.returncode == 0 and "All tests passed!" in res_d.stdout
    print(f"👉 Driver flutter test: {'PASS ✅' if driver_test_pass else 'FAIL ❌'}")

    print("\n==================================================")
    print(f"Customer flutter test: {'PASS' if client_test_pass else 'FAIL'}")
    print(f"Driver flutter test: {'PASS' if driver_test_pass else 'FAIL'}")
    print("==================================================")

if __name__ == '__main__':
    main()
