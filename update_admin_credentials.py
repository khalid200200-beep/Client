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

# 1. Update Database
run("""mysql -u root -pe250eb38de998d02 shipping_db -e "
ALTER TABLE users ADD COLUMN email VARCHAR(100) NULL AFTER name;
" """)

sql_update_admin = """mysql -u root -pe250eb38de998d02 shipping_db -e "
INSERT INTO users (id, name, email, phone, password, city, role, is_active) VALUES
(1, 'خالد - المشرف العام', 'KHALID200200@GMAIL.COM', 'KHALID200200@GMAIL.COM', '\$2y\$10\$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', 'admin', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name), email=VALUES(email), phone=VALUES(phone), role='admin', is_active=1;
" """
run(sql_update_admin)

run("mysql -u root -pe250eb38de998d02 shipping_db -e 'SELECT id, name, email, phone, role FROM users WHERE role=\"admin\";'")

# 2. Upload files
sftp = ssh.open_sftp()
for f, remote_f in [
    ("backend_php/admin/login.php", "/www/wwwroot/app.sudra.sa/admin/login.php"),
    ("backend_php/api/index.php", "/www/wwwroot/app.sudra.sa/api/index.php"),
    ("web_preview/admin.html", "/www/wwwroot/app.sudra.sa/admin.html"),
    ("web_preview/index.html", "/www/wwwroot/app.sudra.sa/index.html")
]:
    print(f"Uploading {f} -> {remote_f} ...")
    sftp.put(os.path.abspath(f), remote_f)

sftp.close()
run("chown -R www:www /www/wwwroot/app.sudra.sa")
ssh.close()
print("Admin credentials update complete on server!")
