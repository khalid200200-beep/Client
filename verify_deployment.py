import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

HOST = "84.247.141.162"
PORT = 22
USER = "root"
PASS = "KkMm1416"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)

def test_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    print(f">>> {cmd}\n{out}\n")

print("--- Testing API Endpoint ---")
test_cmd("curl -k -s https://app.sudra.sa/api/banners.php")

print("--- Testing Admin Page HTTP Status ---")
test_cmd("curl -k -I https://app.sudra.sa/admin/login.php")

print("--- Testing Privacy Policy HTTP Status ---")
test_cmd("curl -k -I https://app.sudra.sa/privacy.html")

print("--- Checking MySQL Tables ---")
test_cmd("mysql -u root -pe250eb38de998d02 -e 'USE shipping_db; SHOW TABLES;'")

ssh.close()
