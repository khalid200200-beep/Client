import paramiko
import sys
import bcrypt

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("84.247.141.162", port=22, username="root", password="KkMm1416", timeout=30)

hashed = bcrypt.hashpw(b"123456", bcrypt.gensalt(10)).decode('utf-8')

script = f"""<?php
require_once '/www/wwwroot/app.sudra.sa/config/db.php';

// Ensure active test driver exists
$stmt = $pdo->prepare("SELECT id FROM users WHERE phone = '0509876543' OR email = 'driver@sudra.sa'");
$stmt->execute();
$driver = $stmt->fetch();

if ($driver) {{
    $upd = $pdo->prepare("UPDATE users SET email = 'driver@sudra.sa', role = 'driver', is_active = 1 WHERE id = ?");
    $upd->execute([$driver['id']]);
}} else {{
    $ins = $pdo->prepare("INSERT INTO users (name, email, phone, password, city, vehicle_plate, role, is_active) VALUES ('أحمد السائق', 'driver@sudra.sa', '0509876543', ?, 'الخرطوم', 'خ 1234', 'driver', 1)");
    $ins->execute(['{hashed}']);
}}

echo "Driver user updated/created successfully!\\n";
"""

sftp = ssh.open_sftp()
with sftp.file('/www/wwwroot/app.sudra.sa/update_driver.php', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('php /www/wwwroot/app.sudra.sa/update_driver.php && rm -f /www/wwwroot/app.sudra.sa/update_driver.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
