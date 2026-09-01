import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=30)

sftp = ssh.open_sftp()

# Copy support.html and privacy.html directly to /www/wwwroot/sudra.sa/public/ and /www/wwwroot/sudra.sa/
with open(r'c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\test_live_urls.py', 'r', encoding='utf-8') as f:
    pass

# Read support.html from app.sudra.sa and write to sudra.sa/public
support_content = sftp.file('/www/wwwroot/app.sudra.sa/support.html').read()
privacy_content = sftp.file('/www/wwwroot/app.sudra.sa/privacy.html').read()

ssh.exec_command('mkdir -p /www/wwwroot/sudra.sa/public')
with sftp.file('/www/wwwroot/sudra.sa/public/support.html', 'wb') as f:
    f.write(support_content)
with sftp.file('/www/wwwroot/sudra.sa/public/privacy.html', 'wb') as f:
    f.write(privacy_content)

# Update sudra.sa nginx config to have fast direct locations for /support and /privacy
nginx_conf = """server
{
    listen 80;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    listen [::]:80;
    server_name sudra.sa www.sudra.sa asudra.com.sa www.asudra.com.sa;
    index index.php index.html index.htm default.php default.htm default.html;
    root /www/wwwroot/sudra.sa;
    include /www/server/panel/vhost/nginx/extension/sudra.sa/*.conf;
    
    #SSL-START
    ssl_certificate    /www/server/panel/vhost/cert/sudra.sa/fullchain.pem;
    ssl_certificate_key    /www/server/panel/vhost/cert/sudra.sa/privkey.pem;
    ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_tickets on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    add_header Strict-Transport-Security "max-age=31536000";
    error_page 497  https://$host$request_uri;
    #SSL-END

    location = /support {
        alias /www/wwwroot/app.sudra.sa/support.html;
        default_type text/html;
    }

    location = /privacy {
        alias /www/wwwroot/app.sudra.sa/privacy.html;
        default_type text/html;
    }

    location / {
        proxy_pass http://127.0.0.1:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~ ^/(\.user.ini|\.htaccess|\.git|\.env|\.svn|\.project|LICENSE|README.md)
    {
        return 404;
    }

    location ~ \.well-known{
        allow all;
    }

    access_log  /www/wwwlogs/sudra.sa.log;
    error_log  /www/wwwlogs/sudra.sa.error.log;
}
"""

with sftp.file('/www/server/panel/vhost/nginx/sudra.sa.conf', 'w') as f:
    f.write(nginx_conf)

sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t && nginx -s reload')
print("Nginx reload:", stdout.read().decode('utf-8'), stderr.read().decode('utf-8'))

ssh.close()
