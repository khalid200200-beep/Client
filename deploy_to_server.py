import os
import sys
import paramiko
import time

HOST = "84.247.141.162"
PORT = 22
USER = "root"
PASS = "KkMm1416"
DB_PASS = "e250eb38de998d02"
DB_NAME = "shipping_db"
REMOTE_PATH = "/www/wwwroot/app.sudra.sa"

def run_ssh_command(ssh, cmd):
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(f"[STDOUT]\n{out}")
    if err:
        print(f"[STDERR]\n{err}")
    return out, err

def main():
    print(f"Connecting to {HOST}:{PORT} as {USER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)
    print("SSH Connection successful!")

    # 1. Check directory
    run_ssh_command(ssh, f"mkdir -p {REMOTE_PATH}")

    # 2. SFTP upload deployment zip
    print("Opening SFTP session...")
    sftp = ssh.open_sftp()
    
    local_zip = os.path.abspath("app_sudra_sa_deployment.zip")
    remote_zip = f"{REMOTE_PATH}/app_sudra_sa_deployment.zip"
    print(f"Uploading {local_zip} -> {remote_zip} ...")
    sftp.put(local_zip, remote_zip)
    print("Upload complete!")

    # 3. Unzip on remote server
    run_ssh_command(ssh, f"cd {REMOTE_PATH} && unzip -o app_sudra_sa_deployment.zip")

    # 4. Create database and import database.sql
    print("Setting up MySQL Database...")
    sql_create_db = f"mysql -u root -p{DB_PASS} -e \"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\""
    run_ssh_command(ssh, sql_create_db)

    sql_import = f"mysql -u root -p{DB_PASS} {DB_NAME} < {REMOTE_PATH}/database.sql"
    run_ssh_command(ssh, sql_import)

    # 5. Fix permissions
    print("Adjusting permissions...")
    run_ssh_command(ssh, f"chown -R www:www {REMOTE_PATH}")
    run_ssh_command(ssh, f"chmod -R 755 {REMOTE_PATH}")

    # 6. Verify Nginx / PHP configuration for app.sudra.sa
    print("Checking website status...")
    run_ssh_command(ssh, "ls -la /www/wwwroot/app.sudra.sa")

    # 7. Test local curl on server
    print("Testing local endpoints on server...")
    run_ssh_command(ssh, f"curl -k -I https://app.sudra.sa/ || curl -I http://127.0.0.1/")
    run_ssh_command(ssh, f"curl -k -s https://app.sudra.sa/api/banners.php || php {REMOTE_PATH}/api/banners.php")

    sftp.close()
    ssh.close()
    print("Deployment completed successfully!")

if __name__ == "__main__":
    main()
