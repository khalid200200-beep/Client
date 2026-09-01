import paramiko

HOST = "84.247.141.162"
PORT = 22
USER = "root"
PASS = "KkMm1416"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

print("--- Check users table ---")
run("mysql -u root -pe250eb38de998d02 shipping_db -e 'SELECT * FROM users;'")

print("--- Check users structure ---")
run("mysql -u root -pe250eb38de998d02 shipping_db -e 'DESCRIBE users;'")

print("--- Check orders structure ---")
run("mysql -u root -pe250eb38de998d02 shipping_db -e 'DESCRIBE orders;'")

ssh.close()
