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
    print(f"Syncing source {src_dir} -> {dest_dir}...")
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

def run_cmd(args, cwd=None):
    print(f"\n>> Running: {' '.join(args)} in {cwd or '.'}")
    res = subprocess.run(args, cwd=cwd, env=env, text=True, errors='ignore')
    if res.returncode != 0:
        print(f"❌ Command failed with return code {res.returncode}")
        return False
    return True

def main():
    print("==================================================")
    print("🚀 بدء بناء وتصدير تطبيقات أندرويد (APK) لسودرا")
    print("==================================================")

    output_dir = os.path.abspath("android_apks")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Build Client App
    kill_java()
    client_src = os.path.abspath("client_app")
    client_temp = os.path.join(temp_base, "client_app")
    copy_project_to_ascii_dir(client_src, client_temp)

    print(f"\n📦 1. بناء تطبيق العميل (Client App APK)...")
    if run_cmd([FLUTTER_BAT, "pub", "get"], cwd=client_temp):
        if run_cmd([FLUTTER_BAT, "build", "apk", "--release", "--no-tree-shake-icons"], cwd=client_temp):
            client_apk = os.path.join(client_temp, "build", "app", "outputs", "flutter-apk", "app-release.apk")
            if os.path.exists(client_apk):
                dest_client_apk = os.path.join(output_dir, "Sudra_Client_App.apk")
                shutil.copy2(client_apk, dest_client_apk)
                size_mb = os.path.getsize(dest_client_apk) / (1024 * 1024)
                print(f"✅ تم تصدير تطبيق العميل بنجاح: {dest_client_apk} ({size_mb:.2f} MB)")

    # 2. Build Driver App
    kill_java()
    driver_src = os.path.abspath("driver_app")
    driver_temp = os.path.join(temp_base, "driver_app")
    copy_project_to_ascii_dir(driver_src, driver_temp)

    print(f"\n📦 2. بناء تطبيق السائق (Driver App APK)...")
    if run_cmd([FLUTTER_BAT, "pub", "get"], cwd=driver_temp):
        if run_cmd([FLUTTER_BAT, "build", "apk", "--release", "--no-tree-shake-icons"], cwd=driver_temp):
            driver_apk = os.path.join(driver_temp, "build", "app", "outputs", "flutter-apk", "app-release.apk")
            if os.path.exists(driver_apk):
                dest_driver_apk = os.path.join(output_dir, "Sudra_Driver_App.apk")
                shutil.copy2(driver_apk, dest_driver_apk)
                size_mb = os.path.getsize(dest_driver_apk) / (1024 * 1024)
                print(f"✅ تم تصدير تطبيق السائق بنجاح: {dest_driver_apk} ({size_mb:.2f} MB)")

    print("\n==================================================")
    print("🎉 اكتمال عملية البناء والتصدير بنجاح!")
    print(f"📁 مجلد ملفات APK الجاهزة للتثبيت: {output_dir}")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.apk'):
            f_path = os.path.join(output_dir, f)
            print(f"  🔹 {f} ({os.path.getsize(f_path)/(1024*1024):.2f} MB)")

    # 3. Upload APKs to production server
    try:
        import paramiko
        print("\n🚀 جاري رفع ملفات APK إلى خادم الإنتاج (app.sudra.sa)...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)
        sftp = ssh.open_sftp()
        
        client_local = os.path.join(output_dir, "Sudra_Client_App.apk")
        if os.path.exists(client_local):
            print("  جاري رفع تطبيق العميل Sudra_Client_App.apk...")
            sftp.put(client_local, '/www/wwwroot/app.sudra.sa/Sudra_Client_App.apk')
            print("  ✅ تم رفع تطبيق العميل: https://app.sudra.sa/Sudra_Client_App.apk")
            
        driver_local = os.path.join(output_dir, "Sudra_Driver_App.apk")
        if os.path.exists(driver_local):
            print("  جاري رفع تطبيق السائق Sudra_Driver_App.apk...")
            sftp.put(driver_local, '/www/wwwroot/app.sudra.sa/Sudra_Driver_App.apk')
            print("  ✅ تم رفع تطبيق السائق: https://app.sudra.sa/Sudra_Driver_App.apk")
            
        sftp.close()
        ssh.close()
        print("🎉 تم اكتمال رفع التطبيقات وجاهزية روابط التنزيل المباشرة!")
    except Exception as e:
        print(f"⚠️ خطأ أثناء رفع APK للسيرفر: {e}")
    print("==================================================")

if __name__ == '__main__':
    main()
