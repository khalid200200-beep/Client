import sys
import paramiko
import os

sys.stdout.reconfigure(encoding='utf-8')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)

    sftp = ssh.open_sftp()
    remote_base = "/www/wwwroot/app.sudra.sa"

    files_to_sync = [
        ("backend_php/config/db.php", f"{remote_base}/config/db.php"),
        ("backend_php/config/mail.php", f"{remote_base}/config/mail.php"),
        ("backend_php/api/index.php", f"{remote_base}/api/index.php"),
        ("backend_php/api/auth.php", f"{remote_base}/api/auth.php"),
        ("backend_php/api/orders.php", f"{remote_base}/api/orders.php"),
        ("backend_php/api/banners.php", f"{remote_base}/api/banners.php"),
        ("backend_php/database.sql", f"{remote_base}/database.sql"),
        ("backend_php/database_migration.sql", f"{remote_base}/database_migration.sql"),
        ("backend_php/.env.example", f"{remote_base}/.env.example"),
    ]

    for local, remote in files_to_sync:
        print(f"Uploading {local} -> {remote}")
        sftp.put(local, remote)

    sftp.close()

    # Fix permissions and reload nginx & php-fpm
    cmd = """
    chown -R www:www /www/wwwroot/app.sudra.sa/api /www/wwwroot/app.sudra.sa/config /www/wwwroot/app.sudra.sa/admin
    systemctl reload nginx
    systemctl reload php-fpm-82 || systemctl reload php-fpm || true
    """
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    print("✅ Successfully deployed updated Backend files to live server (app.sudra.sa)!")
    ssh.close()

if __name__ == '__main__':
    main()
