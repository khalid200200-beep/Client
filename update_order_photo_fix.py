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

# 1. Update MySQL column type
run("""mysql -u root -pe250eb38de998d02 shipping_db -e "
ALTER TABLE orders MODIFY image_path LONGTEXT NULL;
" """)

# 2. Upload files
sftp = ssh.open_sftp()
sftp.put(os.path.abspath('web_preview/client.html'), '/www/wwwroot/app.sudra.sa/client.html')
sftp.put(os.path.abspath('backend_php/api/index.php'), '/www/wwwroot/app.sudra.sa/api/index.php')
sftp.close()

run("chown -R www:www /www/wwwroot/app.sudra.sa")
ssh.close()
print("Server database & files updated successfully!")
