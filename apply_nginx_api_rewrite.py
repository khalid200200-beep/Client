import paramiko
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HOST = "84.247.141.162"
PORT = 22
USER = "root"
PASS = "KkMm1416"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(f">>> {cmd}")
    if out:
        print(out)
    if err:
        print(err)

# 1. Upload api/index.php
sftp = ssh.open_sftp()
local_api_index = os.path.abspath("backend_php/api/index.php")
sftp.put(local_api_index, "/www/wwwroot/app.sudra.sa/api/index.php")
sftp.close()
print("Uploaded api/index.php")

# 2. Update rewrite config
rewrite_conf = """location /api {
    try_files $uri $uri/ /api/index.php?$query_string;
}
"""
run(f"echo '{rewrite_conf}' > /www/server/panel/vhost/rewrite/app.sudra.sa.conf")
run("nginx -t")
run("nginx -s reload")
run("chown -R www:www /www/wwwroot/app.sudra.sa")

ssh.close()
print("Nginx configured and reloaded!")
