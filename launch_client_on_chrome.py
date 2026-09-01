import os
import shutil
import subprocess
import webbrowser
import http.server
import socketserver
import threading
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

TEMP_DIR = r"C:\Users\khalid\AppData\Local\Temp\sudra_flutter_web\client_app"
SRC_DIR = r"c:\Users\khalid\Downloads\تطبيق فلاتر\client_app"
PORT = 8090

print("==================================================")
print("🌐 تجهيز وتشغيل تطبيق العميل على متصفح Google Chrome")
print("==================================================")

# 1. Sync files to temp ASCII directory
os.makedirs(TEMP_DIR, exist_ok=True)
def copytree_ignore(dir_path, filenames):
    ignore = set()
    for name in filenames:
        if name in ['.dart_tool', 'build', '.git', '.gradle']:
            ignore.add(name)
    return ignore

if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

print(">> نسخ ملفات تطبيق العميل إلى بيئة التشغيل...")
shutil.copytree(SRC_DIR, TEMP_DIR, ignore=copytree_ignore)

# 2. Build Flutter Web Release
print(">> جاري بناء نسخة الويب (Flutter Web Build)...")
subprocess.run(
    [r"C:\Users\khalid\flutter\bin\flutter.bat", "pub", "get"],
    cwd=TEMP_DIR,
    check=True,
    shell=True
)

subprocess.run(
    [r"C:\Users\khalid\flutter\bin\flutter.bat", "build", "web", "--release", "--no-tree-shake-icons"],
    cwd=TEMP_DIR,
    check=True,
    shell=True
)

WEB_BUILD_DIR = os.path.join(TEMP_DIR, "build", "web")
print(f"✅ تم بناء نسخة الويب بنجاح: {WEB_BUILD_DIR}")

# 3. Serve via local HTTP server
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_BUILD_DIR, **kwargs)

server = socketserver.TCPServer(("localhost", PORT), Handler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

url = f"http://localhost:{PORT}/"
print(f"\n🚀 تم تشغيل السيرفر المحلي: {url}")
print(">> جاري فتح تطبيق العميل في متصفح Google Chrome تلقائياً...")
webbrowser.open(url)

print("\n==================================================")
print(f"✅ التطبيق يعمل الآن في المتصفح على: {url}")
print("==================================================")

# Keep alive
while True:
    time.sleep(1)
