import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='Password@123' if False else 'KkMm1416', timeout=10)

cmd = 'mysql -u root -pe250eb38de998d02 -e "USE shipping_db; SELECT id, name, phone, email, password, role FROM users WHERE role=\'admin\';"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Admin Users in Database:")
print(stdout.read().decode('utf-8', errors='ignore'))

# Let's also check if there is an admin user, or set a secure known password if needed
cmd2 = 'mysql -u root -pe250eb38de998d02 -e "USE shipping_db; SELECT id, name, phone, email, role FROM users LIMIT 10;"'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print("All Top Users:")
print(stdout2.read().decode('utf-8', errors='ignore'))

ssh.close()
