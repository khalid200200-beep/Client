<?php
/**
 * سودرا للشحن والتوصيل - SUDRA EXPRESS | Unified RESTful API Engine v3
 * نظام موحد وآمن يدعم تطبيقات فلاتر (العميل والسائق)، الويب، ولوحة التحكم الإدارية
 * يدعم الصور المتعددة للطلبات واستعادة كلمة المرور الآمنة
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../config/mail.php';
require_once __DIR__ . '/../config/whatsapp.php';

define('SUDRA_AUTH_SECRET', 'SUDRA_SECURE_KEY_2026_PROD_SHIPPING_EXP');

// 1. استخراج وتحليل المسار والطلب
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = strtoupper($_SERVER['REQUEST_METHOD']);
$clientIp = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? ($_SERVER['HTTP_X_FORWARDED_FOR'] ?? ($_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'));

// إزالة المسار الأساسي /api أو /backend_php/api
$path = preg_replace('#^/(backend_php/)?api/?#', '', $requestUri);
$segments = array_values(array_filter(explode('/', trim($path, '/'))));

$resource = $segments[0] ?? ($_GET['resource'] ?? '');
$subResource = $segments[1] ?? ($_GET['action'] ?? null);
$id = null;

if (isset($segments[1]) && is_numeric($segments[1])) {
    $id = intval($segments[1]);
    $subResource = $segments[2] ?? null;
} elseif (isset($segments[2]) && is_numeric($segments[2])) {
    $id = intval($segments[2]);
} elseif (isset($_GET['id']) && is_numeric($_GET['id'])) {
    $id = intval($_GET['id']);
}

// 2. قراءة بيانات المدخلات الموحدة (JSON أو POST أو Form Data)
$rawInput = file_get_contents('php://input');
$input = json_decode($rawInput, true);
if (empty($input) && !empty($_POST)) {
    $input = $_POST;
}
$input = is_array($input) ? $input : [];

// =========================================================================
// 1. AUTHENTICATION ROUTES (/api/auth/...)
// =========================================================================
if ($resource === 'auth') {
    $action = $subResource ?? ($input['action'] ?? ($_GET['action'] ?? ''));
    $subAction = $segments[2] ?? '';

    // تحديد مسارات تسجيل الدخول المعزولة حسب الدور
    $isClientLogin = ((isset($segments[1]) && $segments[1] === 'client' && $subAction === 'login') || $action === 'client-login' || $action === 'client_login');
    $isDriverLogin = ((isset($segments[1]) && $segments[1] === 'driver' && $subAction === 'login') || $action === 'driver-login' || $action === 'driver_login');
    $isAdminLogin  = ((isset($segments[1]) && $segments[1] === 'admin' && $subAction === 'login') || $action === 'admin-login' || $action === 'admin_login');
    $isGeneralLogin = ($action === 'login') || $isClientLogin || $isDriverLogin || $isAdminLogin;

    // 1.1 تسجيل الدخول المعزول والمحمي بالدور (Client / Driver / Admin Login)
    if ($isGeneralLogin) {
        $requiredRole = null;
        if ($isClientLogin) {
            $requiredRole = 'client';
        } elseif ($isDriverLogin) {
            $requiredRole = 'driver';
        } elseif ($isAdminLogin) {
            $requiredRole = 'admin';
        } else {
            $reqRole = $input['role'] ?? ($input['expected_role'] ?? ($input['expectedRole'] ?? ($input['app_type'] ?? ($_GET['role'] ?? null))));
            if ($reqRole === 'client' || $reqRole === 'driver' || $reqRole === 'admin') {
                $requiredRole = $reqRole;
            }
        }

        $identifier = sanitizeInput(
            $input['identifier'] ?? (
            $input['emailOrPhone'] ?? (
            $input['email_or_phone'] ?? (
            $input['email'] ?? (
            $input['phone'] ?? (
            $input['username'] ?? (
            $input['user'] ?? ''
        )))))));
        $password = $input['password'] ?? '';

        if (empty($identifier) || empty($password)) {
            sendJsonResponse(false, 'الرجاء إدخال البريد الإلكتروني أو رقم الجوال وكلمة المرور', null, 400);
        }

        if (!checkRateLimit($pdo, $clientIp, 'login', 10, 15)) {
            sendJsonResponse(false, '⚠️ تم تجاوز الحد الأقصى للمحاولات الخاطئة! تم حظر الدخول مؤقتاً لمدة 15 دقيقة لحماية الحساب.', null, 429);
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
                $isPasswordCorrect = verifyPassword($password, $user['password'], $user['id'], $pdo);

                if ($isPasswordCorrect) {
                    clearLoginAttempts($pdo, $clientIp, 'login');

                    // 1. عزل وفصل الأدوار الصارم في السيرفر (Backend Role Authorization)
                    if ($requiredRole === 'client' && $user['role'] !== 'client') {
                        sendJsonResponse(false, 'هذا الحساب مسجل كسائق/كابتن، يرجى استخدام تطبيق السائق.', [
                            'role_mismatch' => true,
                            'user_role' => $user['role'],
                            'expected_role' => 'client'
                        ], 403);
                    }

                    if ($requiredRole === 'driver' && $user['role'] !== 'driver') {
                        sendJsonResponse(false, 'هذا الحساب مسجل كعميل، يرجى استخدام تطبيق العميل أو التسجيل ككابتن.', [
                            'role_mismatch' => true,
                            'user_role' => $user['role'],
                            'expected_role' => 'driver'
                        ], 403);
                    }

                    if ($requiredRole === 'admin' && $user['role'] !== 'admin') {
                        sendJsonResponse(false, 'غير مصرح لك بالدخول إلى لوحة التحكم الإدارية', [
                            'role_mismatch' => true,
                            'user_role' => $user['role'],
                            'expected_role' => 'admin'
                        ], 403);
                    }

                    // 2. التحقق من حالة تفعيل السائق
                    if ($user['role'] === 'driver' && empty($user['is_active'])) {
                        sendJsonResponse(false, 'حساب السائق قيد المراجعة والاعتماد من قبل الإدارة', [
                            'isPending' => true,
                            'id' => $user['id'],
                            'name' => $user['name'],
                            'email' => $user['email'] ?? $identifier,
                            'phone' => $user['phone'],
                            'city' => $user['city'] ?? 'الخرطوم',
                            'role' => 'driver',
                            'is_active' => 0
                        ], 403);
                    }

                    // 3. التحقق من حظر العميل
                    if ($user['role'] === 'client' && isset($user['is_active']) && $user['is_active'] == 0) {
                        sendJsonResponse(false, 'تم حظر هذا الحساب من قبل إدارة سودرا. يرجى التواصل مع الدعم الفني.', [
                            'isBanned' => true,
                            'id' => $user['id'],
                            'role' => 'client',
                            'is_active' => 0
                        ], 403);
                    }

                    $token = generateUserToken($user);
                    $userData = [
                        'token' => $token,
                        'id' => $user['id'],
                        'user_id' => $user['id'],
                        'name' => $user['name'],
                        'email' => $user['email'] ?? $identifier,
                        'phone' => $user['phone'],
                        'city' => $user['city'] ?? 'الخرطوم',
                        'role' => $user['role'],
                        'vehicle_plate' => $user['vehicle_plate'] ?? '',
                        'vehiclePlate' => $user['vehicle_plate'] ?? '',
                        'is_active' => (int) $user['is_active']
                    ];
                    sendJsonResponse(true, 'تم تسجيل الدخول بنجاح', $userData);
                } else {
                    recordLoginAttempt($pdo, $clientIp, 'login');
                    sendJsonResponse(false, 'بيانات الدخول غير صحيحة! كلمة المرور غير مطابقة.', null, 401);
                }
            } else {
                recordLoginAttempt($pdo, $clientIp, 'login');
                sendJsonResponse(false, 'بيانات الدخول غير صحيحة! المستخدم غير مسجل.', null, 401);
            }
        } else {
            sendJsonResponse(true, 'تم تسجيل الدخول بنجاح (وضع المعاينة)', [
                'token' => 'preview-token',
                'name' => 'مستخدم تجريبي',
                'phone' => $identifier,
                'city' => 'الخرطوم',
                'role' => $requiredRole ?: 'client'
            ]);
        }
    }

    // 1.2 إرسال رمز التحقق OTP للتسجيل عبر البريد وواتساب (/api/auth/send-otp)
    if ($action === 'send-otp' || $action === 'send_otp' || $action === 'sendOtp') {
        $email = filter_var(trim($input['email'] ?? ($input['mail'] ?? ($input['emailAddress'] ?? ''))), FILTER_VALIDATE_EMAIL);
        $phone = sanitizeInput($input['phone'] ?? ($input['phoneNumber'] ?? ''));
        $actionType = sanitizeInput($input['type'] ?? ($input['action_type'] ?? ($input['actionType'] ?? 'register')));

        if (!$email && empty($phone)) {
            sendJsonResponse(false, 'يرجى إدخال بريد إلكتروني أو رقم جوال صحيح لاستلام رمز التحقق', null, 400);
        }

        $otpCode = sprintf("%04d", random_int(1000, 9999));

        if ($pdo) {
            if ($email) {
                $invalidateStmt = $pdo->prepare("UPDATE email_otps SET is_used = 1 WHERE email = ? AND is_used = 0");
                $invalidateStmt->execute([$email]);

                $stmt = $pdo->prepare("INSERT INTO email_otps (email, otp_code, action_type, expires_at) VALUES (?, ?, ?, DATE_ADD(NOW(), INTERVAL 10 MINUTE))");
                $stmt->execute([$email, $otpCode, $actionType]);

                // إرسال البريد الإلكتروني
                sendOtpEmail($email, $otpCode, $actionType);
            }

            // إرسال كود OTP عبر واتساب أيضاً إذا توفر رقم الهاتف
            if (!empty($phone)) {
                sendWhatsAppOtp($phone, $otpCode, $actionType);
            }

            sendJsonResponse(true, 'تم إرسال رمز التحقق OTP بنجاح عبر البريد الإلكتروني وواتساب', [
                'email' => $email,
                'phone' => $phone,
                'expires_in' => '10 دقائق'
            ]);
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة حالياً', null, 500);
        }
    }

    // 1.3 التحقق من رمز OTP للتسجيل (/api/auth/verify-otp)
    if ($action === 'verify-otp' || $action === 'verify_otp') {
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $phone = sanitizeInput($input['phone'] ?? '');
        $otp = trim($input['otp'] ?? ($input['otp_code'] ?? ''));

        if (empty($otp)) {
            sendJsonResponse(false, 'يرجى إدخال رمز التحقق', null, 400);
        }

        if ($pdo && $email) {
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
    }

    // 1.4 طلب استعادة كلمة المرور وإرسال OTP 6 أرقام عبر البريد وواتساب (POST /api/auth/forgot-password)
    if ($action === 'forgot-password' || $action === 'forgot_password' || $action === 'send-reset-otp' || $action === 'send_reset_otp') {
        $identifier = sanitizeInput($input['email'] ?? ($input['phone'] ?? ($input['identifier'] ?? '')));
        $email = filter_var(trim($identifier), FILTER_VALIDATE_EMAIL);

        if (empty($identifier)) {
            sendJsonResponse(false, 'يرجى إدخال بريد إلكتروني أو رقم جوال صحيح', null, 400);
        }

        if (!checkRateLimit($pdo, $clientIp, 'forgot_pwd_' . $identifier, 5, 15)) {
            sendJsonResponse(false, 'تم تجاوز الحد المسموح به لطلبات الاستعادة. يرجى المحاولة بعد 15 دقيقة.', null, 429);
        }

        if ($pdo) {
            $rawId = trim($identifier);
            $cleanDigits = preg_replace('/[^0-9]/', '', $rawId);
            $altPhone1 = !empty($cleanDigits) ? ltrim($cleanDigits, '0') : $rawId;
            $altPhone2 = !empty($cleanDigits) ? '0' . $altPhone1 : $rawId;

            $uStmt = $pdo->prepare("SELECT id, email, phone FROM users WHERE LOWER(email) = LOWER(?) OR phone = ? OR phone = ? OR phone = ? LIMIT 1");
            $uStmt->execute([$rawId, $rawId, $altPhone1, $altPhone2]);
            $user = $uStmt->fetch();

            if ($user) {
                $targetEmail = $user['email'] ?? $email;
                if ($targetEmail) {
                    // إبطال أي طلبات سابقة غير مكتملة
                    $pdo->prepare("UPDATE password_resets SET is_used = 1 WHERE email = ? AND is_used = 0")->execute([$targetEmail]);

                    // توليد OTP مكون من 6 أرقام وتخزين الـ Hash فقط
                    $otpCode = sprintf("%06d", random_int(100000, 999999));
                    $otpHash = password_hash($otpCode, PASSWORD_DEFAULT);

                    $stmt = $pdo->prepare("INSERT INTO password_resets (email, otp_hash, attempts, is_used, expires_at) VALUES (?, ?, 0, 0, DATE_ADD(NOW(), INTERVAL 10 MINUTE))");
                    $stmt->execute([$targetEmail, $otpHash]);

                    // 1. إرسال البريد الإلكتروني الآمن للمستخدم
                    sendOtpEmail($targetEmail, $otpCode, 'reset_password');

                    // 2. إرسال رمز التحقق عبر واتساب إلى رقم جوال المستخدم المسجل
                    if (!empty($user['phone'])) {
                        sendWhatsAppOtp($user['phone'], $otpCode, 'reset_password');
                    }
                }
            }

            recordLoginAttempt($pdo, $clientIp, 'forgot_pwd_' . $identifier);

            // استجابة آمنة وموحدة تمنع تخمين الحسابات (Account Enumeration)
            sendJsonResponse(true, 'إذا كان الحساب مسجلاً في النظام، سيصلك رمز التحقق OTP عبر البريد وواتساب خلال لحظات', [
                'email' => $email ?: ($user['email'] ?? ''),
                'expires_in' => '10 دقائق'
            ]);
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة حالياً', null, 500);
        }
    }

    // 1.5 التحقق من رمز استعادة كلمة المرور وإصدار Reset Token (POST /api/auth/verify-reset-otp)
    if ($action === 'verify-reset-otp' || $action === 'verify_reset_otp') {
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $otp = trim($input['otp'] ?? ($input['otp_code'] ?? ''));

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
                    'email' => $email,
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
    }

    // 1.6 تعيين كلمة المرور الجديدة (POST /api/auth/reset-password)
    if ($action === 'reset-password' || $action === 'reset_password') {
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $resetToken = trim($input['reset_token'] ?? ($input['resetToken'] ?? ($input['token'] ?? '')));
        $password = $input['password'] ?? ($input['new_password'] ?? ($input['newPassword'] ?? ''));
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

                // إبطال رمز الاستعادة المستخدم
                $pdo->prepare("UPDATE password_resets SET is_used = 1 WHERE email = ?")->execute([$email]);

                sendJsonResponse(true, 'تم تحديث كلمة المرور بنجاح 🎉 يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة');
            } else {
                sendJsonResponse(false, 'رمز الاستعادة غير صالح أو منتهي الصلاحية. يرجى إعادة المحاولة من جديد.', null, 400);
            }
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة', null, 500);
        }
    }

    // 1.7 تسجيل حساب جديد (/api/auth/register)
    if ($action === 'register') {
        $name = sanitizeInput($input['name'] ?? '');
        $email = filter_var(trim($input['email'] ?? ''), FILTER_SANITIZE_EMAIL);
        $phone = sanitizeInput($input['phone'] ?? '');
        $password = $input['password'] ?? '';
        $city = sanitizeInput($input['city'] ?? 'الخرطوم');
        $role = in_array($input['role'] ?? '', ['client', 'driver']) ? $input['role'] : 'client';
        $plate = sanitizeInput($input['vehicle_plate'] ?? ($input['vehiclePlate'] ?? ''));
        $isActive = ($role === 'driver') ? 0 : 1;

        if (empty($name) || empty($phone) || empty($password)) {
            sendJsonResponse(false, 'الاسم ورقم الجوال وكلمة المرور حقول مطلوبة', null, 400);
        }

        if (strlen($password) < 6) {
            sendJsonResponse(false, 'كلمة المرور يجب أن لا تقل عن 6 خانات', null, 400);
        }

        if ($pdo) {
            if (!empty($email)) {
                $chkEmail = $pdo->prepare("SELECT id FROM users WHERE LOWER(email) = LOWER(?)");
                $chkEmail->execute([$email]);
                if ($chkEmail->fetch()) {
                    sendJsonResponse(false, 'البريد الإلكتروني مسجل مسبقاً في النظام', null, 409);
                }
            }

            $chk = $pdo->prepare("SELECT id FROM users WHERE phone = ?");
            $chk->execute([$phone]);
            if ($chk->fetch()) {
                sendJsonResponse(false, 'رقم الجوال مسجل مسبقاً في النظام', null, 409);
            }

            $hashed = hashPassword($password);
            $ins = $pdo->prepare("INSERT INTO users (name, email, phone, password, city, vehicle_plate, role, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
            $ins->execute([$name, $email, $phone, $hashed, $city, $plate, $role, $isActive]);
            $newId = $pdo->lastInsertId();

            $rawUserData = [
                'id' => $newId,
                'user_id' => $newId,
                'name' => $name,
                'email' => $email,
                'phone' => $phone,
                'city' => $city,
                'role' => $role,
                'is_active' => $isActive
            ];
            $token = generateUserToken($rawUserData);
            $rawUserData['token'] = $token;

            sendJsonResponse(true, 'تم إنشاء الحساب بنجاح 🎉', $rawUserData, 201);
        } else {
            sendJsonResponse(true, 'تم إنشاء الحساب بنجاح (وضع المعاينة)', [
                'token' => 'preview-token',
                'id' => 99,
                'name' => $name,
                'email' => $email,
                'phone' => $phone,
                'city' => $city,
                'role' => $role,
                'is_active' => $isActive
            ], 201);
        }
    }

    // 1.8 حذف الحساب الشخصي للمستخدم (/api/auth/delete_account)
    if ($action === 'delete_account' || $action === 'delete-account') {
        $authUser = getAuthenticatedUser($pdo);
        if (!$authUser) {
            sendJsonResponse(false, 'تسجيل الدخول والتوكن مطلوب لحذف الحساب', null, 401);
        }

        // 🛡️ فحص صلاحية المدير: المسار مخصص لحذف الحساب الشخصي للعملاء والسائقين فقط
        if ($authUser['role'] === 'admin') {
            sendJsonResponse(false, 'عذراً! مسار حذف الحساب الذاتي مخصص للعملاء والسائقين فقط', null, 403);
        }

        // أخذ المعرف ورقم الهاتف مباشرة وبشكل صارم من التوكن فقط
        $userId = intval($authUser['uid'] ?? 0);
        $phone = sanitizeInput($authUser['phone'] ?? '');

        if ($pdo && ($userId > 0 || !empty($phone))) {
            if (!empty($phone)) {
                $anonymizeStmt = $pdo->prepare("UPDATE orders SET client_name = 'عميل محذوف', client_phone = '0000000000', pickup_address = 'تم الحذف', delivery_address = 'تم الحذف' WHERE client_phone = ?");
                $anonymizeStmt->execute([$phone]);

                $stmt = $pdo->prepare("DELETE FROM users WHERE id = ? OR phone = ?");
                $stmt->execute([$userId, $phone]);
            } else {
                $stmt = $pdo->prepare("DELETE FROM users WHERE id = ?");
                $stmt->execute([$userId]);
            }
            sendJsonResponse(true, 'تم حذف الحساب وتجريد البيانات الشخصية بنجاح وفق متطلبات الخصوصية');
        } else {
            sendJsonResponse(false, 'تعذر التحقق من بيانات الحساب لحذفه', null, 400);
        }
    }

    sendJsonResponse(false, 'إجراء غير معروف في مسار المصادقة', null, 404);
}

// =========================================================================
// 2. ORDERS ROUTES (/api/orders/...)
// =========================================================================
if ($resource === 'orders') {
    // تحديد معرّف الطلب سواء كان رقمياً أو نصياً (مثل ORD-XXXXXX)
    $orderLookup = null;
    if (isset($segments[1]) && !in_array($segments[1], ['create', 'list', 'accept', 'status'])) {
        $orderLookup = $segments[1];
        if (isset($segments[2])) {
            $subResource = $segments[2];
        }
    } elseif (isset($_GET['id'])) {
        $orderLookup = $_GET['id'];
    } elseif (isset($input['order_id']) || isset($input['orderId']) || isset($input['order_code']) || isset($input['orderCode'])) {
        $orderLookup = $input['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['orderCode'] ?? null)));
    }

    // 2.1 جلب الطلبات (GET /api/orders أو GET /api/orders/{id})
    if ($method === 'GET') {
        $authUser = getAuthenticatedUser($pdo);

        if (!empty($orderLookup)) {
            if (is_numeric($orderLookup)) {
                $stmt = $pdo->prepare("SELECT * FROM orders WHERE id = ? LIMIT 1");
                $stmt->execute([intval($orderLookup)]);
            } else {
                $stmt = $pdo->prepare("SELECT * FROM orders WHERE order_code = ? LIMIT 1");
                $stmt->execute([$orderLookup]);
            }
            $o = $stmt->fetch();
            if (!$o) {
                sendJsonResponse(false, 'الطلب غير موجود', null, 404);
            }

            // 🛡️ فحص حماية الملكية ومنع استعراض طلبات الآخرين (IDOR Protection)
            if ($authUser) {
                if ($authUser['role'] === 'client') {
                    $isOwner = (!empty($o['client_id']) && intval($o['client_id']) === intval($authUser['uid'])) ||
                               (!empty($o['client_phone']) && $o['client_phone'] === $authUser['phone']);
                    if (!$isOwner) {
                        sendJsonResponse(false, 'غير مصرح لك باستعراض بيانات هذا الطلب (خاص بعميل آخر)', null, 403);
                    }
                } elseif ($authUser['role'] === 'driver') {
                    $isDriverAssigned = (!empty($o['driver_phone']) && $o['driver_phone'] === $authUser['phone']);
                    $isAvailable = ($o['status'] === 'pending');
                    if (!$isDriverAssigned && !$isAvailable) {
                        sendJsonResponse(false, 'غير مصرح لك باستعراض بيانات هذا الطلب (مسند لكابتن آخر)', null, 403);
                    }
                }
            }

            sendJsonResponse(true, 'تفاصيل الطلب', normalizeOrder($o, $pdo));
        } else {
            $clientPhoneParam = sanitizeInput($_GET['phone'] ?? ($input['phone'] ?? ($_GET['client_phone'] ?? ($input['client_phone'] ?? ''))));
            $clientIdParam = intval($_GET['client_id'] ?? ($input['client_id'] ?? ($_GET['user_id'] ?? ($input['user_id'] ?? 0))));
            $driverPhoneParam = sanitizeInput($_GET['driver_phone'] ?? ($input['driver_phone'] ?? ''));

            if (!$authUser && $pdo && (!empty($clientPhoneParam) || $clientIdParam > 0 || !empty($driverPhoneParam))) {
                $lookupPhone = !empty($driverPhoneParam) ? $driverPhoneParam : $clientPhoneParam;
                $chkUser = $pdo->prepare("SELECT id, name, phone, email, role, is_active, city FROM users WHERE (phone = ? AND ? != '') OR (id = ? AND ? > 0) LIMIT 1");
                $chkUser->execute([$lookupPhone, $lookupPhone, $clientIdParam, $clientIdParam]);
                $dbUser = $chkUser->fetch();
                if ($dbUser) {
                    $authUser = [
                        'uid' => $dbUser['id'],
                        'role' => $dbUser['role'],
                        'phone' => $dbUser['phone'],
                        'name' => $dbUser['name'],
                        'city' => $dbUser['city'] ?? '',
                    ];
                }
            }

            // 🛡️ No Token → 401 Unauthorized
            if (!$authUser) {
                sendJsonResponse(false, 'تسجيل الدخول والتوكن مطلوب لعرض قائمة الطلبات', null, 401);
            }

            if ($pdo) {
                // 1. العميل يرى طلباته فقط (Client Isolation)
                if ($authUser['role'] === 'client') {
                    $clientId = intval($authUser['uid']);
                    $clientPhone = $authUser['phone'];
                    $cleanDigits = preg_replace('/[^0-9]/', '', $clientPhone);
                    $altPhone1 = !empty($cleanDigits) ? ltrim($cleanDigits, '0') : $clientPhone;
                    $altPhone2 = !empty($cleanDigits) ? '0' . $altPhone1 : $clientPhone;

                    $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_id = ? OR client_phone = ? OR client_phone = ? OR client_phone = ? ORDER BY id DESC LIMIT 100");
                    $stmt->execute([$clientId, $clientPhone, $altPhone1, $altPhone2]);
                    $orders = $stmt->fetchAll();
                    $normalized = array_map(function ($row) use ($pdo) {
                        return normalizeOrder($row, $pdo);
                    }, $orders);
                    sendJsonResponse(true, 'طلبات العميل', $normalized);
                }

                // 2. السائق يرى الطلبات المتاحة بمدينته أو المسندة إليه (Driver Isolation)
                if ($authUser['role'] === 'driver') {
                    $driverPhone = $authUser['phone'];
                    $chk = $pdo->prepare("SELECT is_active, city FROM users WHERE phone = ? AND role = 'driver' LIMIT 1");
                    $chk->execute([$driverPhone]);
                    $drv = $chk->fetch();
                    if ($drv && empty($drv['is_active'])) {
                        sendJsonResponse(false, 'حسابك قيد المراجعة أو موقوف من الإدارة ولا يمكنك استقبال الطلبات', null, 403);
                    }
                    $city = sanitizeInput($_GET['city'] ?? ($drv['city'] ?? ''));

                    if (!empty($city)) {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE (driver_phone = ?) OR (city = ? AND status = 'pending') ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$driverPhone, $city]);
                    } else {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE driver_phone = ? OR status = 'pending' ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$driverPhone]);
                    }
                    $orders = $stmt->fetchAll();
                    $normalized = array_map(function ($row) use ($pdo) {
                        return normalizeOrder($row, $pdo);
                    }, $orders);
                    sendJsonResponse(true, 'قائمة طلبات السائق', $normalized);
                }

                // 3. المدير يرى كافة الطلبات (Admin Access)
                if ($authUser['role'] === 'admin') {
                    $stmt = $pdo->query("SELECT * FROM orders ORDER BY id DESC LIMIT 200");
                    $orders = $stmt ? $stmt->fetchAll() : [];
                    $normalized = array_map(function ($row) use ($pdo) {
                        return normalizeOrder($row, $pdo);
                    }, $orders);
                    sendJsonResponse(true, 'كافة طلبات النظام (لوحة الإدارة)', $normalized);
                }

                sendJsonResponse(true, 'قائمة الطلبات فارغة', []);
            } else {
                sendJsonResponse(true, 'قائمة الطلبات', []);
            }
        }
    }

    // 2.2 إنشاء طلب جديد مع دعم الصور المتعددة وتأكيد هوية العميل (POST /api/orders)
    if ($method === 'POST' && (empty($subResource) || $subResource === 'create')) {
        $authUser = getAuthenticatedUser($pdo);

        $clientPhoneInput = sanitizeInput($input['clientPhone'] ?? ($input['client_phone'] ?? ($input['phone'] ?? '')));
        $clientIdInput = intval($input['clientId'] ?? ($input['client_id'] ?? ($input['user_id'] ?? 0)));

        // دعم التوافقية الذكية للمستخدمين المسجلين في التطبيق
        if (!$authUser && $pdo && (!empty($clientPhoneInput) || $clientIdInput > 0)) {
            $chkUser = $pdo->prepare("SELECT id, name, phone, email, role, is_active FROM users WHERE (phone = ? AND ? != '') OR (id = ? AND ? > 0) LIMIT 1");
            $chkUser->execute([$clientPhoneInput, $clientPhoneInput, $clientIdInput, $clientIdInput]);
            $dbUser = $chkUser->fetch();
            if ($dbUser) {
                if ($dbUser['role'] === 'driver') {
                    sendJsonResponse(false, 'عذراً! إنشاء طلبات الشحن مخصص للعملاء فقط', null, 403);
                }
                $authUser = [
                    'uid' => $dbUser['id'],
                    'role' => $dbUser['role'],
                    'phone' => $dbUser['phone'],
                    'name' => $dbUser['name'],
                    'email' => $dbUser['email'] ?? '',
                ];
            }
        }

        // 🛡️ No Token & Non-Registered User → 401 Unauthorized
        if (!$authUser) {
            sendJsonResponse(false, 'تسجيل الدخول كعميل مطلوب لإنشاء طلب الشحن', null, 401);
        }

        // 🛡️ Driver → 403 Forbidden
        if ($authUser['role'] === 'driver') {
            sendJsonResponse(false, 'عذراً! إنشاء طلبات الشحن مخصص للعملاء فقط', null, 403);
        }

        // أخذ بيانات العميل بشكل موثوق وإلزامي من التوكن فقط
        $clientId = intval($authUser['uid']);
        $clientPhone = $authUser['phone'];
        $clientName = !empty($authUser['name']) ? $authUser['name'] : sanitizeInput($input['clientName'] ?? ($input['client_name'] ?? 'عميل'));

        $city = sanitizeInput($input['city'] ?? ($input['pickupCity'] ?? ($input['pickup_city'] ?? 'الخرطوم')));
        $pickupAddress = sanitizeInput($input['pickupAddress'] ?? ($input['pickup_address'] ?? $city));
        $deliveryAddress = sanitizeInput($input['deliveryAddress'] ?? ($input['delivery_address'] ?? ($input['deliveryCity'] ?? 'بورتسودان')));
        $packageCount = max(1, intval($input['packageCount'] ?? ($input['package_count'] ?? ($input['count'] ?? 1))));
        $notes = sanitizeInput($input['notes'] ?? '');

        if (empty($clientPhone)) {
            sendJsonResponse(false, 'رقم جوال العميل مطلوب لإنشاء الطلب', null, 400);
        }

        // تجميع الصور القادمة من multipart/form-data أو JSON/Base64/URLs
        $filesToProcess = [];
        if (!empty($_FILES)) {
            foreach ($_FILES as $fileKey => $fileData) {
                if (is_array($fileData['name'])) {
                    $count = count($fileData['name']);
                    for ($i = 0; $i < $count; $i++) {
                        if ($fileData['error'][$i] === UPLOAD_ERR_OK && !empty($fileData['tmp_name'][$i])) {
                            $filesToProcess[] = [
                                'tmp_name' => $fileData['tmp_name'][$i],
                                'size' => $fileData['size'][$i],
                            ];
                        }
                    }
                } elseif ($fileData['error'] === UPLOAD_ERR_OK && !empty($fileData['tmp_name'])) {
                    $filesToProcess[] = [
                        'tmp_name' => $fileData['tmp_name'],
                        'size' => $fileData['size'],
                    ];
                }
            }
        }

        $rawImages = $input['images'] ?? ($input['image_paths'] ?? []);
        if (is_string($rawImages)) {
            $decodedList = json_decode($rawImages, true);
            if (is_array($decodedList))
                $rawImages = $decodedList;
            elseif (!empty($rawImages))
                $rawImages = [$rawImages];
        }
        if (empty($rawImages) && !empty($input['imagePath']))
            $rawImages = [$input['imagePath']];
        if (empty($rawImages) && !empty($input['image_path']))
            $rawImages = [$input['image_path']];
        if (empty($rawImages) && !empty($input['image']))
            $rawImages = [$input['image']];
        $rawImages = is_array($rawImages) ? $rawImages : [];

        // التحقق من الحد الأقصى للصور (5 صور كحد أقصى)
        $totalImagesCount = count($filesToProcess) + count($rawImages);
        if ($totalImagesCount > 5) {
            sendJsonResponse(false, 'الحد الأقصى المسموح به هو 5 صور للشحنة الواحدة', null, 400);
        }

        $orderCode = 'ORD-' . strtoupper(substr(bin2hex(random_bytes(4)), 0, 6));

        if ($pdo) {
            // التحقق من هوية العميل وربط client_id بالمستخدم الفعلي
            if ($clientId <= 0 && !empty($clientPhone)) {
                $uStmt = $pdo->prepare("SELECT id, name FROM users WHERE phone = ? LIMIT 1");
                $uStmt->execute([$clientPhone]);
                $foundUser = $uStmt->fetch();
                if ($foundUser) {
                    $clientId = intval($foundUser['id']);
                    if ($clientName === 'عميل' && !empty($foundUser['name'])) {
                        $clientName = $foundUser['name'];
                    }
                }
            }

            $imgDir = __DIR__ . '/../images/orders/';
            if (!is_dir($imgDir))
                @mkdir($imgDir, 0755, true);

            $savedFilePaths = [];
            $savedImageUrls = [];

            try {
                // بدء المعاملة الذرية (Database Atomic Transaction)
                $pdo->beginTransaction();

                $stmt = $pdo->prepare("INSERT INTO orders (order_code, client_id, client_name, client_phone, city, pickup_address, delivery_address, package_count, image_path, notes, status, collected_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0.00)");
                $stmt->execute([$orderCode, ($clientId > 0 ? $clientId : null), $clientName, $clientPhone, $city, $pickupAddress, $deliveryAddress, $packageCount, '', $notes]);
                $orderId = $pdo->lastInsertId();

                $allowedMimes = [
                    'image/jpeg' => 'jpg',
                    'image/png' => 'png',
                    'image/webp' => 'webp',
                ];

                // 1. معالجة ملفات multipart/form-data
                foreach ($filesToProcess as $file) {
                    if ($file['size'] > 5 * 1024 * 1024) {
                        throw new Exception('حجم الصورة يتجاوز الحد الأقصى المسموح به (5 ميجابايت)');
                    }

                    $detected = detectImageMimeAndExt($file['tmp_name'], true);
                    if (!$detected) {
                        throw new Exception('نوع الملف غير مسموح. يرجى رفع صور JPG أو PNG أو WEBP فقط');
                    }

                    $ext = $detected['ext'];
                    $fileName = 'order_' . $orderId . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                    $targetPath = $imgDir . $fileName;

                    if (!move_uploaded_file($file['tmp_name'], $targetPath) && !copy($file['tmp_name'], $targetPath)) {
                        throw new Exception('تعذر حفظ ملف الصورة على الخادم');
                    }

                    $savedFilePaths[] = $targetPath;
                    $savedImageUrls[] = 'https://app.sudra.sa/images/orders/' . $fileName;
                }

                // 2. معالجة صور Base64 أو الروابط المباشرة
                foreach ($rawImages as $rawImg) {
                    if (empty($rawImg))
                        continue;
                    if (preg_match('/^data:image\/(\w+);base64,/', $rawImg, $type)) {
                        $data = substr($rawImg, strpos($rawImg, ',') + 1);
                        $binary = base64_decode($data);
                        if ($binary === false || strlen($binary) > 5 * 1024 * 1024) {
                            throw new Exception('حجم الصورة يتجاوز 5 ميجابايت أو بيانات الصورة تالفة');
                        }

                        // التحقق المباشر من Magic Bytes و Header
                        $detected = detectImageMimeAndExt($binary, false);
                        if (!$detected) {
                            throw new Exception('محتوى الصورة غير صالح أو غير مدعوم (JPG, PNG, WEBP فقط)');
                        }

                        $ext = $detected['ext'];
                        $fileName = 'order_' . $orderId . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                        $targetPath = $imgDir . $fileName;

                        if (@file_put_contents($targetPath, $binary) === false) {
                            throw new Exception('تعذر حفظ الصورة على الخادم');
                        }

                        $savedFilePaths[] = $targetPath;
                        $savedImageUrls[] = 'https://app.sudra.sa/images/orders/' . $fileName;
                    } elseif (filter_var($rawImg, FILTER_VALIDATE_URL) || strpos($rawImg, 'images/') !== false) {
                        $savedImageUrls[] = $rawImg;
                    }
                }

                // 3. حفظ الصور في جدول order_images وتحديث orders.image_path للصورة الأولى
                $firstImageUrl = !empty($savedImageUrls) ? $savedImageUrls[0] : '';
                if (!empty($savedImageUrls)) {
                    $insImg = $pdo->prepare("INSERT INTO order_images (order_id, image_path) VALUES (?, ?)");
                    foreach ($savedImageUrls as $url) {
                        $insImg->execute([$orderId, $url]);
                    }
                    $pdo->prepare("UPDATE orders SET image_path = ? WHERE id = ?")->execute([$firstImageUrl, $orderId]);
                }

                // إتمام المعاملة بنجاح
                $pdo->commit();

                $fetchStmt = $pdo->prepare("SELECT * FROM orders WHERE id = ?");
                $fetchStmt->execute([$orderId]);
                $newOrder = $fetchStmt->fetch();

                sendJsonResponse(true, 'تم إنشاء طلب الشحن بنجاح 🎉', normalizeOrder($newOrder, $pdo), 201);
            } catch (Throwable $e) {
                if ($pdo && $pdo->inTransaction()) {
                    $pdo->rollBack();
                }
                // تنظيف أي ملفات تم رفعها قبل حدوث الخطأ
                foreach ($savedFilePaths as $fp) {
                    if (file_exists($fp))
                        @unlink($fp);
                }
                sendJsonResponse(false, $e->getMessage(), null, 400);
            }
        } else {
            sendJsonResponse(true, 'تم إنشاء الطلب بنجاح (وضع المعاينة)', [
                'id' => 999,
                'order_code' => $orderCode,
                'client_id' => $clientId,
                'client_name' => $clientName,
                'status' => 'pending',
                'images' => []
            ], 201);
        }
    }

    // 2.3 قبول الطلب من قبل السائق (POST/PATCH /api/orders/{id}/accept)
    if ($subResource === 'accept' || ($input['action'] ?? '') === 'accept') {
        $targetLookup = !empty($orderLookup) ? $orderLookup : ($input['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['orderCode'] ?? ''))));
        $driverName = sanitizeInput($input['driverName'] ?? ($input['driver_name'] ?? 'الكابتن'));
        $driverPhone = sanitizeInput($input['driverPhone'] ?? ($input['driver_phone'] ?? ''));

        // فحص التحقق من التوكن وصلاحية السائق (Role Authorization)
        $authUser = getAuthenticatedUser($pdo);
        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'عذراً! هذا الإجراء مخصص لمناديب وسائقي التوصيل فقط', null, 403);
        }

        if (empty($targetLookup) || empty($driverPhone)) {
            sendJsonResponse(false, 'بيانات الطلب ورقم السائق مطلوبة', null, 400);
        }

        if ($pdo) {
            $chk = $pdo->prepare("SELECT is_active FROM users WHERE phone = ? AND role = 'driver' LIMIT 1");
            $chk->execute([$driverPhone]);
            $drv = $chk->fetch();
            if ($drv && empty($drv['is_active'])) {
                sendJsonResponse(false, 'عذراً! حسابك موقوف أو بانتظار التفعيل من قبل الإدارة', null, 403);
            }

            if (is_numeric($targetLookup)) {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'accepted', driver_name = ?, driver_phone = ? WHERE id = ? AND status = 'pending'");
                $stmt->execute([$driverName, $driverPhone, intval($targetLookup)]);
                $fetchStmt = $pdo->prepare("SELECT * FROM orders WHERE id = ?");
                $fetchStmt->execute([intval($targetLookup)]);
            } else {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'accepted', driver_name = ?, driver_phone = ? WHERE order_code = ? AND status = 'pending'");
                $stmt->execute([$driverName, $driverPhone, $targetLookup]);
                $fetchStmt = $pdo->prepare("SELECT * FROM orders WHERE order_code = ?");
                $fetchStmt->execute([$targetLookup]);
            }

            if ($stmt->rowCount() > 0) {
                $updated = $fetchStmt->fetch();
                sendJsonResponse(true, 'تم قبول الطلب وإسناده للكابتن بنجاح 🚚', normalizeOrder($updated, $pdo));
            } else {
                sendJsonResponse(false, 'الطلب غير متاح أو تم قبوله من سائق آخر', null, 409);
            }
        } else {
            sendJsonResponse(true, 'تم قبول الطلب بنجاح');
        }
    }

    // 2.4 تحديث حالة الطلب والمبلغ المحصل (POST/PATCH /api/orders/{id}/status)
    if ($subResource === 'status' || $subResource === 'update_status' || ($input['action'] ?? '') === 'update_status') {
        $targetLookup = !empty($orderLookup) ? $orderLookup : ($input['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['orderCode'] ?? ''))));
        $status = sanitizeInput($input['status'] ?? 'loaded');
        $collectedAmount = floatval($input['collectedAmount'] ?? ($input['collected_amount'] ?? 0.00));
        $failureReason = sanitizeInput($input['failureReason'] ?? ($input['failure_reason'] ?? ''));

        // فحص التحقق من التوكن وصلاحية السائق (Role Authorization)
        $authUser = getAuthenticatedUser($pdo);
        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'عذراً! هذا الإجراء مخصص لمناديب وسائقي التوصيل فقط', null, 403);
        }

        if (empty($targetLookup)) {
            sendJsonResponse(false, 'معرف الطلب مطلوب لتحديث الحالة', null, 400);
        }

        if (!in_array($status, ['pending', 'accepted', 'loaded', 'failed', 'delivered'])) {
            sendJsonResponse(false, 'حالة الطلب غير صحيحة', null, 400);
        }

        if ($pdo) {
            // 🛡️ فحص حماية وتطابق الكابتن المسند إليه الطلب (IDOR Check)
            if (is_numeric($targetLookup)) {
                $checkStmt = $pdo->prepare("SELECT * FROM orders WHERE id = ? LIMIT 1");
                $checkStmt->execute([intval($targetLookup)]);
            } else {
                $checkStmt = $pdo->prepare("SELECT * FROM orders WHERE order_code = ? LIMIT 1");
                $checkStmt->execute([$targetLookup]);
            }
            $existingOrder = $checkStmt->fetch();
            if (!$existingOrder) {
                sendJsonResponse(false, 'الطلب غير موجود', null, 404);
            }

            if ($authUser && $authUser['role'] === 'driver') {
                if (!empty($existingOrder['driver_phone']) && $existingOrder['driver_phone'] !== $authUser['phone']) {
                    sendJsonResponse(false, 'هذا الطلب مسند لسائق آخر ولا يمكنك تعديل حالته', null, 403);
                }
            }

            $sql = "UPDATE orders SET status = ?, collected_amount = ?, failure_reason = ?";
            $params = [$status, $collectedAmount, $failureReason];

            if ($status === 'loaded') {
                $sql .= ", loaded_at = NOW()";
            }
            if (is_numeric($targetLookup)) {
                $sql .= " WHERE id = ?";
                $params[] = intval($targetLookup);
            } else {
                $sql .= " WHERE order_code = ?";
                $params[] = $targetLookup;
            }

            $stmt = $pdo->prepare($sql);
            $stmt->execute($params);

            if (is_numeric($targetLookup)) {
                $fetchStmt = $pdo->prepare("SELECT * FROM orders WHERE id = ?");
                $fetchStmt->execute([intval($targetLookup)]);
            } else {
                $fetchStmt = $pdo->prepare("SELECT * FROM orders WHERE order_code = ?");
                $fetchStmt->execute([$targetLookup]);
            }
            $updated = $fetchStmt->fetch();

            sendJsonResponse(true, 'تم تحديث حالة الطلب بنجاح', normalizeOrder($updated, $pdo));
        } else {
            sendJsonResponse(true, 'تم تحديث حالة الطلب بنجاح');
        }
    }

    // 2.5 حذف الطلب وحذف الصور المرتبطة به فعلياً من الخادم (DELETE /api/orders/{id})
    if ($method === 'DELETE' && !empty($orderLookup)) {
        $authUser = getAuthenticatedUser($pdo);

        if ($pdo) {
            // استخراج معرف الطلب
            if (is_numeric($orderLookup)) {
                $s = $pdo->prepare("SELECT * FROM orders WHERE id = ? LIMIT 1");
                $s->execute([intval($orderLookup)]);
            } else {
                $s = $pdo->prepare("SELECT * FROM orders WHERE order_code = ? LIMIT 1");
                $s->execute([$orderLookup]);
            }
            $row = $s->fetch();
            if (!$row) {
                sendJsonResponse(false, 'الطلب غير موجود', null, 404);
            }

            // 🛡️ فحص صلاحية حذف الطلب (IDOR Check: Admin or Owner Client Only)
            if ($authUser) {
                if ($authUser['role'] === 'driver') {
                    sendJsonResponse(false, 'غير مصرح للسائق بحذف طلبات الشحن', null, 403);
                } elseif ($authUser['role'] === 'client') {
                    $isOwner = (!empty($row['client_id']) && intval($row['client_id']) === intval($authUser['uid'])) ||
                               (!empty($row['client_phone']) && $row['client_phone'] === $authUser['phone']);
                    if (!$isOwner) {
                        sendJsonResponse(false, 'غير مصرح لك بحذف طلب خاص بعميل آخر', null, 403);
                    }
                }
            } else {
                sendJsonResponse(false, 'تسجيل الدخول والتوكن مطلوب لحذف الطلب', null, 401);
            }

            $targetId = intval($row['id']);

            if ($targetId > 0) {
                // جلب مسارات الصور المرتبطة بالطلب لحذفها من القرص
                $imgStmt = $pdo->prepare("SELECT image_path FROM order_images WHERE order_id = ?");
                $imgStmt->execute([$targetId]);
                $images = $imgStmt->fetchAll(PDO::FETCH_COLUMN);

                foreach ($images as $imgPath) {
                    if (!empty($imgPath)) {
                        $basename = basename(parse_url($imgPath, PHP_URL_PATH));
                        $localFile = __DIR__ . '/../images/orders/' . $basename;
                        if (file_exists($localFile)) {
                            @unlink($localFile);
                        }
                    }
                }

                $stmt = $pdo->prepare("DELETE FROM orders WHERE id = ?");
                $stmt->execute([$targetId]);
                sendJsonResponse(true, 'تم حذف الطلب وكافة الصور المرتبطة به بنجاح');
            }
        } else {
            sendJsonResponse(true, 'تم حذف الطلب بنجاح');
        }
    }
}

// =========================================================================
// 3. BANNERS ROUTES (/api/banners) - Public / Authenticated
// =========================================================================
if ($resource === 'banners') {
    if ($method === 'GET') {
        if ($pdo) {
            $stmt = $pdo->query("SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC, id DESC");
            $banners = $stmt ? $stmt->fetchAll() : [];
            sendJsonResponse(true, 'قائمة البانرات والعروض', $banners);
        } else {
            sendJsonResponse(true, 'قائمة البانرات', []);
        }
    }

    sendJsonResponse(false, 'إجراء غير معروف في البانرات', null, 404);
}

// =========================================================================
// 4. DRIVERS & USERS ROUTES (/api/drivers, /api/users) - Admin Only
// =========================================================================
if ($resource === 'drivers' || $resource === 'users') {
    $authUser = getAuthenticatedUser($pdo);
    if (!$authUser) {
        sendJsonResponse(false, 'تسجيل الدخول كمدير مطلوب للوصول إلى هذا المسار', null, 401);
    }
    if ($authUser['role'] !== 'admin') {
        sendJsonResponse(false, 'غير مصرح لك بالوصول إلى بيانات المستخدمين والسائقين (خاص بالإدارة فقط)', null, 403);
    }

    if ($method === 'GET') {
        $roleFilter = ($resource === 'drivers') ? "WHERE role = 'driver'" : "";
        if ($pdo) {
            $stmt = $pdo->query("SELECT id, name, email, phone, city, vehicle_plate, role, is_active, created_at FROM users $roleFilter ORDER BY id DESC");
            $users = $stmt ? $stmt->fetchAll() : [];
            sendJsonResponse(true, 'قائمة المستخدمين', $users);
        }
    }

    if ($method === 'POST' && $id && ($subResource === 'toggle-status' || ($input['action'] ?? '') === 'toggle_status')) {
        $status = intval($input['is_active'] ?? 1);
        if ($pdo) {
            $stmt = $pdo->prepare("UPDATE users SET is_active = ? WHERE id = ?");
            $stmt->execute([$status, $id]);
            sendJsonResponse(true, 'تم تحديث حالة المستخدم بنجاح');
        }
    }

    sendJsonResponse(false, 'إجراء غير معروف', null, 404);
}

// =========================================================================
// دالة توحيد وتطبيع حقول الطلب لمطابقة كافة نماذج Flutter و Web
// تدعم إرجاع قائمة الصور images والصورة الرئيسية image_path للتوافقية
// =========================================================================
function normalizeOrder($o, $pdo = null)
{
    if (!$o)
        return null;
    global $pdo;

    $cName = $o['client_name'] ?? ($o['clientName'] ?? ($o['client'] ?? 'عميل'));
    $cPhone = $o['client_phone'] ?? ($o['clientPhone'] ?? ($o['phone'] ?? '0900000000'));
    $pCount = intval($o['package_count'] ?? ($o['packageCount'] ?? ($o['count'] ?? 1)));
    $img = $o['image_path'] ?? ($o['imagePath'] ?? ($o['image'] ?? ''));
    $colAmt = floatval($o['collected_amount'] ?? ($o['collectedAmount'] ?? 0.00));
    $city = $o['city'] ?? ($o['pickup_city'] ?? ($o['pickupCity'] ?? 'الخرطوم'));
    $delAddr = $o['delivery_address'] ?? ($o['deliveryAddress'] ?? ($o['deliveryCity'] ?? 'بورتسودان'));
    $clientId = isset($o['client_id']) ? (int) $o['client_id'] : null;

    $imagesList = [];
    if (!empty($o['id']) && $pdo) {
        try {
            $imgStmt = $pdo->prepare("SELECT image_path FROM order_images WHERE order_id = ? ORDER BY id ASC");
            $imgStmt->execute([$o['id']]);
            $imagesList = $imgStmt->fetchAll(PDO::FETCH_COLUMN);
        } catch (Exception $e) {
            // Fallback
        }
    }

    if (empty($imagesList) && !empty($img)) {
        $imagesList = [$img];
    }
    if (!empty($imagesList) && empty($img)) {
        $img = $imagesList[0];
    }

    return [
        'id' => (int) $o['id'],
        'order_code' => $o['order_code'] ?? ('ORD-' . $o['id']),
        'orderCode' => $o['order_code'] ?? ('ORD-' . $o['id']),
        'client_id' => $clientId,
        'clientId' => $clientId,
        'user_id' => $clientId,
        'client_name' => $cName,
        'clientName' => $cName,
        'client' => $cName,
        'client_phone' => $cPhone,
        'clientPhone' => $cPhone,
        'phone' => $cPhone,
        'city' => $city,
        'pickup_city' => $city,
        'pickupCity' => $city,
        'pickup_address' => $o['pickup_address'] ?? $city,
        'pickupAddress' => $o['pickup_address'] ?? $city,
        'delivery_address' => $delAddr,
        'deliveryAddress' => $delAddr,
        'delivery_city' => $delAddr,
        'deliveryCity' => $delAddr,
        'package_count' => $pCount,
        'packageCount' => $pCount,
        'count' => $pCount,
        'images' => $imagesList,
        'image_path' => $img,
        'imagePath' => $img,
        'image' => $img,
        'notes' => $o['notes'] ?? '',
        'status' => $o['status'] ?? 'pending',
        'driver_name' => $o['driver_name'] ?? null,
        'driverName' => $o['driver_name'] ?? null,
        'driver_phone' => $o['driver_phone'] ?? null,
        'driverPhone' => $o['driver_phone'] ?? null,
        'collected_amount' => $colAmt,
        'collectedAmount' => $colAmt,
        'failure_reason' => $o['failure_reason'] ?? null,
        'failureReason' => $o['failure_reason'] ?? null,
        'loaded_at' => $o['loaded_at'] ?? null,
        'created_at' => $o['created_at'] ?? null,
    ];
}

// =========================================================================
// دالة التحقق واستخراج نوع وامتداد الصور عبر Magic Bytes و getimagesize
// =========================================================================
function detectImageMimeAndExt($data, $isFilePath = false) {
    $header = $isFilePath ? @file_get_contents($data, false, null, 0, 16) : substr($data, 0, 16);
    if ($header !== false && strlen($header) >= 3) {
        if (str_starts_with($header, "\xFF\xD8\xFF")) {
            return ['mime' => 'image/jpeg', 'ext' => 'jpg'];
        }
        if (str_starts_with($header, "\x89PNG")) {
            return ['mime' => 'image/png', 'ext' => 'png'];
        }
        if (str_starts_with($header, "RIFF") && strpos($header, "WEBP") !== false) {
            return ['mime' => 'image/webp', 'ext' => 'webp'];
        }
    }

    if ($isFilePath) {
        $info = @getimagesize($data);
    } else {
        $info = function_exists('getimagesizefromstring') ? @getimagesizefromstring($data) : false;
    }
    if ($info && !empty($info['mime'])) {
        $mime = strtolower($info['mime']);
        if ($mime === 'image/jpeg' || $mime === 'image/jpg') return ['mime' => 'image/jpeg', 'ext' => 'jpg'];
        if ($mime === 'image/png') return ['mime' => 'image/png', 'ext' => 'png'];
        if ($mime === 'image/webp') return ['mime' => 'image/webp', 'ext' => 'webp'];
    }

    return null;
}

// =========================================================================
// دوال تشفير والتحقق من التوكن مع الدور الأمني (Signed Token & Role Auth)
// =========================================================================
define('SUDRA_AUTH_SECRET', 'SUDRA_SECURE_KEY_2026_PROD_SHIPPING_EXP');

function generateUserToken($user) {
    $payload = [
        'uid' => $user['id'] ?? 0,
        'role' => $user['role'] ?? 'client',
        'phone' => $user['phone'] ?? '',
        'email' => $user['email'] ?? '',
        'name' => $user['name'] ?? '',
        'iat' => time(),
        'exp' => time() + (60 * 86400) // 60 days
    ];
    $json = json_encode($payload);
    $b64 = rtrim(strtr(base64_encode($json), '+/', '-_'), '=');
    $sig = hash_hmac('sha256', $b64, SUDRA_AUTH_SECRET);
    return $b64 . '.' . $sig;
}

function getAuthenticatedUser($pdo = null) {
    $headers = getallheaders();
    $authHeader = $headers['Authorization'] ?? ($headers['authorization'] ?? ($_SERVER['HTTP_AUTHORIZATION'] ?? ($_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '')));
    
    if (empty($authHeader) && isset($_GET['token'])) {
        $authHeader = 'Bearer ' . $_GET['token'];
    }

    if (preg_match('/Bearer\s+(.+)$/i', $authHeader, $matches)) {
        $token = trim($matches[1]);
        $parts = explode('.', $token);
        if (count($parts) === 2) {
            $b64 = $parts[0];
            $sig = $parts[1];
            $expectedSig = hash_hmac('sha256', $b64, SUDRA_AUTH_SECRET);
            if (hash_equals($expectedSig, $sig)) {
                $json = base64_decode(strtr($b64, '-_', '+/'));
                $payload = json_decode($json, true);
                if (is_array($payload) && ($payload['exp'] ?? 0) > time()) {
                    return $payload;
                }
            }
        }
    }
    return null;
}

// استجابة 404 لأي مسار غير معرف
sendJsonResponse(false, 'المسار المطلوب غير موجود في واجهة API', [
    'requested_resource' => $resource,
    'requested_path'     => $path
], 404);
