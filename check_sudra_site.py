import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore')

print("=== SUDRA.SA CONTENTS ===")
print(run_cmd("ls -la /www/wwwroot/sudra.sa/"))

print("=== SUDRA.SA NGINX CONF ===")
print(run_cmd("cat /www/server/panel/vhost/nginx/sudra.sa.conf"))

print("=== APP.SUDRA.SA NGINX CONF ===")
print(run_cmd("cat /www/server/panel/vhost/nginx/app.sudra.sa.conf"))

ssh.close()
