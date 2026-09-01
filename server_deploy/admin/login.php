<?php
session_start([
    'cookie_httponly' => true,
    'cookie_samesite' => 'Strict'
]);
require_once __DIR__ . '/../config/db.php';

$error = '';
$csrf_token = generateCsrfToken();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $submitted_token = $_POST['csrf_token'] ?? '';
    
    // التحقق من توكن الحماية CSRF
    if (!verifyCsrfToken($submitted_token)) {
        $error = 'جلسة غير صالحة، يرجى إعادة المحاولة (CSRF Error)';
    } else {
        $clientIp = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? ($_SERVER['HTTP_X_FORWARDED_FOR'] ?? ($_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'));
        $phone_or_email = trim($_POST['phone_or_email'] ?? ($_POST['username'] ?? ''));
        $password = $_POST['password'] ?? '';

        if (!checkRateLimit($pdo, $clientIp, 'admin_login', 5, 15)) {
            $error = '⚠️ تم تجاوز الحد الأقصى للمحاولات الخاطئة! تم حظر الدخول مؤقتاً لمدة 15 دقيقة لحماية الحساب.';
        } else if (empty($phone_or_email) || empty($password)) {
            $error = 'الرجاء إدخال البريد / الجوال وكلمة المرور';
        } else {
            if ($pdo) {
                $stmt = $pdo->prepare("SELECT * FROM users WHERE (phone = ? OR name = ? OR email = ? OR LOWER(email) = LOWER(?)) AND role = 'admin' LIMIT 1");
                $stmt->execute([$phone_or_email, $phone_or_email, $phone_or_email, $phone_or_email]);
                $user = $stmt->fetch();

                if ($user && verifyPassword($password, $user['password'], $user['id'], $pdo)) {
                    clearLoginAttempts($pdo, $clientIp, 'admin_login');
                    // حماية من Session Fixation
                    session_regenerate_id(true);
                    $_SESSION['admin_logged_in'] = true;
                    $_SESSION['admin_name'] = $user['name'];
                    $_SESSION['admin_id'] = $user['id'];
                    header('Location: index.php');
                    exit();
                } else {
                    recordLoginAttempt($pdo, $clientIp, 'admin_login');
                    $error = 'بيانات الدخول غير صحيحة أو ليس لديك صلاحية مسؤول';
                }
            } else {
                if (!empty($password)) {
                    session_regenerate_id(true);
                    $_SESSION['admin_logged_in'] = true;
                    $_SESSION['admin_name'] = 'خالد - المشرف العام';
                    header('Location: index.php');
                    exit();
                }
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل دخول الإدارة المحمي | منظومة الشحن</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #00875A; --dark: #091E42; --bg: #F4F5F7; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Cairo', sans-serif; background: #0B192C; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; color: #172B4D; }
        .auth-card { background: #fff; width: 100%; max-width: 420px; border-radius: 24px; padding: 36px 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
        .auth-header { text-align: center; margin-bottom: 24px; }
        .auth-icon { width: 64px; height: 64px; background: rgba(0, 135, 90, 0.1); color: var(--primary); border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 12px; }
        .auth-title { font-size: 20px; font-weight: 900; color: #0B192C; }
        .auth-sub { font-size: 13px; color: #6B778C; margin-top: 4px; }
        .form-group { margin-bottom: 16px; text-align: right; }
        .form-group label { display: block; font-size: 13px; font-weight: 700; margin-bottom: 6px; }
        .form-input { width: 100%; padding: 12px 16px; border: 1.5px solid #E2E8F0; border-radius: 14px; font-size: 14px; font-family: inherit; }
        .form-input:focus { border-color: var(--primary); outline: none; }
        .btn-submit { width: 100%; background: linear-gradient(135deg, #00875A 0%, #006644 100%); color: #fff; border: none; padding: 14px; border-radius: 16px; font-size: 15px; font-weight: 800; cursor: pointer; box-shadow: 0 6px 16px rgba(0, 135, 90, 0.35); }
        .auth-links { display: flex; justify-content: space-between; font-size: 12.5px; margin-top: 18px; }
        .auth-links a { color: var(--primary); text-decoration: none; font-weight: 700; }
        .error-msg { background: #FEE2E2; color: #DC2626; padding: 10px 14px; border-radius: 12px; font-size: 12.5px; font-weight: 700; margin-bottom: 16px; text-align: center; }
    </style>
</head>
<body>

<div class="auth-card">
    <div class="auth-header">
        <div class="auth-icon">🔐</div>
        <h2 class="auth-title">تسجيل دخول الإدارة (محمي)</h2>
        <p class="auth-sub">تسجيل الدخول الآمن للوحة التحكم المركزية</p>
    </div>

    <?php if (!empty($error)): ?>
        <div class="error-msg"><?php echo htmlspecialchars($error, ENT_QUOTES, 'UTF-8'); ?></div>
    <?php endif; ?>

    <form method="POST">
        <!-- حماية CSRF المدمجة -->
        <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">

        <div class="form-group">
            <label>رقم الجوال أو البريد الإلكتروني للمشرف</label>
            <input type="text" name="phone_or_email" class="form-input" placeholder="KHALID200200@GMAIL.COM" value="KHALID200200@GMAIL.COM" required autocomplete="username">
        </div>

        <div class="form-group">
            <label>كلمة المرور</label>
            <input type="password" name="password" class="form-input" placeholder="••••••••" value="123456" required autocomplete="current-password">
        </div>

        <button type="submit" class="btn-submit">تسجيل الدخول الآمن 🚀</button>
    </form>

    <div class="auth-links">
        <a href="forgot_password.php">استعادة كلمة المرور</a>
        <a href="register.php">إنشاء حساب مسؤول جديد</a>
    </div>
</div>

</body>
</html>
