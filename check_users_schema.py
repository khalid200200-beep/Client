import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_query(sql):
    cmd = f'mysql -u shipping_user -p"Ship_SecurePass_2026!#" shipping_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return out, err

out, err = run_query("DESCRIBE users;")
print("Users table structure:")
print(out)
if err:
    print("Error:", err)

ssh.close()
