<?php
/**
 * سودرا للشحن والتوصيل - SUDRA EXPRESS
 * إعدادات الاتصال بقاعدة البيانات والحماية الصارمة
 */

// 1. كتم أخطاء HTML ومعالج الأخطاء المركزي الموحد للاستجابة بصيغة JSON
error_reporting(E_ALL & ~E_DEPRECATED & ~E_STRICT);
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

set_exception_handler(function($e) {
    sendJsonResponse(false, 'حدث خطأ في معالجة الطلب على الخادم', [
        'error_type' => 'ServerException'
    ], 500);
});

set_error_handler(function($errno, $errstr, $errfile, $errline) {
    if (!(error_reporting() & $errno)) return false;
    error_log("PHP Error [$errno]: $errstr in $errfile on line $errline");
    return true;
});

// 2. ترويسات الأمان السيبراني (HTTP Security Headers)
header('X-Frame-Options: SAMEORIGIN');
header('X-Content-Type-Options: nosniff');
header('X-XSS-Protection: 1; mode=block');
header('Referrer-Policy: strict-origin-when-cross-origin');

// 3. ترويسات CORS المدارة
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, X-CSRF-Token');
header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// 4. قراءة إعدادات البيئة
$db_host = getenv('DB_HOST') ?: '127.0.0.1';
$db_user = getenv('DB_USER') ?: 'root';
$db_pass = getenv('DB_PASS') ?: 'e250eb38de998d02';
$db_name = getenv('DB_NAME') ?: 'shipping_db';

try {
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8mb4", $db_user, $db_pass, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false, // الحماية الصارمة من SQL Injection
    ]);
} catch (PDOException $e) {
    error_log("Database Connection Error: " . $e->getMessage());
    $pdo = null;
}

require_once __DIR__ . '/mail.php';

/**
 * دالة تعقيم وتطهير المدخلات من نصوص XSS الخبيثة
 */
function sanitizeInput($data) {
    if (is_array($data)) {
        return array_map('sanitizeInput', $data);
    }
    return htmlspecialchars(trim($data ?? ''), ENT_QUOTES, 'UTF-8');
}

/**
 * دالة التحقق من صحة رقم الجوال
 */
function isValidPhone($phone) {
    $p = preg_replace('/[^0-9]/', '', $phone);
    return strlen($p) >= 9 && strlen($p) <= 15;
}

/**
 * دالة تشفير كلمات المرور باستخدام Bcrypt
 */
function hashPassword($password) {
    return password_hash($password, PASSWORD_BCRYPT, ['cost' => 10]);
}

/**
 * دالة مطابقة وفحص كلمة المرور المعتمدة فقط على التشفير بدون أي كلمات مرور ثابتة
 */
function verifyPassword($plainPassword, $hashedPassword, $userId = null, $pdo = null) {
    if (empty($hashedPassword) || empty($plainPassword)) return false;

    // التحقق المشفر الرسمي
    if (password_verify($plainPassword, $hashedPassword)) {
        if ($pdo && $userId && password_needs_rehash($hashedPassword, PASSWORD_BCRYPT)) {
            $newHash = hashPassword($plainPassword);
            $stmt = $pdo->prepare("UPDATE users SET password = ? WHERE id = ?");
            $stmt->execute([$newHash, $userId]);
        }
        return true;
    }

    return false;
}

/**
 * نظام حماية تسجيل الدخول من هجمات التخمين Rate Limiter
 */
function checkRateLimit($pdo, $ip, $endpoint = 'login', $maxAttempts = 10, $decayMinutes = 15) {
    if (!$pdo) return true;
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM login_attempts WHERE ip_address = ? AND endpoint = ? AND attempt_time > (NOW() - INTERVAL ? MINUTE)");
        $stmt->execute([$ip, $endpoint, $decayMinutes]);
        $attempts = $stmt->fetchColumn();
        return $attempts < $maxAttempts;
    } catch (Exception $e) {
        return true;
    }
}

function recordLoginAttempt($pdo, $ip, $endpoint = 'login') {
    if (!$pdo) return;
    try {
        $stmt = $pdo->prepare("INSERT INTO login_attempts (ip_address, endpoint, attempt_time) VALUES (?, ?, NOW())");
        $stmt->execute([$ip, $endpoint]);
    } catch (Exception $e) {}
}

function clearLoginAttempts($pdo, $ip, $endpoint = 'login') {
    if (!$pdo) return;
    try {
        $stmt = $pdo->prepare("DELETE FROM login_attempts WHERE ip_address = ? AND endpoint = ?");
        $stmt->execute([$ip, $endpoint]);
    } catch (Exception $e) {}
}

/**
 * توليد وفحص رمز الحماية من تزوير الطلبات CSRF Token
 */
function generateCsrfToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function verifyCsrfToken($token) {
    if (empty($_SESSION['csrf_token']) || empty($token)) {
        return false;
    }
    return hash_equals($_SESSION['csrf_token'], $token);
}

/**
 * إرجاع استجابة JSON موحدة ونظيفة
 */
function sendJsonResponse($status, $message, $data = null, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'success'   => (bool)$status,
        'message'   => $message,
        'data'      => $data,
        'timestamp' => time()
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit();
}
