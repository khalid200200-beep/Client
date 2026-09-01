import paramiko
import sys
import bcrypt

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("84.247.141.162", port=22, username="root", password="KkMm1416", timeout=30)

def exec_sql(sql):
    stdin, stdout, stderr = ssh.exec_command(f'mysql -u root -pe250eb38de998d02 shipping_db -e "{sql}"')
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(out)
    if err and 'Warning' not in err:
        print("ERR:", err)

print("=== 1. Checking columns before ALTER ===")
exec_sql("DESCRIBE orders;")

print("=== 2. Explicit ALTER TABLE for Financial Columns ===")
exec_sql("""
ALTER TABLE orders 
ADD COLUMN delivery_fee DECIMAL(10,2) NOT NULL DEFAULT 25.00,
ADD COLUMN total_amount DECIMAL(10,2) NOT NULL DEFAULT 25.00,
ADD COLUMN commission_amount DECIMAL(10,2) NOT NULL DEFAULT 5.00,
ADD COLUMN driver_earnings DECIMAL(10,2) NOT NULL DEFAULT 20.00,
ADD COLUMN payment_method ENUM('cod', 'card', 'wallet') NOT NULL DEFAULT 'cod',
ADD COLUMN payment_status ENUM('unpaid', 'paid', 'refunded') NOT NULL DEFAULT 'unpaid';
""")

print("=== 3. Checking Users ===")
exec_sql("SELECT id, name, email, phone, role, password FROM users;")

# Ensure Admin user exists with exact email KHALID200200@GMAIL.COM and bcrypt password
hashed = bcrypt.hashpw(b"123456", bcrypt.gensalt(10)).decode('utf-8')
exec_sql(f"""
UPDATE users SET email = 'KHALID200200@GMAIL.COM', password = '{hashed}', role = 'admin' WHERE id = 1 OR role = 'admin' OR email LIKE '%khalid%';
""")

print("=== 4. Verified Users ===")
exec_sql("SELECT id, name, email, phone, role FROM users;")

ssh.close()
