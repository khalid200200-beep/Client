import sys
import paramiko
import os

sys.stdout.reconfigure(encoding='utf-8')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)

    # 1. Upload all local php files to a temp directory on the server to check their syntax
    sftp = ssh.open_sftp()
    
    local_php_files = []
    for root_dir in ['backend_php', 'server_deploy']:
        for root, dirs, files in os.walk(root_dir):
            for f in files:
                if f.endswith('.php'):
                    local_php_files.append(os.path.join(root, f))
    
    print(f"Total local PHP files to audit: {len(local_php_files)}")
    ssh.exec_command("mkdir -p /tmp/audit_php")
    
    has_errors = False
    for f in local_php_files:
        remote_dest = f"/tmp/audit_php/{os.path.basename(f)}"
        sftp.put(os.path.abspath(f), remote_dest)
        
        stdin, stdout, stderr = ssh.exec_command(f"php -l {remote_dest}")
        out = stdout.read().decode('utf-8', errors='ignore').strip()
        err = stderr.read().decode('utf-8', errors='ignore').strip()
        
        if "No syntax errors detected" in out:
            print(f"  ✅ {f}: Syntax OK")
        else:
            print(f"  ❌ {f}: {out or err}")
            has_errors = True
            
    sftp.close()
    ssh.close()
    
    if not has_errors:
        print("\n🎉 ALL PHP files passed syntax check with 0 errors!")
    else:
        print("\n⚠️ Syntax errors detected!")

if __name__ == '__main__':
    main()
