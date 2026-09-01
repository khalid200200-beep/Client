import paramiko
import requests
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='Password@123' if False else 'KkMm1416', timeout=10)

# Set password properly via PHP script on remote server
remote_script = """<?php
require '/www/wwwroot/app.sudra.sa/config/db.php';
$new_hash = password_hash('Password@123', PASSWORD_BCRYPT, ['cost' => 10]);
$stmt = $pdo->prepare('UPDATE users SET password = ? WHERE role = "admin" OR email = "KHALID200200@GMAIL.COM"');
$stmt->execute([$new_hash]);
$pdo->exec('DELETE FROM login_attempts');
echo "Updated rows: " . $stmt->rowCount() . "\n";
"""
sftp = ssh.open_sftp()
with sftp.file('/tmp/update_admin.php', 'w') as f:
    f.write(remote_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('php /tmp/update_admin.php && rm -f /tmp/update_admin.php')
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()

# Test Web Login via requests Session
print("Testing web login via requests session...")
s = requests.Session()
s.verify = False

r_page = s.get("https://app.sudra.sa/admin/login.php", timeout=10)
csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', r_page.text)
csrf_token = csrf_match.group(1) if csrf_match else ""

r_post = s.post("https://app.sudra.sa/admin/login.php", data={
    "csrf_token": csrf_token,
    "phone_or_email": "KHALID200200@GMAIL.COM",
    "password": "Password@123"
}, allow_redirects=True, timeout=10)

print(f"Login Response URL: {r_post.url}")
print("Contains Dashboard Header:", "لوحة التحكم" in r_post.text or "إدارة الشحنات" in r_post.text or "المدير العام" in r_post.text)
