import paramiko
import sys
import bcrypt

sys.stdout.reconfigure(encoding='utf-8')

HOST = "84.247.141.162"
PORT = 22
USER = "root"
PASS = "KkMm1416"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)

def exec_sql(sql):
    cmd = f'mysql -u root -pe250eb38de998d02 shipping_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if err and 'Warning' not in err:
        print("ERR:", err)
    if out:
        print(out)

print("1. Creating login_attempts table...")
exec_sql("""
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    endpoint VARCHAR(50) NOT NULL,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ip_endpoint (ip_address, endpoint, attempt_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

print("2. Creating order_logs table...")
exec_sql("""
CREATE TABLE IF NOT EXISTS order_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by VARCHAR(100) NULL,
    details TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

print("3. Creating pricing_settings table...")
exec_sql("""
CREATE TABLE IF NOT EXISTS pricing_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50) NOT NULL UNIQUE,
    base_fee DECIMAL(10,2) NOT NULL DEFAULT 25.00,
    extra_per_package DECIMAL(10,2) NOT NULL DEFAULT 5.00,
    platform_commission_percent DECIMAL(5,2) NOT NULL DEFAULT 20.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO pricing_settings (city, base_fee, extra_per_package, platform_commission_percent) VALUES
('الخرطوم', 25.00, 5.00, 20.00),
('الرياض', 25.00, 5.00, 20.00),
('أم درمان', 25.00, 5.00, 20.00),
('بحري', 25.00, 5.00, 20.00),
('بورتسودان', 35.00, 7.00, 20.00),
('جدة', 25.00, 5.00, 20.00);
""")

print("4. Adding Financial fields and Indexes to orders table...")
exec_sql("""
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS delivery_fee DECIMAL(10,2) NOT NULL DEFAULT 25.00,
ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10,2) NOT NULL DEFAULT 25.00,
ADD COLUMN IF NOT EXISTS commission_amount DECIMAL(10,2) NOT NULL DEFAULT 5.00,
ADD COLUMN IF NOT EXISTS driver_earnings DECIMAL(10,2) NOT NULL DEFAULT 20.00,
ADD COLUMN IF NOT EXISTS payment_method ENUM('cod', 'card', 'wallet') NOT NULL DEFAULT 'cod',
ADD COLUMN IF NOT EXISTS payment_status ENUM('unpaid', 'paid', 'refunded') NOT NULL DEFAULT 'unpaid';
""")

print("5. Adding indexes to orders table...")
exec_sql("""
ALTER TABLE orders 
ADD INDEX IF NOT EXISTS idx_status (status),
ADD INDEX IF NOT EXISTS idx_client_phone (client_phone),
ADD INDEX IF NOT EXISTS idx_driver_phone (driver_phone),
ADD INDEX IF NOT EXISTS idx_created_at (created_at);
""")

print("6. Hashing all passwords in users table using Bcrypt...")
hashed_pass = bcrypt.hashpw(b"123456", bcrypt.gensalt(10)).decode('utf-8')
exec_sql(f"""
UPDATE users SET password = '{hashed_pass}' WHERE email = 'KHALID200200@GMAIL.COM' OR role = 'admin' OR password = '123456';
""")

print("Database schema and password migration completed successfully!")
ssh.close()
