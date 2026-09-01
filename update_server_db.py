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
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(f"[OUT] {out}")
    if err:
        print(f"[ERR] {err}")

print("Updating schema...")
sql_alter_users = """
mysql -u root -pe250eb38de998d02 shipping_db -e "
ALTER TABLE users ADD COLUMN IF NOT EXISTS vehicle_plate VARCHAR(50) NULL AFTER city;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active TINYINT(1) DEFAULT 1 AFTER role;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS pickup_address VARCHAR(255) NULL AFTER city;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_address VARCHAR(255) NULL AFTER pickup_address;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS loaded_at TIMESTAMP NULL AFTER failure_reason;
"
"""
run(sql_alter_users)

sql_insert_users = """
mysql -u root -pe250eb38de998d02 shipping_db -e "
INSERT INTO users (id, name, phone, password, city, vehicle_plate, role, is_active) VALUES
(1, 'المدير العام', '0551234567', '\$2y\$10\$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', NULL, 'admin', 1),
(2, 'أحمد السائق', '0509876543', '\$2y\$10\$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', 'أ ب ج 1234', 'driver', 1),
(3, 'خالد العميل', '0550000000', '\$2y\$10\$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', NULL, 'client', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name), is_active=1;
"
"""
run(sql_insert_users)

print("Checking users table now:")
run("mysql -u root -pe250eb38de998d02 shipping_db -e 'SELECT id, name, phone, city, role, is_active FROM users;'")

ssh.close()
