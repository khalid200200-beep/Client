<?php
/**
 * سودرا للشحن والتوصيل - SUDRA EXPRESS
 * وحدة المصادقة والتحقق الآمن (Authentication Controller)
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../config/mail.php';

$rawBody = file_get_contents('php://input');
$input = json_decode($rawBody, true) ?? [];
if (empty($input) && !empty($_POST)) {
    $input = $_POST;
}

$action = $_GET['action'] ?? ($input['action'] ?? '');
$clientIp = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? ($_SERVER['HTTP_X_FORWARDED_FOR'] ?? ($_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'));

switch ($action) {
    // 1. إرسال كود التحقق OTP عبر البريد الإلكتروني
    case 'send_otp':
        $email      = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $actionType = sanitizeInput($input['type'] ?? ($input['action_type'] ?? 'register'));

        if (!$email) {
            sendJsonResponse(false, 'يرجى إدخال بريد إلكتروني صحيح لاستلام رمز التحقق', null, 400);
        }

        // توليد كود تحقق عشوائي من 4 أرقام
        $otpCode = sprintf("%04d", random_int(1000, 9999));

        if ($pdo) {
            // إبطال أي رموز سابقة غير مستخدمة لهذا البريد
            $invalidateStmt = $pdo->prepare("UPDATE email_otps SET is_used = 1 WHERE email = ? AND is_used = 0");
            $invalidateStmt->execute([$email]);

            // حفظ الرمز الجديد في قاعدة البيانات بصلاحية 10 دقائق
            $stmt = $pdo->prepare("INSERT INTO email_otps (email, otp_code, action_type, expires_at) VALUES (?, ?, ?, DATE_ADD(NOW(), INTERVAL 10 MINUTE))");
            $stmt->execute([$email, $otpCode, $actionType]);

            // إرسال البريد الإلكتروني الفعلي
            $mailSent = sendOtpEmail($email, $otpCode, $actionType);

            if ($mailSent) {
                sendJsonResponse(true, 'تم إرسال رمز التحقق OTP بنجاح إلى بريدك الإلكتروني', [
                    'email'     => $email,
                    'expires_in'=> '10 دقائق'
                ]);
            } else {
                error_log("Failed to deliver OTP email to: " . $email);
                sendJsonResponse(false, 'تعذر إرسال رمز التحقق إلى بريدك الإلكتروني حالياً. يرجى التحقق من صحة البريد أو المحاولة لاحقاً', null, 500);
            }
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة حالياً', null, 500);
        }
        break;

    // 2. التحقق من رمز OTP المدخل
    case 'verify_otp':
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $phone = sanitizeInput($input['phone'] ?? '');
        $otp   = trim($input['otp'] ?? ($input['otp_code'] ?? ''));

        if (empty($otp) || empty($email)) {
            sendJsonResponse(false, 'البريد الإلكتروني ورمز التحقق مطلوبان', null, 400);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("SELECT id FROM email_otps WHERE email = ? AND otp_code = ? AND is_used = 0 AND expires_at >= NOW() ORDER BY id DESC LIMIT 1");
            $stmt->execute([$email, $otp]);
            $otpRecord = $stmt->fetch();

            if ($otpRecord) {
                $upd = $pdo->prepare("UPDATE email_otps SET is_used = 1 WHERE id = ?");
                $upd->execute([$otpRecord['id']]);

                $secureToken = bin2hex(random_bytes(32));
                sendJsonResponse(true, 'تم التحقق من الرمز بنجاح ✅', [
                    'token' => $secureToken,
                    'email' => $email,
                    'phone' => $phone
                ]);
            } else {
                sendJsonResponse(false, 'رمز التحقق غير صحيح أو انتهت صلاحيته. يرجى طلب رمز جديد.', null, 400);
            }
        } else {
            $secureToken = bin2hex(random_bytes(32));
            sendJsonResponse(true, 'تم التحقق بنجاح', [
                'token' => $secureToken,
                'email' => $email,
                'phone' => $phone
            ]);
        }
        break;

    // 3. تسجيل حساب جديد
    case 'register':
        $name     = sanitizeInput($input['name'] ?? '');
        $email    = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $phone    = sanitizeInput($input['phone'] ?? '');
        $password = $input['password'] ?? '';
        $city     = sanitizeInput($input['city'] ?? 'الخرطوم');
        $role     = in_array($input['role'] ?? '', ['client', 'driver']) ? $input['role'] : 'client';
        $plate    = sanitizeInput($input['vehicle_plate'] ?? ($input['vehiclePlate'] ?? ''));
        $isActive = ($role === 'driver') ? 0 : 1;

        if (empty($name) || empty($phone) || empty($password)) {
            sendJsonResponse(false, 'جميع الحقول الأساسية مطلوبة (الاسم، الجوال، كلمة المرور)', null, 400);
        }

        if (strlen($password) < 6) {
            sendJsonResponse(false, 'كلمة المرور يجب أن لا تقل عن 6 خانات', null, 400);
        }

        if ($pdo) {
            if ($email) {
                $stmt = $pdo->prepare("SELECT id FROM users WHERE LOWER(email) = LOWER(?)");
                $stmt->execute([$email]);
                if ($stmt->fetch()) {
                    sendJsonResponse(false, 'البريد الإلكتروني مسجل مسبقاً في النظام', null, 409);
                }
            }

            $stmt = $pdo->prepare("SELECT id FROM users WHERE phone = ?");
            $stmt->execute([$phone]);
            if ($stmt->fetch()) {
                sendJsonResponse(false, 'رقم الجوال مسجل مسبقاً في النظام', null, 409);
            }

            $hashedPassword = hashPassword($password);
            $stmt = $pdo->prepare("INSERT INTO users (name, email, phone, password, city, vehicle_plate, role, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
            $stmt->execute([$name, $email, $phone, $hashedPassword, $city, $plate, $role, $isActive]);
            $userId = $pdo->lastInsertId();

            $token = bin2hex(random_bytes(32));
            sendJsonResponse(true, 'تم إنشاء الحساب بنجاح 🎉', [
                'token'     => $token,
                'user_id'   => $userId,
                'id'        => $userId,
                'name'      => $name,
                'email'     => $email,
                'phone'     => $phone,
                'city'      => $city,
                'role'      => $role,
                'is_active' => $isActive
            ], 201);
        } else {
            sendJsonResponse(true, 'تم إنشاء الحساب بنجاح (وضع المعاينة)', [
                'token'     => 'preview-token-99',
                'user_id'   => 99,
                'id'        => 99,
                'name'      => $name,
                'email'     => $email,
                'phone'     => $phone,
                'city'      => $city,
                'role'      => $role,
                'is_active' => $isActive
            ], 201);
        }
        break;

    // 4. تسجيل الدخول
    case 'login':
        $identifier = sanitizeInput($input['email'] ?? ($input['phone'] ?? ($input['username'] ?? '')));
        $password   = $input['password'] ?? '';

        if (empty($identifier) || empty($password)) {
            sendJsonResponse(false, 'رقم الجوال أو البريد الإلكتروني وكلمة المرور مطلوبان', null, 400);
        }

        if (!checkRateLimit($pdo, $clientIp, 'login', 10, 15)) {
            sendJsonResponse(false, '⚠️ تم تجاوز الحد الأقصى للمحاولات الخاطئة! تم حظر الدخول مؤقتاً لمدة 15 دقيقة.', null, 429);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR phone = ? LIMIT 1");
            $stmt->execute([$identifier, $identifier]);
            $user = $stmt->fetch();

            if ($user) {
                // التحقق الحصري من كلمة المرور المشفرة فقط دون أي تجاوزات
                $pwdMatches = verifyPassword($password, $user['password'], $user['id'], $pdo);
                if ($pwdMatches) {
                    clearLoginAttempts($pdo, $clientIp, 'login');

                    if ($user['role'] === 'driver' && empty($user['is_active'])) {
                        sendJsonResponse(false, 'حساب السائق قيد المراجعة والاعتماد من قبل الإدارة', [
                            'is_active' => 0
                        ], 403);
                    }

                    $token = bin2hex(random_bytes(32));
                    sendJsonResponse(true, 'تم تسجيل الدخول بنجاح', [
                        'token'     => $token,
                        'user_id'   => $user['id'],
                        'id'        => $user['id'],
                        'name'      => $user['name'],
                        'email'     => $user['email'] ?? '',
                        'phone'     => $user['phone'],
                        'city'      => $user['city'],
                        'role'      => $user['role'],
                        'is_active' => (int)$user['is_active']
                    ]);
                }
            }

            recordLoginAttempt($pdo, $clientIp, 'login');
            sendJsonResponse(false, 'بيانات الدخول غير صحيحة', null, 401);
        } else {
            sendJsonResponse(true, 'تم تسجيل الدخول بنجاح (وضع المعاينة)', [
                'token'   => 'preview-demo-token-12345',
                'name'    => 'مستخدم تجريبي',
                'phone'   => $identifier,
                'city'    => 'الخرطوم',
                'role'    => 'client'
            ]);
        }
        break;

    // 5. حذف الحساب والبيانات نهائياً
    case 'delete_account':
        $userId = intval($input['user_id'] ?? 0);
        $phone  = sanitizeInput($input['phone'] ?? '');

        if ($pdo && ($userId > 0 || !empty($phone))) {
            if ($userId > 0) {
                $stmt = $pdo->prepare("DELETE FROM users WHERE id = ?");
                $stmt->execute([$userId]);
            } else {
                $stmt = $pdo->prepare("DELETE FROM users WHERE phone = ?");
                $stmt->execute([$phone]);
            }
            sendJsonResponse(true, 'تم حذف حسابك وكافة البيانات المرتبطة به بنجاح وفق متطلبات الخصوصية');
        } else {
            sendJsonResponse(false, 'معرف المستخدم أو رقم الهاتف مطلوب', null, 400);
        }
        break;

    default:
        sendJsonResponse(false, 'إجراء غير معروف في مسار المصادقة', null, 404);
}
