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

def kill_gradle_daemons():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "java.exe"], capture_output=True)
    except Exception:
        pass

def copy_to_temp(src_name):
    src_dir = os.path.abspath(src_name)
    dest_dir = os.path.join(temp_base, src_name)
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
    return dest_dir

def run_flutter_cmd(cmd_list, cwd):
    print(f"\n>> Executing: {' '.join(cmd_list)} in {cwd}")
    res = subprocess.run(cmd_list, cwd=cwd, env=env, capture_output=True, text=True, errors='ignore')
    out = res.stdout.strip()
    err = res.stderr.strip()
    if out:
        print("STDOUT:\n", out[-1200:] if len(out) > 1200 else out)
    if err and res.returncode != 0:
        print("STDERR:\n", err[-1200:] if len(err) > 1200 else err)
    return res.returncode == 0, out, err

def main():
    print("==================================================")
    print("🚀 بدء الفحص والتحليل وبناء تطبيقات أندرويد")
    print("==================================================")

    output_dir = os.path.abspath("android_apks")
    os.makedirs(output_dir, exist_ok=True)

    # 1. CLIENT APP
    print("\n--------------------------------------------------")
    print("📱 1. تدقيق وفحص تطبيق العميل (Customer App)")
    print("--------------------------------------------------")
    kill_gradle_daemons()
    client_dir = copy_to_temp("client_app")

    run_flutter_cmd([FLUTTER_BAT, "clean"], client_dir)
    run_flutter_cmd([FLUTTER_BAT, "pub", "get"], client_dir)

    ok_analyze_c, out_analyze_c, _ = run_flutter_cmd([FLUTTER_BAT, "analyze"], client_dir)
    print(f"👉 Customer App Analyze: {'PASS ✅' if 'No issues found!' in out_analyze_c or ok_analyze_c else 'CHECK'}")

    print("\n🔨 Building Customer Release APK...")
    ok_release_c, _, _ = run_flutter_cmd([FLUTTER_BAT, "build", "apk", "--release"], client_dir)
    if ok_release_c:
        src_apk = os.path.join(client_dir, "build", "app", "outputs", "flutter-apk", "app-release.apk")
        dest_apk = os.path.join(output_dir, "Sudra_Client_App.apk")
        shutil.copy2(src_apk, dest_apk)
        print(f"👉 Customer Release APK: PASS ✅ ({os.path.getsize(dest_apk)/(1024*1024):.2f} MB)")

    print("\n🔨 Building Customer Debug APK...")
    ok_debug_c, _, _ = run_flutter_cmd([FLUTTER_BAT, "build", "apk", "--debug"], client_dir)
    if ok_debug_c:
        src_dbg = os.path.join(client_dir, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
        dest_dbg = os.path.join(output_dir, "Sudra_Client_App_debug.apk")
        if os.path.exists(src_dbg):
            shutil.copy2(src_dbg, dest_dbg)
            print(f"👉 Customer Debug APK: PASS ✅ ({os.path.getsize(dest_dbg)/(1024*1024):.2f} MB)")

    # 2. DRIVER APP
    print("\n--------------------------------------------------")
    print("🚚 2. تدقيق وفحص تطبيق السائق (Driver App)")
    print("--------------------------------------------------")
    kill_gradle_daemons()
    driver_dir = copy_to_temp("driver_app")

    run_flutter_cmd([FLUTTER_BAT, "clean"], driver_dir)
    run_flutter_cmd([FLUTTER_BAT, "pub", "get"], driver_dir)

    ok_analyze_d, out_analyze_d, _ = run_flutter_cmd([FLUTTER_BAT, "analyze"], driver_dir)
    print(f"👉 Driver App Analyze: {'PASS ✅' if 'No issues found!' in out_analyze_d or ok_analyze_d else 'CHECK'}")

    print("\n🔨 Building Driver Release APK...")
    ok_release_d, _, _ = run_flutter_cmd([FLUTTER_BAT, "build", "apk", "--release"], driver_dir)
    if ok_release_d:
        src_apk = os.path.join(driver_dir, "build", "app", "outputs", "flutter-apk", "app-release.apk")
        dest_apk = os.path.join(output_dir, "Sudra_Driver_App.apk")
        shutil.copy2(src_apk, dest_apk)
        print(f"👉 Driver Release APK: PASS ✅ ({os.path.getsize(dest_apk)/(1024*1024):.2f} MB)")

    print("\n🔨 Building Driver Debug APK...")
    ok_debug_d, _, _ = run_flutter_cmd([FLUTTER_BAT, "build", "apk", "--debug"], driver_dir)
    if ok_debug_d:
        src_dbg = os.path.join(driver_dir, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
        dest_dbg = os.path.join(output_dir, "Sudra_Driver_App_debug.apk")
        if os.path.exists(src_dbg):
            shutil.copy2(src_dbg, dest_dbg)
            print(f"👉 Driver Debug APK: PASS ✅ ({os.path.getsize(dest_dbg)/(1024*1024):.2f} MB)")

    print("\n==================================================")
    print("🎉 اكتمال عمليات الفحص والتحليل وبناء تطبيقات أندرويد!")
    print("📁 قائمة الحزم الجاهزة في مجلد android_apks:")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.apk'):
            f_path = os.path.join(output_dir, f)
            print(f"  🔹 {f} ({os.path.getsize(f_path)/(1024*1024):.2f} MB)")
    print("==================================================")

if __name__ == '__main__':
    main()
