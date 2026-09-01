import paramiko
import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore')

print("=== SUDRA.SA SRC/APP DIRS ===")
print(run_cmd("find /www/wwwroot/sudra.sa/src -maxdepth 3"))

print("=== PM2 / NODE PROCESSES ===")
print(run_cmd("pm2 list || ps aux | grep node"))

# Test current response of support and privacy URLs
print("=== TESTING URLS ===")
for url in ["https://sudra.sa/support", "https://sudra.sa/privacy", "https://app.sudra.sa/privacy.html", "https://app.sudra.sa/support"]:
    try:
        r = requests.get(url, timeout=10)
        print(f"{url} -> Status: {r.status_code}, Length: {len(r.text)}, Title in text: {'<title>' in r.text}")
    except Exception as e:
        print(f"{url} -> Error: {e}")

ssh.close()
