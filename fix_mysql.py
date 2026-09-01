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

def run_sql(sql):
    cmd = f'mysql -u root -pe250eb38de998d02 shipping_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(f"SQL: {sql}\nOUT: {out}\nERR: {err}\n")

run_sql("ALTER TABLE users ADD COLUMN vehicle_plate VARCHAR(50) NULL AFTER city;")
run_sql("ALTER TABLE users ADD COLUMN is_active TINYINT(1) DEFAULT 1 AFTER role;")
run_sql("ALTER TABLE orders ADD COLUMN pickup_address VARCHAR(255) NULL AFTER city;")
run_sql("ALTER TABLE orders ADD COLUMN delivery_address VARCHAR(255) NULL AFTER pickup_address;")
run_sql("ALTER TABLE orders ADD COLUMN loaded_at TIMESTAMP NULL AFTER failure_reason;")

run_sql("""INSERT INTO users (id, name, phone, password, city, vehicle_plate, role, is_active) VALUES (1, 'المدير العام', '0551234567', '$2y$10$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', NULL, 'admin', 1) ON DUPLICATE KEY UPDATE name=VALUES(name), is_active=1;""")
run_sql("""INSERT INTO users (id, name, phone, password, city, vehicle_plate, role, is_active) VALUES (2, 'أحمد السائق', '0509876543', '$2y$10$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', 'أ ب ج 1234', 'driver', 1) ON DUPLICATE KEY UPDATE name=VALUES(name), is_active=1;""")
run_sql("""INSERT INTO users (id, name, phone, password, city, vehicle_plate, role, is_active) VALUES (3, 'خالد العميل', '0550000000', '$2y$10$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', 'الرياض', NULL, 'client', 1) ON DUPLICATE KEY UPDATE name=VALUES(name), is_active=1;""")

run_sql("SELECT id, name, phone, city, role, is_active FROM users;")

ssh.close()
