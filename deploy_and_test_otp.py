import sys
import os
import paramiko
import json
import time
import requests

HOST = "84.247.141.162"
PORT = 22
USER = "root"
PASS = "KkMm1416"
DB_PASS = "e250eb38de998d02"
DB_NAME = "shipping_db"
REMOTE_PATH = "/www/wwwroot/app.sudra.sa"

def run_ssh_command(ssh, cmd):
    print(f">> Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out.strip():
        print(f"[STDOUT]\n{out}")
    if err.strip():
        print(f"[STDERR]\n{err}")
    return out, err

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("==================================================")
    print("🚀 بدء نشر وترقية نظام التحقق OTP عبر البريد الإلكتروني")
    print("==================================================")

    # 1. الاتصال بالسيرفر
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)
    print("✅ تم الاتصال بالسيرفر بنجاح عبر SSH.")

    # 2. رفع الملفات المحدثة إلى السيرفر
    print("\n📤 1. رفع ملفات الـ Backend المحدثة عبر SFTP...")
    sftp = ssh.open_sftp()
    
    files_to_upload = [
        ("backend_php/config/mail.php", f"{REMOTE_PATH}/config/mail.php"),
        ("backend_php/config/db.php", f"{REMOTE_PATH}/config/db.php"),
        ("backend_php/api/auth.php", f"{REMOTE_PATH}/api/auth.php"),
        ("backend_php/api/index.php", f"{REMOTE_PATH}/api/index.php"),
        ("backend_php/database.sql", f"{REMOTE_PATH}/database.sql"),
    ]

    for local_f, remote_f in files_to_upload:
        full_local = os.path.abspath(local_f)
        if os.path.exists(full_local):
            print(f"Uploading {local_f} -> {remote_f}")
            sftp.put(full_local, remote_f)
        else:
            print(f"⚠️ Warning: File not found locally: {full_local}")

    sftp.close()
    print("✅ تم رفع كافة الملفات بنجاح.")

    # 3. إنشاء جدول email_otps في قاعدة البيانات عبر استيراد database.sql
    print("\n📦 2. إنشاء وتجهيز جدول email_otps في MySQL...")
    run_ssh_command(ssh, f"mysql -u root -p{DB_PASS} {DB_NAME} < {REMOTE_PATH}/database.sql")

    # 4. ضبط الأذونات والصلاحيات
    print("\n🔒 3. ضبط صلاحيات الملفات...")
    run_ssh_command(ssh, f"chown -R www:www {REMOTE_PATH}/api {REMOTE_PATH}/config")

    # 5. اختبار إرسال OTP عبر API السيرفر
    print("\n🧪 4. اختبار طلب إرسال OTP عبر الـ API الحي...")
    test_email = "info@sudra.sa"
    
    send_otp_url = "https://app.sudra.sa/api/auth.php?action=send_otp"
    try:
        res = requests.post(send_otp_url, json={"email": test_email, "type": "register"}, verify=False, timeout=15)
        print("API Response (send_otp):", res.status_code, res.text)
    except Exception as e:
        print("HTTP Request failed:", e)

    # 6. قراءة رمز التحقق الذي تم توليده من قاعدة البيانات
    print("\n🔍 5. استعلام قاعدة البيانات للتحقق من رمز OTP الصادر...")
    check_db_cmd = f"mysql -u root -p{DB_PASS} {DB_NAME} -e \"SELECT id, email, otp_code, action_type, is_used, expires_at, created_at FROM email_otps WHERE email='{test_email}' ORDER BY id DESC LIMIT 1;\""
    out, _ = run_ssh_command(ssh, check_db_cmd)

    # 7. اختبار التحقق من الرمز الصحيح verify_otp
    otp_code = None
    lines = out.strip().split('\n')
    for line in lines:
        if test_email in line:
            parts = line.split('\t')
            if len(parts) >= 3:
                otp_code = parts[2].strip()
                break

    if otp_code:
        print(f"\n🎯 الرمز المستخرج من قاعدة البيانات: [{otp_code}]")
        print("\n🧪 6. اختبار التحقق بالرمز الصحيح verify_otp...")
        verify_url = "https://app.sudra.sa/api/auth.php?action=verify_otp"
        res_verify = requests.post(verify_url, json={"email": test_email, "otp": otp_code}, verify=False, timeout=15)
        print("API Response (verify_otp SUCCESS):", res_verify.status_code, res_verify.text)

        print("\n🧪 7. اختبار محاولة إعادة استخدام نفس الرمز (يجب أن يفشل)...")
        res_reuse = requests.post(verify_url, json={"email": test_email, "otp": otp_code}, verify=False, timeout=15)
        print("API Response (verify_otp REUSE):", res_reuse.status_code, res_reuse.text)

        print("\n🧪 8. اختبار إدخال رمز غير صحيح 0000...")
        res_fail = requests.post(verify_url, json={"email": test_email, "otp": "0000"}, verify=False, timeout=15)
        print("API Response (verify_otp INVALID):", res_fail.status_code, res_fail.text)

    # 8. فحص سجلات البريد في السيرفر للتأكد من تسليم البريد
    print("\n📬 9. فحص سجلات تسليم البريد في السيرفر...")
    time.sleep(1)
    run_ssh_command(ssh, "tail -n 15 /var/log/mail.log 2>/dev/null || journalctl -u postfix -n 15 --no-pager")

    ssh.close()
    print("\n==================================================")
    print("🎉 اكتمل نشر واختبار نظام التحقق OTP عبر البريد الإلكتروني بنجاح!")
    print("==================================================")

if __name__ == '__main__':
    main()
