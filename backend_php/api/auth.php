<?php
/**
 * سودرا للشحن والتوصيل - SUDRA EXPRESS
 * وحدة المصادقة والتحقق الآمن (Authentication Controller v3)
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
    // 1. إرسال كود التحقق OTP للتسجيل عبر البريد الإلكتروني
    case 'send_otp':
    case 'send-otp':
        $email      = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $actionType = sanitizeInput($input['type'] ?? ($input['action_type'] ?? 'register'));

        if (!$email) {
            sendJsonResponse(false, 'يرجى إدخال بريد إلكتروني صحيح لاستلام رمز التحقق', null, 400);
        }

        $otpCode = sprintf("%04d", random_int(1000, 9999));

        if ($pdo) {
            $invalidateStmt = $pdo->prepare("UPDATE email_otps SET is_used = 1 WHERE email = ? AND is_used = 0");
            $invalidateStmt->execute([$email]);

            $stmt = $pdo->prepare("INSERT INTO email_otps (email, otp_code, action_type, expires_at) VALUES (?, ?, ?, DATE_ADD(NOW(), INTERVAL 10 MINUTE))");
            $stmt->execute([$email, $otpCode, $actionType]);

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

    // 2. التحقق من رمز OTP المدخل للتسجيل
    case 'verify_otp':
    case 'verify-otp':
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

    // 3. طلب استعادة كلمة المرور (Forgot Password - 6 digits OTP)
    case 'forgot_password':
    case 'forgot-password':
    case 'send_reset_otp':
    case 'send-reset-otp':
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);

        if (!$email) {
            sendJsonResponse(false, 'يرجى إدخال بريد إلكتروني صحيح', null, 400);
        }

        if (!checkRateLimit($pdo, $clientIp, 'forgot_pwd_' . $email, 5, 15)) {
            sendJsonResponse(false, 'تم تجاوز الحد المسموح به لطلبات الاستعادة. يرجى المحاولة بعد 15 دقيقة.', null, 429);
        }

        if ($pdo) {
            $uStmt = $pdo->prepare("SELECT id FROM users WHERE LOWER(email) = LOWER(?) LIMIT 1");
            $uStmt->execute([$email]);
            $user = $uStmt->fetch();

            if ($user) {
                $pdo->prepare("UPDATE password_resets SET is_used = 1 WHERE email = ? AND is_used = 0")->execute([$email]);

                $otpCode = sprintf("%06d", random_int(100000, 999999));
                $otpHash = password_hash($otpCode, PASSWORD_DEFAULT);

                $stmt = $pdo->prepare("INSERT INTO password_resets (email, otp_hash, attempts, is_used, expires_at) VALUES (?, ?, 0, 0, DATE_ADD(NOW(), INTERVAL 10 MINUTE))");
                $stmt->execute([$email, $otpHash]);

                sendOtpEmail($email, $otpCode, 'reset_password');
            }

            recordLoginAttempt($pdo, $clientIp, 'forgot_pwd_' . $email);

            sendJsonResponse(true, 'إذا كان البريد الإلكتروني مسجلاً في النظام، سيصلك رمز التحقق OTP خلال لحظات', [
                'email'      => $email,
                'expires_in' => '10 دقائق'
            ]);
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة حالياً', null, 500);
        }
        break;

    // 4. التحقق من كود الاستعادة (Verify Reset OTP)
    case 'verify_reset_otp':
    case 'verify-reset-otp':
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $otp   = trim($input['otp'] ?? ($input['otp_code'] ?? ''));

        if (empty($email) || empty($otp)) {
            sendJsonResponse(false, 'البريد الإلكتروني ورمز التحقق مطلوبان', null, 400);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("SELECT * FROM password_resets WHERE email = ? AND is_used = 0 AND expires_at >= NOW() AND attempts < 5 ORDER BY id DESC LIMIT 1");
            $stmt->execute([$email]);
            $record = $stmt->fetch();

            if ($record && password_verify($otp, $record['otp_hash'])) {
                $resetToken = bin2hex(random_bytes(32));
                $resetTokenHash = password_hash($resetToken, PASSWORD_DEFAULT);

                $upd = $pdo->prepare("UPDATE password_resets SET reset_token_hash = ?, is_used = 0, expires_at = DATE_ADD(NOW(), INTERVAL 10 MINUTE) WHERE id = ?");
                $upd->execute([$resetTokenHash, $record['id']]);

                sendJsonResponse(true, 'تم التحقق من الرمز بنجاح ✅ يمكنك الآن تعيين كلمة المرور الجديدة', [
                    'email'       => $email,
                    'reset_token' => $resetToken
                ]);
            } else {
                if ($record) {
                    $newAttempts = $record['attempts'] + 1;
                    $isUsedNow = ($newAttempts >= 5) ? 1 : 0;
                    $pdo->prepare("UPDATE password_resets SET attempts = ?, is_used = ? WHERE id = ?")->execute([$newAttempts, $isUsedNow, $record['id']]);
                }
                sendJsonResponse(false, 'رمز التحقق غير صحيح أو انتهت صلاحيته. يرجى طلب رمز جديد.', null, 400);
            }
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة', null, 500);
        }
        break;

    // 5. تعيين كلمة المرور الجديدة (Reset Password)
    case 'reset_password':
    case 'reset-password':
        $email       = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $resetToken  = trim($input['reset_token'] ?? ($input['resetToken'] ?? ($input['token'] ?? '')));
        $password    = $input['password'] ?? ($input['new_password'] ?? ($input['newPassword'] ?? ''));
        $confirmPass = $input['confirm_password'] ?? ($input['confirmPassword'] ?? '');

        if (empty($email) || empty($resetToken) || empty($password)) {
            sendJsonResponse(false, 'جميع الحقول مطلوبة لإعادة تعيين كلمة المرور', null, 400);
        }

        if (strlen($password) < 8) {
            sendJsonResponse(false, 'يجب أن لا تقل كلمة المرور عن 8 أحرف وأرقام للأمان', null, 400);
        }

        if (!empty($confirmPass) && $password !== $confirmPass) {
            sendJsonResponse(false, 'كلمة المرور وتأكيدها غير متطابقين', null, 400);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("SELECT * FROM password_resets WHERE email = ? AND is_used = 0 AND expires_at >= NOW() AND reset_token_hash IS NOT NULL ORDER BY id DESC LIMIT 1");
            $stmt->execute([$email]);
            $record = $stmt->fetch();

            if ($record && password_verify($resetToken, $record['reset_token_hash'])) {
                $hashedPassword = hashPassword($password);
                $updUser = $pdo->prepare("UPDATE users SET password = ? WHERE LOWER(email) = LOWER(?)");
                $updUser->execute([$hashedPassword, $email]);

                $pdo->prepare("UPDATE password_resets SET is_used = 1 WHERE email = ?")->execute([$email]);

                sendJsonResponse(true, 'تم تحديث كلمة المرور بنجاح 🎉 يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة');
            } else {
                sendJsonResponse(false, 'رمز الاستعادة غير صالح أو منتهي الصلاحية. يرجى إعادة المحاولة من جديد.', null, 400);
            }
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة', null, 500);
        }
        break;

    // 6. تسجيل حساب جديد
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

    // 7. تسجيل الدخول بالبريد الإلكتروني أو رقم الجوال
    case 'login':
        $identifier = sanitizeInput(
            $input['identifier'] ?? (
            $input['emailOrPhone'] ?? (
            $input['email_or_phone'] ?? (
            $input['email'] ?? (
            $input['phone'] ?? (
            $input['username'] ?? (
            $input['user'] ?? ''
        )))))));
        $password   = $input['password'] ?? '';

        if (empty($identifier) || empty($password)) {
            sendJsonResponse(false, 'رقم الجوال أو البريد الإلكتروني وكلمة المرور مطلوبان', null, 400);
        }

        if (!checkRateLimit($pdo, $clientIp, 'login', 10, 15)) {
            sendJsonResponse(false, '⚠️ تم تجاوز الحد الأقصى للمحاولات الخاطئة! تم حظر الدخول مؤقتاً لمدة 15 دقيقة.', null, 429);
        }

        if ($pdo) {
            $rawId = trim($identifier);
            $cleanDigits = preg_replace('/[^0-9]/', '', $rawId);
            $altPhone1 = !empty($cleanDigits) ? ltrim($cleanDigits, '0') : $rawId;
            $altPhone2 = !empty($cleanDigits) ? '0' . $altPhone1 : $rawId;

            $stmt = $pdo->prepare("SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR phone = ? OR phone = ? OR phone = ? LIMIT 1");
            $stmt->execute([$rawId, $rawId, $altPhone1, $altPhone2]);
            $user = $stmt->fetch();

            if ($user) {
                $pwdMatches = verifyPassword($password, $user['password'], $user['id'], $pdo);
                if ($pwdMatches) {
                    clearLoginAttempts($pdo, $clientIp, 'login');

                    if ($user['role'] === 'driver' && empty($user['is_active'])) {
                        sendJsonResponse(false, 'حساب السائق قيد المراجعة والاعتماد من قبل الإدارة', [
                            'is_active' => 0
                        ], 403);
                    }

                    if ($user['role'] === 'client' && isset($user['is_active']) && $user['is_active'] == 0) {
                        sendJsonResponse(false, 'تم حظر هذا الحساب من قبل إدارة سودرا. يرجى التواصل مع الدعم الفني.', [
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

    // 8. حذف الحساب والبيانات نهائياً
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
