import paramiko
import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_query(sql):
    cmd = f'mysql -u root -pe250eb38de998d02 shipping_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return out, err

client_pass = "Review12345!"
driver_pass = "DriverReview12345!"

cmd_hash = f'php -r "echo password_hash(\'{client_pass}\', PASSWORD_BCRYPT) . PHP_EOL . password_hash(\'{driver_pass}\', PASSWORD_BCRYPT);"'
stdin, stdout, stderr = ssh.exec_command(cmd_hash)
hashes = stdout.read().decode('utf-8').strip().split()
client_hash = hashes[0]
driver_hash = hashes[1]

# Delete any existing old entries with these emails or phones to avoid collision
run_query("DELETE FROM users WHERE email IN ('review@sudra.sa', 'driver_review@sudra.sa') OR phone IN ('0559998877', '0501112233');")

# 1. Insert Client Demo Account
# Email: review@sudra.sa, Phone: 0559998877
sql_client = f"""
INSERT INTO users (name, email, phone, password, role, is_active, city, created_at)
VALUES ('حساب مراجعة آبل (عميل)', 'review@sudra.sa', '0559998877', '{client_hash}', 'client', 1, 'الرياض', NOW());
"""
run_query(sql_client)

# 2. Insert Driver Demo Account
# Email: driver_review@sudra.sa, Phone: 0501112233
sql_driver = f"""
INSERT INTO users (name, email, phone, password, role, vehicle_plate, is_active, city, created_at)
VALUES ('كابتن مراجعة آبل', 'driver_review@sudra.sa', '0501112233', '{driver_hash}', 'driver', 'أ ب ج 1111', 1, 'الرياض', NOW());
"""
run_query(sql_driver)

out_verify, _ = run_query("SELECT id, name, email, phone, role, is_active, city FROM users WHERE email IN ('review@sudra.sa', 'driver_review@sudra.sa');")
print("Verified Review Accounts in DB:")
print(out_verify)

ssh.close()

# Test Login via Production API
print("\n--- Testing Login via Production API ---")
r_client = requests.post("https://app.sudra.sa/api/auth/login", json={"email": "review@sudra.sa", "password": client_pass})
print(f"Client Login Status: {r_client.status_code}, Response: {r_client.json().get('message')}")

r_driver = requests.post("https://app.sudra.sa/api/auth/login", json={"email": "driver_review@sudra.sa", "password": driver_pass})
print(f"Driver Login Status: {r_driver.status_code}, Response: {r_driver.json().get('message')}")

# Also test phone login
r_client_phone = requests.post("https://app.sudra.sa/api/auth/login", json={"phone": "0559998877", "password": client_pass})
print(f"Client Phone Login Status: {r_client_phone.status_code}, Response: {r_client_phone.json().get('message')}")

r_driver_phone = requests.post("https://app.sudra.sa/api/auth/login", json={"phone": "0501112233", "password": driver_pass})
print(f"Driver Phone Login Status: {r_driver_phone.status_code}, Response: {r_driver_phone.json().get('message')}")
