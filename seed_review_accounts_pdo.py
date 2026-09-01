import paramiko
import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

client_pass = "Review12345!"
driver_pass = "DriverReview12345!"

# Let's run a PHP CLI script on the server that connects via PDO and inserts/updates using prepared statements!
php_code = f"""<?php
require_once '/www/wwwroot/app.sudra.sa/config/db.php';

$client_hash = hashPassword('{client_pass}');
$driver_hash = hashPassword('{driver_pass}');

// 1. Client demo account
$stmt = $pdo->prepare("DELETE FROM users WHERE email IN ('review@sudra.sa', 'driver_review@sudra.sa') OR phone IN ('0559998877', '0501112233', '0551122334')");
$stmt->execute();

$stmt1 = $pdo->prepare("INSERT INTO users (name, email, phone, password, role, is_active, city) VALUES (?, ?, ?, ?, ?, 1, ?)");
$stmt1->execute(['حساب مراجعة آبل (عميل)', 'review@sudra.sa', '0551122334', $client_hash, 'client', 'الرياض']);

$stmt2 = $pdo->prepare("INSERT INTO users (name, email, phone, password, role, vehicle_plate, is_active, city) VALUES (?, ?, ?, ?, ?, ?, 1, ?)");
$stmt2->execute(['كابتن مراجعة آبل', 'driver_review@sudra.sa', '0500000000', $driver_hash, 'driver', 'أ ب ج 1111', 'الرياض']);

echo "SUCCESS_SEEDED\\n";
"""

# Write script to server temp and run
sftp = ssh.open_sftp()
with sftp.file('/tmp/seed_apple.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('php /tmp/seed_apple.php')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print("PHP Run output:", out)
if err:
    print("PHP Run error:", err)

ssh.close()

# Test Login via Production API
print("\n--- Testing Login via Production API ---")
r_client = requests.post("https://app.sudra.sa/api/auth/login", json={"email": "review@sudra.sa", "password": client_pass})
print(f"Client Login Status: {r_client.status_code}, Response: {r_client.json()}")

r_driver = requests.post("https://app.sudra.sa/api/auth/login", json={"email": "driver_review@sudra.sa", "password": driver_pass})
print(f"Driver Login Status: {r_driver.status_code}, Response: {r_driver.json()}")

r_client_phone = requests.post("https://app.sudra.sa/api/auth/login", json={"phone": "0551122334", "password": client_pass})
print(f"Client Phone Login Status: {r_client_phone.status_code}, Response: {r_client_phone.json()}")

r_driver_phone = requests.post("https://app.sudra.sa/api/auth/login", json={"phone": "0500000000", "password": driver_pass})
print(f"Driver Phone Login Status: {r_driver_phone.status_code}, Response: {r_driver_phone.json()}")
