import paramiko
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
    print(f">>> {cmd}")
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

run("node -v")
run("pm2 list")
run("cat /www/server/panel/vhost/nginx/app.sudra.sa.conf")

ssh.close()
