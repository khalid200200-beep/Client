import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    return out

print("--- TABLES ---")
print(run_cmd("mysql -u root -pe250eb38de998d02 shipping_db -e 'SHOW TABLES;'"))

print("--- USERS ---")
print(run_cmd("mysql -u root -pe250eb38de998d02 shipping_db -e 'DESCRIBE users;'"))

print("--- ORDERS ---")
print(run_cmd("mysql -u root -pe250eb38de998d02 shipping_db -e 'DESCRIBE orders;'"))

print("--- BANNERS ---")
print(run_cmd("mysql -u root -pe250eb38de998d02 shipping_db -e 'DESCRIBE banners;'"))

print("--- NGINX SSL CONFIG ---")
print(run_cmd("cat /www/server/panel/vhost/nginx/app.sudra.sa.conf | head -n 40"))

print("--- PHP-FPM / MEMORY / LOAD ---")
print(run_cmd("uptime; free -m; df -h /"))

ssh.close()
