import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return out, err

print("=== NGINX SITES / VHOSTS ===")
out, _ = run_cmd("ls -la /www/server/panel/vhost/nginx/ || ls -la /etc/nginx/sites-enabled/")
print(out)

print("=== WEB ROOTS ===")
out, _ = run_cmd("ls -la /www/wwwroot/")
print(out)

print("=== APP.SUDRA.SA CONTENTS ===")
out, _ = run_cmd("ls -la /www/wwwroot/app.sudra.sa/")
print(out)

ssh.close()
