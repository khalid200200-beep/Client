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
    print(f">>> {cmd}")
    if out:
        print(out)
    if err:
        print(err)

run("""mysql -u root -pe250eb38de998d02 shipping_db -e "
ALTER TABLE users MODIFY phone VARCHAR(100) NOT NULL;
UPDATE users SET name = 'خالد - المشرف العام', email = 'KHALID200200@GMAIL.COM', phone = 'KHALID200200@GMAIL.COM', password = '\$2y\$10\$wOaA0v1rA8K1pL6Xy2Jgku4bX4J.bZ6F4b5oP7g/Y.vW9bK0Y7F/6', role = 'admin', is_active = 1 WHERE id = 1 OR role = 'admin';
" """)

run("mysql -u root -pe250eb38de998d02 shipping_db -e 'SELECT id, name, email, phone, role FROM users WHERE role=\"admin\";'")

ssh.close()
print("Updated MySQL admin table successfully!")
