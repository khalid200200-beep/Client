import requests
import json
import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

# Let's verify or seed the review accounts on production database via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_query(sql):
    cmd = f'mysql -u shipping_user -p"Ship_SecurePass_2026!#" shipping_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return out, err

print("Checking review accounts in DB:")
out, _ = run_query("SELECT id, name, email, phone, role, is_active FROM users WHERE email IN ('review@sudra.sa', 'driver_review@sudra.sa');")
print(out)

ssh.close()
