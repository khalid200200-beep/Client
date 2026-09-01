<?php
session_start();
require_once __DIR__ . '/../config/db.php';

$step = 1;
$msg = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['send_otp'])) {
        $phone = trim($_POST['phone'] ?? '');
        if (empty($phone)) {
            $error = 'الرجاء إدخال رقم الجوال المسجل';
        } else {
            $_SESSION['reset_phone'] = $phone;
            $step = 2;
            $msg = 'تم إرسال رمز التحقق OTP إلى رقم جوالك (رمز تجريبي: 1234)';
        }
    } elseif (isset($_POST['reset_password'])) {
        $otp = trim($_POST['otp'] ?? '');
        $new_pass = trim($_POST['new_password'] ?? '');

        if ($otp !== '1234' && !empty($otp)) {
            $error = 'رمز التحقق غير صحيح';
            $step = 2;
        } elseif (empty($new_pass) || strlen($new_pass) < 6) {
            $error = 'كلمة المرور يجب أن لا تقل عن 6 خانات';
            $step = 2;
        } else {
            $phone = $_SESSION['reset_phone'] ?? '';
            if ($pdo && !empty($phone)) {
                $hash = password_hash($new_pass, PASSWORD_DEFAULT);
                $stmt = $pdo->prepare("UPDATE users SET password = ? WHERE phone = ?");
                $stmt->execute([$hash, $phone]);
            }
            $step = 3;
            $msg = 'تمت إعادة تعيين كلمة المرور بنجاح! يمكنك تسجيل الدخول الآن.';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>استعادة كلمة المرور | منظومة الشحن</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #E51D24; --dark: #1E242B; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background: #0F172A; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; color: var(--dark); }
        .auth-card { background: #fff; width: 100%; max-width: 420px; border-radius: 28px; padding: 32px 28px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); }
        .auth-header { text-align: center; margin-bottom: 24px; }
        .auth-icon { width: 64px; height: 64px; background: rgba(229, 29, 36, 0.1); border-radius: 20px; display: inline-flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 12px; }
        .auth-title { font-size: 22px; font-weight: 900; }
        .auth-sub { font-size: 13px; color: #64748B; margin-top: 4px; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; font-size: 12.5px; font-weight: 700; margin-bottom: 6px; }
        .form-input { width: 100%; padding: 12px 16px; border: 1.5px solid #E2E8F0; border-radius: 14px; font-size: 14px; font-family: inherit; }
        .form-input:focus { border-color: var(--primary); outline: none; }
        .btn-submit { width: 100%; background: linear-gradient(135deg, #FF333A 0%, #D60B12 100%); color: #fff; border: none; padding: 14px; border-radius: 16px; font-size: 15px; font-weight: 800; cursor: pointer; box-shadow: 0 6px 16px rgba(229, 29, 36, 0.35); margin-top: 8px; }
        .auth-links { text-align: center; font-size: 13px; margin-top: 18px; }
        .auth-links a { color: var(--primary); text-decoration: none; font-weight: 700; }
        .error-msg { background: #FEE2E2; color: #DC2626; padding: 10px 14px; border-radius: 12px; font-size: 12.5px; font-weight: 700; margin-bottom: 16px; text-align: center; }
        .success-msg { background: #DCFCE7; color: #16A34A; padding: 10px 14px; border-radius: 12px; font-size: 12.5px; font-weight: 700; margin-bottom: 16px; text-align: center; }
    </style>
</head>
<body>

<div class="auth-card">
    <div class="auth-header">
        <div class="auth-icon">🔑</div>
        <h2 class="auth-title">استعادة كلمة المرور</h2>
        <p class="auth-sub">استرجاع حسابك برمز التحقق OTP</p>
    </div>

    <?php if (!empty($error)): ?>
        <div class="error-msg"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>
    <?php if (!empty($msg)): ?>
        <div class="success-msg"><?php echo htmlspecialchars($msg); ?></div>
    <?php endif; ?>

    <?php if ($step === 1): ?>
        <form method="POST">
            <div class="form-group">
                <label>رقم الجوال المسجل في الحساب</label>
                <input type="text" name="phone" class="form-input" placeholder="05xxxxxxxx" required>
            </div>
            <button type="submit" name="send_otp" class="btn-submit">إرسال رمز التحقق OTP 📲</button>
        </form>
    <?php elseif ($step === 2): ?>
        <form method="POST">
            <div class="form-group">
                <label>رمز التحقق المرسل (OTP)</label>
                <input type="text" name="otp" class="form-input" placeholder="1234" value="1234" required>
            </div>
            <div class="form-group">
                <label>كلمة المرور الجديدة</label>
                <input type="password" name="new_password" class="form-input" placeholder="••••••••" required>
            </div>
            <button type="submit" name="reset_password" class="btn-submit">حفظ كلمة المرور الجديدة 🔒</button>
        </form>
    <?php else: ?>
        <a href="login.php" class="btn-submit" style="display:block; text-align:center; text-decoration:none;">التوجه لتسجيل الدخول 🚀</a>
    <?php endif; ?>

    <div class="auth-links">
        تذكرت كلمة المرور؟ <a href="login.php">تسجيل الدخول</a>
    </div>
</div>

</body>
</html>
