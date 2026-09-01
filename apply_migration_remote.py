import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)

sftp = ssh.open_sftp()
sftp.put('backend_php/database_migration_v3.sql', '/www/wwwroot/app.sudra.sa/database_migration_v3.sql')
sftp.close()

# 1. Run PHP script to convert legacy base64 to disk files and update orders.image_path
convert_php = """
php -r '
require "/www/wwwroot/app.sudra.sa/config/db.php";
$stmt = $pdo->query("SELECT id, image_path FROM orders WHERE image_path LIKE \"data:image%\"");
$imgDir = "/www/wwwroot/app.sudra.sa/images/orders/";
if (!is_dir($imgDir)) @mkdir($imgDir, 0755, true);
while ($row = $stmt->fetch()) {
    $raw = $row["image_path"];
    if (preg_match("/^data:image\/(\w+);base64,/", $raw, $type)) {
        $data = substr($raw, strpos($raw, ",") + 1);
        $ext = strtolower($type[1]);
        $data = base64_decode($data);
        if ($data !== false) {
            $fileName = "order_" . $row["id"] . "_legacy." . $ext;
            file_put_contents($imgDir . $fileName, $data);
            $url = "https://app.sudra.sa/images/orders/" . $fileName;
            $upd = $pdo->prepare("UPDATE orders SET image_path = ? WHERE id = ?");
            $upd->execute([$url, $row["id"]]);
            echo "Converted order " . $row["id"] . " to $url\\n";
        }
    }
}
'
"""
stdin, stdout, stderr = ssh.exec_command(convert_php)
print("PHP Conversion output:", stdout.read().decode('utf-8'))
print("PHP Conversion stderr:", stderr.read().decode('utf-8'))

# 2. Run SQL migration
cmd = 'mysql -u root -pe250eb38de998d02 shipping_db < /www/wwwroot/app.sudra.sa/database_migration_v3.sql'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Migration stdout:', stdout.read().decode('utf-8'))
print('Migration stderr:', stderr.read().decode('utf-8'))

# 3. Check tables
cmd_check = "mysql -u root -pe250eb38de998d02 shipping_db -e 'SELECT COUNT(*) as total_migrated_images FROM order_images; DESCRIBE password_resets;'"
stdin, stdout, stderr = ssh.exec_command(cmd_check)
print('DB Verification:\n', stdout.read().decode('utf-8'))
ssh.close()
