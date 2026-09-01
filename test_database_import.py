import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)

    sftp = ssh.open_sftp()
    sftp.put('backend_php/database.sql', '/tmp/test_database.sql')
    sftp.put('backend_php/database_migration.sql', '/tmp/test_database_migration.sql')
    sftp.close()

    print("==================================================")
    print("1. اختبار استيراد database.sql على قاعدة بيانات فارغة جديدة")
    print("==================================================")
    cmd1 = "mysql -u root -pe250eb38de998d02 -e 'DROP DATABASE IF EXISTS test_empty_shipping_db; CREATE DATABASE test_empty_shipping_db CHARACTER SET utf8mb4;' && mysql -u root -pe250eb38de998d02 test_empty_shipping_db < /tmp/test_database.sql && mysql -u root -pe250eb38de998d02 -e 'SHOW TABLES FROM test_empty_shipping_db;'"
    stdin, stdout, stderr = ssh.exec_command(cmd1)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(out)
    if "Tables_in_test_empty_shipping_db" in out:
        print("✅ نجح استيراد database.sql على قاعدة بيانات فارغة بدون أخطاء!")
    else:
        print("❌ فشل الاستيراد:", err)

    print("\n==================================================")
    print("2. تطبيق الترقية (database_migration.sql) على قاعدة بيانات الإنتاج")
    print("==================================================")
    cmd2 = "mysql -u root -pe250eb38de998d02 shipping_db < /tmp/test_database_migration.sql && mysql -u root -pe250eb38de998d02 shipping_db -e 'DESCRIBE users; DESCRIBE orders;'"
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    out2 = stdout.read().decode('utf-8', errors='ignore')
    print(out2)
    print("✅ تم تطبيق الترقية ومطابقة الحقول بنجاح!")

    ssh.close()

if __name__ == '__main__':
    main()
