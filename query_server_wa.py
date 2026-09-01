import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)

cmd = """php -r '
require "/www/wwwroot/app.sudra.sa/config/whatsapp.php";
$settings = getWhatsAppSettings();
echo "WhatsApp Settings:\n";
print_r($settings);
echo "\nTesting sendWhatsAppMessage to 966560060938:\n";
$res = sendWhatsAppMessage("966560060938", "🚚 مرحباً بك! هذه رسالة اختبار من منظومة سودرا للشحن والخدمات اللوجستية عبر بوابة Whats-CRM بنجاح ✅");
print_r($res);
'"""

stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')

print("STDOUT:\n", out)
if err:
    print("STDERR:\n", err)

ssh.close()
