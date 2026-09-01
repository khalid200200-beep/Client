import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)

php_debug = """
ini_set('display_errors', '1');
error_reporting(E_ALL);
require_once '/www/wwwroot/app.sudra.sa/config/db.php';

$input = [
    'clientName' => 'عميل تجريبي',
    'clientPhone' => '0912345678',
    'city' => 'الخرطوم',
    'packageCount' => 2,
    'notes' => 'ملاحظات',
    'images' => [
        'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA='
    ]
];

$clientName      = sanitizeInput($input['clientName'] ?? ($input['client_name'] ?? ($input['client'] ?? 'عميل')));
$clientPhone     = sanitizeInput($input['clientPhone'] ?? ($input['client_phone'] ?? ($input['phone'] ?? '')));
$clientId        = intval($input['clientId'] ?? ($input['client_id'] ?? ($input['user_id'] ?? 0)));
$city            = sanitizeInput($input['city'] ?? ($input['pickupCity'] ?? ($input['pickup_city'] ?? 'الخرطوم')));
$pickupAddress   = sanitizeInput($input['pickupAddress'] ?? ($input['pickup_address'] ?? $city));
$deliveryAddress = sanitizeInput($input['deliveryAddress'] ?? ($input['delivery_address'] ?? ($input['deliveryCity'] ?? 'بورتسودان')));
$packageCount    = max(1, intval($input['packageCount'] ?? ($input['package_count'] ?? ($input['count'] ?? 1))));
$notes           = sanitizeInput($input['notes'] ?? '');

$rawImages = $input['images'] ?? [];
$orderCode = 'ORD-' . strtoupper(substr(bin2hex(random_bytes(4)), 0, 6));

try {
    $pdo->beginTransaction();
    $stmt = $pdo->prepare("INSERT INTO orders (order_code, client_id, client_name, client_phone, city, pickup_address, delivery_address, package_count, image_path, notes, status, collected_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0.00)");
    $stmt->execute([$orderCode, ($clientId > 0 ? $clientId : null), $clientName, $clientPhone, $city, $pickupAddress, $deliveryAddress, $packageCount, '', $notes]);
    $orderId = $pdo->lastInsertId();
    echo "Inserted order id: $orderId\\n";

    $imgDir = '/www/wwwroot/app.sudra.sa/images/orders/';
    $savedImageUrls = [];
    $allowedMimes = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp'];

    foreach ($rawImages as $rawImg) {
        if (preg_match('/^data:image\/(\w+);base64,/', $rawImg, $type)) {
            $rawExt = strtolower($type[1]);
            $allowedBaseExts = ['jpeg' => 'jpg', 'jpg' => 'jpg', 'png' => 'png', 'webp' => 'webp'];
            $data = substr($rawImg, strpos($rawImg, ',') + 1);
            $binary = base64_decode($data);

            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mime = finfo_buffer($finfo, $binary);
            finfo_close($finfo);

            echo "Detected MIME: $mime\\n";
            $ext = $allowedBaseExts[$rawExt] ?? 'jpg';
            $fileName = 'order_' . $orderId . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
            $targetPath = $imgDir . $fileName;
            file_put_contents($targetPath, $binary);
            $savedImageUrls[] = 'https://app.sudra.sa/images/orders/' . $fileName;
        }
    }

    $firstImageUrl = !empty($savedImageUrls) ? $savedImageUrls[0] : '';
    if (!empty($savedImageUrls)) {
        $insImg = $pdo->prepare("INSERT INTO order_images (order_id, image_path) VALUES (?, ?)");
        foreach ($savedImageUrls as $url) {
            $insImg->execute([$orderId, $url]);
        }
        $pdo->prepare("UPDATE orders SET image_path = ? WHERE id = ?")->execute([$firstImageUrl, $orderId]);
    }
    $pdo->commit();
    echo "Order created successfully with images: " . json_encode($savedImageUrls) . "\\n";
} catch (Throwable $t) {
    if ($pdo->inTransaction()) $pdo->rollBack();
    echo "ERROR: " . $t->getMessage() . " in " . $t->getFile() . ":" . $t->getLine() . "\\n" . $t->getTraceAsString() . "\\n";
}
"""

sftp = ssh.open_sftp()
with sftp.file('/www/wwwroot/app.sudra.sa/test_order_debug.php', 'w') as f:
    f.write(f"<?php\n{php_debug}")
sftp.close()

stdin, stdout, stderr = ssh.exec_command('php /www/wwwroot/app.sudra.sa/test_order_debug.php')
print("STDOUT:\n", stdout.read().decode('utf-8'))
print("STDERR:\n", stderr.read().decode('utf-8'))

ssh.exec_command('rm -f /www/wwwroot/app.sudra.sa/test_order_debug.php')
ssh.close()
