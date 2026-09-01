<?php
/**
 * سودرا للشحن والتوصيل - SUDRA EXPRESS | Unified RESTful API Engine
 * نظام موحد وآمن يدعم تطبيقات فلاتر (العميل والسائق)، الويب، ولوحة التحكم الإدارية
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../config/mail.php';

// 1. استخراج وتحليل المسار والطلب
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method     = strtoupper($_SERVER['REQUEST_METHOD']);
$clientIp   = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? ($_SERVER['HTTP_X_FORWARDED_FOR'] ?? ($_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'));

// إزالة المسار الأساسي /api أو /backend_php/api
$path = preg_replace('#^/(backend_php/)?api/?#', '', $requestUri);
$segments = array_values(array_filter(explode('/', trim($path, '/'))));

$resource    = $segments[0] ?? ($_GET['resource'] ?? '');
$subResource = $segments[1] ?? ($_GET['action'] ?? null);
$id          = null;

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
$input    = json_decode($rawInput, true);
if (empty($input) && !empty($_POST)) {
    $input = $_POST;
}
$input = is_array($input) ? $input : [];

// =========================================================================
// 1. AUTHENTICATION ROUTES (/api/auth/...)
// =========================================================================
if ($resource === 'auth') {
    $action = $subResource ?? ($input['action'] ?? ($_GET['action'] ?? ''));

    // 1.1 تسجيل الدخول (login & admin-login)
    if ($action === 'login' || $action === 'admin-login' || $action === 'admin_login') {
        $identifier = sanitizeInput($input['email'] ?? ($input['phone'] ?? ($input['username'] ?? '')));
        $password   = $input['password'] ?? '';

        if (empty($identifier) || empty($password)) {
            sendJsonResponse(false, 'الرجاء إدخال البريد الإلكتروني أو رقم الجوال وكلمة المرور', null, 400);
        }

        if (!checkRateLimit($pdo, $clientIp, 'login', 10, 15)) {
            sendJsonResponse(false, '⚠️ تم تجاوز الحد الأقصى للمحاولات الخاطئة! تم حظر الدخول مؤقتاً لمدة 15 دقيقة لحماية الحساب.', null, 429);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR phone = ? LIMIT 1");
            $stmt->execute([$identifier, $identifier]);
            $user = $stmt->fetch();

            if ($user) {
                $isPasswordCorrect = verifyPassword($password, $user['password'], $user['id'], $pdo);

                if ($isPasswordCorrect) {
                    clearLoginAttempts($pdo, $clientIp, 'login');

                    if ($user['role'] === 'driver' && empty($user['is_active'])) {
                        sendJsonResponse(false, 'حساب السائق قيد المراجعة والاعتماد من قبل الإدارة', [
                            'isPending' => true,
                            'id'        => $user['id'],
                            'name'      => $user['name'],
                            'email'     => $user['email'] ?? $identifier,
                            'phone'     => $user['phone'],
                            'city'      => $user['city'] ?? 'الخرطوم',
                            'role'      => 'driver',
                            'is_active' => 0
                        ], 403);
                    }

                    $token = bin2hex(random_bytes(32));
                    $userData = [
                        'token'     => $token,
                        'id'        => $user['id'],
                        'user_id'   => $user['id'],
                        'name'      => $user['name'],
                        'email'     => $user['email'] ?? $identifier,
                        'phone'     => $user['phone'],
                        'city'      => $user['city'] ?? 'الخرطوم',
                        'role'      => $user['role'],
                        'is_active' => (int)$user['is_active']
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
                'token'   => 'preview-token',
                'name'    => 'مستخدم تجريبي',
                'phone'   => $identifier,
                'city'    => 'الخرطوم',
                'role'    => 'client'
            ]);
        }
    }

    // 1.2 إرسال رمز التحقق OTP (/api/auth/send-otp)
    if ($action === 'send-otp' || $action === 'send_otp' || $action === 'sendOtp') {
        $email      = filter_var(trim($input['email'] ?? ($input['mail'] ?? ($input['emailAddress'] ?? ''))), FILTER_VALIDATE_EMAIL);
        $actionType = sanitizeInput($input['type'] ?? ($input['action_type'] ?? ($input['actionType'] ?? 'register')));

        if (!$email) {
            sendJsonResponse(false, 'يرجى إدخال بريد إلكتروني صحيح لاستلام رمز التحقق', null, 400);
        }

        $otpCode = sprintf("%04d", random_int(1000, 9999));

        if ($pdo) {
            $invalidateStmt = $pdo->prepare("UPDATE email_otps SET is_used = 1 WHERE email = ? AND is_used = 0");
            $invalidateStmt->execute([$email]);

            $stmt = $pdo->prepare("INSERT INTO email_otps (email, otp_code, action_type, expires_at) VALUES (?, ?, ?, DATE_ADD(NOW(), INTERVAL 10 MINUTE))");
            $stmt->execute([$email, $otpCode, $actionType]);

            // إرسال البريد الإلكتروني الفعلي باستخدام محرك SMTP الموحد
            $mailSent = sendOtpEmail($email, $otpCode, $actionType);

            if ($mailSent) {
                sendJsonResponse(true, 'تم إرسال رمز التحقق OTP بنجاح إلى بريدك الإلكتروني', [
                    'email'      => $email,
                    'expires_in' => '10 دقائق'
                ]);
            } else {
                error_log("[SUDRA-AUTH] Failed to deliver OTP email to: " . $email);
                sendJsonResponse(false, 'تعذر إرسال رمز التحقق إلى بريدك الإلكتروني حالياً. يرجى التحقق من إعدادات البريد أو المحاولة لاحقاً', null, 500);
            }
        } else {
            sendJsonResponse(false, 'خدمة قاعدة البيانات غير متصلة حالياً', null, 500);
        }
    }

    // 1.3 التحقق من رمز OTP (/api/auth/verify-otp)
    if ($action === 'verify-otp' || $action === 'verify_otp') {
        $email = filter_var(trim($input['email'] ?? ''), FILTER_VALIDATE_EMAIL);
        $phone = sanitizeInput($input['phone'] ?? '');
        $otp   = trim($input['otp'] ?? ($input['otp_code'] ?? ''));

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

    // 1.4 تسجيل حساب جديد (/api/auth/register)
    if ($action === 'register') {
        $name     = sanitizeInput($input['name'] ?? '');
        $email    = filter_var(trim($input['email'] ?? ''), FILTER_SANITIZE_EMAIL);
        $phone    = sanitizeInput($input['phone'] ?? '');
        $password = $input['password'] ?? '';
        $city     = sanitizeInput($input['city'] ?? 'الخرطوم');
        $role     = in_array($input['role'] ?? '', ['client', 'driver']) ? $input['role'] : 'client';
        $plate    = sanitizeInput($input['vehicle_plate'] ?? ($input['vehiclePlate'] ?? ''));
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

            $token = bin2hex(random_bytes(32));
            $userData = [
                'token'     => $token,
                'id'        => $newId,
                'user_id'   => $newId,
                'name'      => $name,
                'email'     => $email,
                'phone'     => $phone,
                'city'      => $city,
                'role'      => $role,
                'is_active' => $isActive
            ];
            sendJsonResponse(true, 'تم إنشاء الحساب بنجاح 🎉', $userData, 201);
        } else {
            sendJsonResponse(true, 'تم إنشاء الحساب بنجاح (وضع المعاينة)', [
                'token'     => 'preview-token',
                'id'        => 99,
                'name'      => $name,
                'email'     => $email,
                'phone'     => $phone,
                'city'      => $city,
                'role'      => $role,
                'is_active' => $isActive
            ], 201);
        }
    }

    // 1.5 حذف الحساب وتجريد البيانات الشخصية (/api/auth/delete_account)
    if ($action === 'delete_account' || $action === 'delete-account') {
        $phone = sanitizeInput($input['phone'] ?? '');
        $userId = intval($input['user_id'] ?? 0);

        if ($pdo && (!empty($phone) || $userId > 0)) {
            if (!empty($phone)) {
                $anonymizeStmt = $pdo->prepare("UPDATE orders SET client_name = 'عميل محذوف', client_phone = '0000000000', pickup_address = 'تم الحذف', delivery_address = 'تم الحذف' WHERE client_phone = ?");
                $anonymizeStmt->execute([$phone]);

                $stmt = $pdo->prepare("DELETE FROM users WHERE phone = ?");
                $stmt->execute([$phone]);
            } else {
                $stmt = $pdo->prepare("DELETE FROM users WHERE id = ?");
                $stmt->execute([$userId]);
            }
            sendJsonResponse(true, 'تم حذف الحساب وتجريد البيانات الشخصية بنجاح وفق متطلبات الخصوصية');
        } else {
            sendJsonResponse(false, 'رقم الجوال أو معرّف الحساب مطلوب لحذف الحساب', null, 400);
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
            sendJsonResponse(true, 'تفاصيل الطلب', normalizeOrder($o));
        } else {
            $clientPhone = sanitizeInput($_GET['phone'] ?? ($input['phone'] ?? ($_GET['client_phone'] ?? ($input['client_phone'] ?? ''))));
            $clientId    = intval($_GET['client_id'] ?? ($input['client_id'] ?? ($_GET['user_id'] ?? ($input['user_id'] ?? 0))));
            $city        = sanitizeInput($_GET['city'] ?? ($input['city'] ?? ''));
            $driverPhone = sanitizeInput($_GET['driver_phone'] ?? ($input['driver_phone'] ?? ''));

            if ($pdo) {
                // 1. فلترة طلبات العميل الحصرية (Customer Isolation)
                if ($clientId > 0 || !empty($clientPhone)) {
                    if ($clientId > 0 && !empty($clientPhone)) {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_id = ? OR client_phone = ? ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$clientId, $clientPhone]);
                    } elseif ($clientId > 0) {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_id = ? ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$clientId]);
                    } else {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_phone = ? ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$clientPhone]);
                    }
                    $orders = $stmt->fetchAll();
                    $normalized = array_map('normalizeOrder', $orders);
                    sendJsonResponse(true, 'طلبات العميل', $normalized);
                }

                // 2. فلترة طلبات السائق المؤهل
                if (!empty($driverPhone) || !empty($city)) {
                    if (!empty($driverPhone)) {
                        $chk = $pdo->prepare("SELECT is_active, city FROM users WHERE phone = ? AND role = 'driver' LIMIT 1");
                        $chk->execute([$driverPhone]);
                        $drv = $chk->fetch();
                        if ($drv && empty($drv['is_active'])) {
                            sendJsonResponse(false, 'حسابك قيد المراجعة أو موقوف من الإدارة ولا يمكنك استقبال الطلبات', null, 403);
                        }
                        if (empty($city) && $drv && !empty($drv['city'])) {
                            $city = $drv['city'];
                        }
                    }

                    if (!empty($city) && !empty($driverPhone)) {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE (driver_phone = ?) OR (city = ? AND status = 'pending') ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$driverPhone, $city]);
                    } elseif (!empty($city)) {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE (city = ? OR ? = '') AND status = 'pending' ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$city, $city]);
                    } else {
                        $stmt = $pdo->prepare("SELECT * FROM orders WHERE driver_phone = ? OR status = 'pending' ORDER BY id DESC LIMIT 100");
                        $stmt->execute([$driverPhone]);
                    }
                    $orders = $stmt->fetchAll();
                    $normalized = array_map('normalizeOrder', $orders);
                    sendJsonResponse(true, 'قائمة طلبات السائق', $normalized);
                }

                // 3. استرجاع أحدث الطلبات
                $stmt = $pdo->query("SELECT * FROM orders ORDER BY id DESC LIMIT 100");
                $orders = $stmt ? $stmt->fetchAll() : [];
                $normalized = array_map('normalizeOrder', $orders);
                sendJsonResponse(true, 'قائمة الطلبات', $normalized);
            } else {
                sendJsonResponse(true, 'قائمة الطلبات', []);
            }
        }
    }

    // 2.2 إنشاء طلب جديد (POST /api/orders)
    if ($method === 'POST' && (empty($subResource) || $subResource === 'create')) {
        $clientName      = sanitizeInput($input['clientName'] ?? ($input['client_name'] ?? ($input['client'] ?? 'عميل')));
        $clientPhone     = sanitizeInput($input['clientPhone'] ?? ($input['client_phone'] ?? ($input['phone'] ?? '')));
        $clientId        = intval($input['clientId'] ?? ($input['client_id'] ?? ($input['user_id'] ?? 0)));
        $city            = sanitizeInput($input['city'] ?? ($input['pickupCity'] ?? ($input['pickup_city'] ?? 'الخرطوم')));
        $pickupAddress   = sanitizeInput($input['pickupAddress'] ?? ($input['pickup_address'] ?? $city));
        $deliveryAddress = sanitizeInput($input['deliveryAddress'] ?? ($input['delivery_address'] ?? ($input['deliveryCity'] ?? 'بورتسودان')));
        $packageCount    = max(1, intval($input['packageCount'] ?? ($input['package_count'] ?? ($input['count'] ?? 1))));
        $notes           = sanitizeInput($input['notes'] ?? '');
        $imagePath       = $input['imagePath'] ?? ($input['image_path'] ?? ($input['image'] ?? ''));

        if (empty($clientPhone)) {
            sendJsonResponse(false, 'رقم جوال العميل مطلوب لإنشاء الطلب', null, 400);
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

            // معالجة وحفظ الصورة المرفوعة إن وجدت (Base64 أو رابط)
            $savedImageUrl = '';
            if (!empty($imagePath)) {
                if (preg_match('/^data:image\/(\w+);base64,/', $imagePath, $type)) {
                    $data = substr($imagePath, strpos($imagePath, ',') + 1);
                    $type = strtolower($type[1]);
                    $data = base64_decode($data);
                    if ($data !== false) {
                        $imgDir = __DIR__ . '/../images/orders/';
                        if (!is_dir($imgDir)) @mkdir($imgDir, 0755, true);
                        $fileName = 'order_' . time() . '_' . rand(100, 999) . '.' . $type;
                        if (@file_put_contents($imgDir . $fileName, $data)) {
                            $savedImageUrl = 'https://app.sudra.sa/images/orders/' . $fileName;
                        }
                    }
                } else {
                    $savedImageUrl = $imagePath;
                }
            }

            $stmt = $pdo->prepare("INSERT INTO orders (order_code, client_id, client_name, client_phone, city, pickup_address, delivery_address, package_count, image_path, notes, status, collected_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0.00)");
            $stmt->execute([$orderCode, ($clientId > 0 ? $clientId : null), $clientName, $clientPhone, $city, $pickupAddress, $deliveryAddress, $packageCount, $savedImageUrl, $notes]);
            $orderId = $pdo->lastInsertId();

            $fetchStmt = $pdo->prepare("SELECT * FROM orders WHERE id = ?");
            $fetchStmt->execute([$orderId]);
            $newOrder = $fetchStmt->fetch();

            sendJsonResponse(true, 'تم إنشاء طلب الشحن بنجاح 🎉', normalizeOrder($newOrder), 201);
        } else {
            sendJsonResponse(true, 'تم إنشاء الطلب بنجاح (وضع المعاينة)', [
                'id'         => 999,
                'order_code' => $orderCode,
                'client_id'  => $clientId,
                'client_name'=> $clientName,
                'status'     => 'pending'
            ], 201);
        }
    }

    // 2.3 قبول الطلب من قبل السائق (POST/PATCH /api/orders/{id}/accept)
    if ($subResource === 'accept' || ($input['action'] ?? '') === 'accept') {
        $targetLookup = !empty($orderLookup) ? $orderLookup : ($input['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['orderCode'] ?? ''))));
        $driverName   = sanitizeInput($input['driverName'] ?? ($input['driver_name'] ?? 'الكابتن'));
        $driverPhone  = sanitizeInput($input['driverPhone'] ?? ($input['driver_phone'] ?? ''));

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
                sendJsonResponse(true, 'تم قبول الطلب وإسناده للكابتن بنجاح 🚚', normalizeOrder($updated));
            } else {
                sendJsonResponse(false, 'الطلب غير متاح أو تم قبوله من سائق آخر', null, 409);
            }
        } else {
            sendJsonResponse(true, 'تم قبول الطلب بنجاح');
        }
    }

    // 2.4 تحديث حالة الطلب والمبلغ المحصل (POST/PATCH /api/orders/{id}/status)
    if ($subResource === 'status' || $subResource === 'update_status' || ($input['action'] ?? '') === 'update_status') {
        $targetLookup    = !empty($orderLookup) ? $orderLookup : ($input['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['orderCode'] ?? ''))));
        $status          = sanitizeInput($input['status'] ?? 'loaded');
        $collectedAmount = floatval($input['collectedAmount'] ?? ($input['collected_amount'] ?? 0.00));
        $failureReason   = sanitizeInput($input['failureReason'] ?? ($input['failure_reason'] ?? ''));

        if (empty($targetLookup)) {
            sendJsonResponse(false, 'معرف الطلب مطلوب لتحديث الحالة', null, 400);
        }

        if (!in_array($status, ['pending', 'accepted', 'loaded', 'failed', 'delivered'])) {
            sendJsonResponse(false, 'حالة الطلب غير صحيحة', null, 400);
        }

        if ($pdo) {
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

            sendJsonResponse(true, 'تم تحديث حالة الطلب بنجاح', normalizeOrder($updated));
        } else {
            sendJsonResponse(true, 'تم تحديث حالة الطلب بنجاح');
        }
    }

    // 2.5 حذف الطلب (DELETE /api/orders/{id})
    if ($method === 'DELETE' && !empty($orderLookup)) {
        if ($pdo) {
            if (is_numeric($orderLookup)) {
                $stmt = $pdo->prepare("DELETE FROM orders WHERE id = ?");
                $stmt->execute([intval($orderLookup)]);
            } else {
                $stmt = $pdo->prepare("DELETE FROM orders WHERE order_code = ?");
                $stmt->execute([$orderLookup]);
            }
            sendJsonResponse(true, 'تم حذف الطلب بنجاح');
        } else {
            sendJsonResponse(true, 'تم حذف الطلب بنجاح');
        }
    }

    sendJsonResponse(false, 'إجراء غير معروف في مسار الطلبات', null, 404);
}

// =========================================================================
// 3. BANNERS ROUTES (/api/banners)
// =========================================================================
if ($resource === 'banners') {
    if ($method === 'GET') {
        if ($pdo) {
            $stmt = $pdo->query("SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC, id DESC");
            $banners = $stmt ? $stmt->fetchAll() : [];
            sendJsonResponse(true, 'قائمة البانرات الترويجية', $banners);
        } else {
            sendJsonResponse(true, 'قائمة البانرات', []);
        }
    }

    if ($method === 'POST') {
        $title      = sanitizeInput($input['title'] ?? '');
        $subtitle   = sanitizeInput($input['subtitle'] ?? '');
        $badgeText  = sanitizeInput($input['badge_text'] ?? ($input['badgeText'] ?? 'عرض خاص'));
        $imageUrl   = sanitizeInput($input['image_url'] ?? ($input['imageUrl'] ?? ''));
        $buttonText = sanitizeInput($input['button_text'] ?? ($input['buttonText'] ?? 'اطلب شحن الآن'));

        if (empty($title) || empty($imageUrl)) {
            sendJsonResponse(false, 'عنوان البانر ورابط الصورة مطلوبان', null, 400);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("INSERT INTO banners (title, subtitle, badge_text, image_url, button_text, is_active) VALUES (?, ?, ?, ?, ?, 1)");
            $stmt->execute([$title, $subtitle, $badgeText, $imageUrl, $buttonText]);
            sendJsonResponse(true, 'تمت إضافة البانر الترويجي بنجاح', ['id' => $pdo->lastInsertId()], 201);
        }
    }

    sendJsonResponse(false, 'إجراء غير معروف في مسار البانرات', null, 404);
}

// =========================================================================
// 4. DRIVERS & USERS ROUTES (/api/drivers, /api/users)
// =========================================================================
if ($resource === 'drivers' || $resource === 'users') {
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
// =========================================================================
function normalizeOrder($o) {
    if (!$o) return null;
    $cName   = $o['client_name'] ?? ($o['clientName'] ?? ($o['client'] ?? 'عميل'));
    $cPhone  = $o['client_phone'] ?? ($o['clientPhone'] ?? ($o['phone'] ?? '0900000000'));
    $pCount  = intval($o['package_count'] ?? ($o['packageCount'] ?? ($o['count'] ?? 1)));
    $img     = $o['image_path'] ?? ($o['imagePath'] ?? ($o['image'] ?? ''));
    $colAmt  = floatval($o['collected_amount'] ?? ($o['collectedAmount'] ?? 0.00));
    $city    = $o['city'] ?? ($o['pickup_city'] ?? ($o['pickupCity'] ?? 'الخرطوم'));
    $delAddr = $o['delivery_address'] ?? ($o['deliveryAddress'] ?? ($o['deliveryCity'] ?? 'بورتسودان'));

    $clientId = isset($o['client_id']) ? (int)$o['client_id'] : null;

    return [
        'id'               => (int)$o['id'],
        'order_code'       => $o['order_code'] ?? ('ORD-' . $o['id']),
        'orderCode'        => $o['order_code'] ?? ('ORD-' . $o['id']),
        'client_id'        => $clientId,
        'clientId'         => $clientId,
        'user_id'          => $clientId,
        'client_name'      => $cName,
        'clientName'       => $cName,
        'client'           => $cName,
        'client_phone'     => $cPhone,
        'clientPhone'      => $cPhone,
        'phone'            => $cPhone,
        'city'             => $city,
        'pickup_city'      => $city,
        'pickupCity'       => $city,
        'pickup_address'   => $o['pickup_address'] ?? $city,
        'pickupAddress'    => $o['pickup_address'] ?? $city,
        'delivery_address' => $delAddr,
        'deliveryAddress'  => $delAddr,
        'delivery_city'    => $delAddr,
        'deliveryCity'     => $delAddr,
        'package_count'    => $pCount,
        'packageCount'     => $pCount,
        'count'            => $pCount,
        'image_path'       => $img,
        'imagePath'        => $img,
        'image'            => $img,
        'notes'            => $o['notes'] ?? '',
        'status'           => $o['status'] ?? 'pending',
        'driver_name'      => $o['driver_name'] ?? null,
        'driverName'       => $o['driver_name'] ?? null,
        'driver_phone'     => $o['driver_phone'] ?? null,
        'driverPhone'      => $o['driver_phone'] ?? null,
        'collected_amount' => $colAmt,
        'collectedAmount'  => $colAmt,
        'failure_reason'   => $o['failure_reason'] ?? null,
        'failureReason'    => $o['failure_reason'] ?? null,
        'loaded_at'        => $o['loaded_at'] ?? null,
        'created_at'       => $o['created_at'] ?? null,
    ];
}

// استجابة 404 لأي مسار غير معرف
sendJsonResponse(false, 'المسار المطلوب غير موجود في واجهة API', [
    'requested_resource' => $resource,
    'requested_path'     => $path
], 404);
