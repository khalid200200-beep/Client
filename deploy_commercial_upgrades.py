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

def exec_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(f">>> {cmd}")
    if out:
        print(out)
    if err and 'Warning' not in err:
        print("ERR:", err)

# 1. Upload files to server
sftp = ssh.open_sftp()
sftp.put(os.path.abspath('backend_php/config/db.php'), '/www/wwwroot/app.sudra.sa/config/db.php')
sftp.put(os.path.abspath('backend_php/api/index.php'), '/www/wwwroot/app.sudra.sa/api/index.php')
sftp.put(os.path.abspath('backend_php/admin/login.php'), '/www/wwwroot/app.sudra.sa/admin/login.php')

# 2. Setup backup script
backup_script = """#!/bin/bash
BACKUP_DIR="/www/backup/database"
mkdir -p "$BACKUP_DIR"
DATE=$(date +"%Y%m%d_%H%M%S")
FILENAME="shipping_db_$DATE.sql.gz"

mysqldump -u root -pe250eb38de998d02 --single-transaction --quick shipping_db 2>/dev/null | gzip > "$BACKUP_DIR/$FILENAME"
chmod 600 "$BACKUP_DIR/$FILENAME"

find "$BACKUP_DIR" -name "shipping_db_*.sql.gz" -type f -mtime +30 -delete
"""

with sftp.file('/www/backup/backup_sudra_db.sh', 'w') as f:
    f.write(backup_script)
sftp.close()

exec_cmd("chmod +x /www/backup/backup_sudra_db.sh")
# Test running backup script immediately
exec_cmd("/www/backup/backup_sudra_db.sh")
exec_cmd("ls -lh /www/backup/database/")

# Add cron job for daily backup at 3:00 AM
exec_cmd("""(crontab -l 2>/dev/null | grep -v 'backup_sudra_db.sh' ; echo '0 3 * * * /www/backup/backup_sudra_db.sh >/dev/null 2>&1') | crontab -""")

exec_cmd("chown -R www:www /www/wwwroot/app.sudra.sa")
ssh.close()
print("Commercial upgrades, security & backup automation deployed successfully!")
