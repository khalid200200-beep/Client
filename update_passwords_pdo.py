import paramiko
import sys
import bcrypt

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("84.247.141.162", port=22, username="root", password="KkMm1416", timeout=30)

hashed = bcrypt.hashpw(b"123456", bcrypt.gensalt(10)).decode('utf-8')

# Write a temporary PHP script on the server to update passwords via PDO safely without bash dollar escaping issues
update_php = f"""<?php
require_once '/www/wwwroot/app.sudra.sa/config/db.php';
$hash = '{hashed}';
$stmt = $pdo->prepare("UPDATE users SET email = 'KHALID200200@GMAIL.COM', password = ?, role = 'admin' WHERE id = 1 OR role = 'admin'");
$stmt->execute([$hash]);

$stmt2 = $pdo->prepare("UPDATE users SET password = ? WHERE password NOT LIKE '$2y$%'");
$stmt2->execute([$hash]);

echo "Users updated successfully via PDO!\\n";
"""

sftp = ssh.open_sftp()
with sftp.file('/www/wwwroot/app.sudra.sa/update_passwords.php', 'w') as f:
    f.write(update_php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('php /www/wwwroot/app.sudra.sa/update_passwords.php && rm -f /www/wwwroot/app.sudra.sa/update_passwords.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
