import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore')

print("=== SUDRA.SA PRIVACY PAGE ===")
print(run_cmd("cat /www/wwwroot/sudra.sa/src/app/privacy/page.tsx"))

print("=== SUDRA.SA CONTACT PAGE ===")
print(run_cmd("cat /www/wwwroot/sudra.sa/src/app/contact/page.tsx"))

ssh.close()
