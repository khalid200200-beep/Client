import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("84.247.141.162", port=22, username="root", password="KkMm1416", timeout=30)

def exec_sql(sql):
    stdin, stdout, stderr = ssh.exec_command(f'mysql -u root -pe250eb38de998d02 shipping_db -e "{sql}"')
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out)
    if err and 'Warning' not in err:
        print("ERR:", err)

print("1. Adding collected_amount column...")
exec_sql("ALTER TABLE orders ADD COLUMN collected_amount DECIMAL(10,2) NULL DEFAULT 0.00;")

print("2. Verifying orders columns...")
exec_sql("DESCRIBE orders;")

ssh.close()
