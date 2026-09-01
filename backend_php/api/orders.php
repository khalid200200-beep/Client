<?php
/**
 * سودرا للشحن والتوصيل - SUDRA EXPRESS
 * وحدة إدارة طلبات الشحن (Orders Controller v3)
 */

require_once __DIR__ . '/../config/db.php';

if (!defined('SUDRA_AUTH_SECRET')) {
    define('SUDRA_AUTH_SECRET', 'SUDRA_SECURE_KEY_2026_PROD_SHIPPING_EXP');
}

function getAuthenticatedUser($pdo = null) {
    $headers = function_exists('getallheaders') ? getallheaders() : [];
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

$authUser = getAuthenticatedUser($pdo);

$rawBody = file_get_contents('php://input');
$input = json_decode($rawBody, true) ?? [];
if (empty($input) && !empty($_POST)) {
    $input = $_POST;
}

$action = $_GET['action'] ?? ($input['action'] ?? '');
if (empty($action) && isset($_GET['phone'])) {
    $action = 'client_orders';
}

function detectImageMimeAndExt($data, $isFilePath = false) {
    $header = $isFilePath ? @file_get_contents($data, false, null, 0, 16) : substr($data, 0, 16);
    if ($header !== false && strlen($header) >= 3) {
        if (str_starts_with($header, "\xFF\xD8\xFF")) return ['mime' => 'image/jpeg', 'ext' => 'jpg'];
        if (str_starts_with($header, "\x89PNG")) return ['mime' => 'image/png', 'ext' => 'png'];
        if (str_starts_with($header, "RIFF") && strpos($header, "WEBP") !== false) return ['mime' => 'image/webp', 'ext' => 'webp'];
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

switch ($action) {
    // 1. إنشاء طلب شحن جديد من العميل مع دعم الصور المتعددة والمعاملة الذرية
    case 'create':
    case 'create_order':
        $clientPhoneInput = sanitizeInput($input['client_phone'] ?? ($input['clientPhone'] ?? ($input['phone'] ?? '')));
        $clientIdInput = intval($input['client_id'] ?? ($input['clientId'] ?? ($input['user_id'] ?? 0)));

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

        if (!$authUser) {
            sendJsonResponse(false, 'تسجيل الدخول كعميل مطلوب لإنشاء طلب الشحن', null, 401);
        }
        if ($authUser['role'] === 'driver') {
            sendJsonResponse(false, 'عذراً! إنشاء طلبات الشحن مخصص للعملاء فقط', null, 403);
        }

        $clientId        = intval($authUser['uid']);
        $clientPhone     = $authUser['phone'];
        $clientName      = !empty($authUser['name']) ? $authUser['name'] : sanitizeInput($input['client_name'] ?? ($input['clientName'] ?? 'عميل'));
        $city            = sanitizeInput($input['city'] ?? ($input['pickup_city'] ?? ($input['pickupCity'] ?? 'الخرطوم')));
        $pickupAddress   = sanitizeInput($input['pickup_address'] ?? ($input['pickupAddress'] ?? ''));
        $deliveryAddress = sanitizeInput($input['delivery_address'] ?? ($input['deliveryAddress'] ?? ($input['delivery_city'] ?? ($input['deliveryCity'] ?? ''))));
        $packageCount    = max(1, min(100, intval($input['package_count'] ?? ($input['packageCount'] ?? 1))));
        $notes           = sanitizeInput($input['notes'] ?? 'لا توجد ملاحظات');
        $orderCode       = 'ORD-' . random_int(100000, 999999);

        // تجميع الصور
        $filesToProcess = [];
        if (!empty($_FILES)) {
            foreach ($_FILES as $fileKey => $fileData) {
                if (is_array($fileData['name'])) {
                    $count = count($fileData['name']);
                    for ($i = 0; $i < $count; $i++) {
                        if ($fileData['error'][$i] === UPLOAD_ERR_OK && !empty($fileData['tmp_name'][$i])) {
                            $filesToProcess[] = ['tmp_name' => $fileData['tmp_name'][$i], 'size' => $fileData['size'][$i]];
                        }
                    }
                } elseif ($fileData['error'] === UPLOAD_ERR_OK && !empty($fileData['tmp_name'])) {
                    $filesToProcess[] = ['tmp_name' => $fileData['tmp_name'], 'size' => $fileData['size']];
                }
            }
        }

        $rawImages = $input['images'] ?? ($input['image_paths'] ?? []);
        if (is_string($rawImages)) {
            $dec = json_decode($rawImages, true);
            if (is_array($dec)) $rawImages = $dec;
            elseif (!empty($rawImages)) $rawImages = [$rawImages];
        }
        if (empty($rawImages) && !empty($input['image_path'])) $rawImages = [$input['image_path']];
        if (empty($rawImages) && !empty($input['imagePath'])) $rawImages = [$input['imagePath']];
        if (empty($rawImages) && !empty($input['image'])) $rawImages = [$input['image']];
        $rawImages = is_array($rawImages) ? $rawImages : [];

        if (count($filesToProcess) + count($rawImages) > 5) {
            sendJsonResponse(false, 'الحد الأقصى المسموح به هو 5 صور للشحنة الواحدة', null, 400);
        }

        if ($pdo) {
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
            if (!is_dir($imgDir)) @mkdir($imgDir, 0755, true);

            $savedFilePaths = [];
            $savedImageUrls = [];
            $allowedMimes = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp'];

            try {
                $pdo->beginTransaction();

                $stmt = $pdo->prepare("INSERT INTO orders (order_code, client_id, client_name, client_phone, city, pickup_address, delivery_address, package_count, image_path, notes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', ?, 'pending')");
                $stmt->execute([$orderCode, ($clientId > 0 ? $clientId : null), $clientName, $clientPhone, $city, $pickupAddress, $deliveryAddress, $packageCount, $notes]);
                $orderId = $pdo->lastInsertId();

                foreach ($filesToProcess as $file) {
                    if ($file['size'] > 5 * 1024 * 1024) throw new Exception('حجم الصورة يتجاوز الحد الأقصى 5 ميجابايت');
                    $detected = detectImageMimeAndExt($file['tmp_name'], true);
                    if (!$detected) throw new Exception('نوع الملف غير مسموح. يرجى رفع صور JPG أو PNG أو WEBP فقط');
                    $ext = $detected['ext'];
                    $fileName = 'order_' . $orderId . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                    $target = $imgDir . $fileName;
                    if (!move_uploaded_file($file['tmp_name'], $target) && !copy($file['tmp_name'], $target)) {
                        throw new Exception('تعذر حفظ ملف الصورة على الخادم');
                    }
                    $savedFilePaths[] = $target;
                    $savedImageUrls[] = 'https://app.sudra.sa/images/orders/' . $fileName;
                }

                foreach ($rawImages as $rawImg) {
                    if (empty($rawImg)) continue;
                    if (preg_match('/^data:image\/(\w+);base64,/', $rawImg, $type)) {
                        $data = substr($rawImg, strpos($rawImg, ',') + 1);
                        $binary = base64_decode($data);
                        if ($binary === false || strlen($binary) > 5 * 1024 * 1024) throw new Exception('بيانات الصورة تالفة أو تتجاوز 5 ميجابايت');
                        $detected = detectImageMimeAndExt($binary, false);
                        if (!$detected) throw new Exception('نوع الصورة غير مسموح (JPG, PNG, WEBP فقط)');
                        $ext = $detected['ext'];
                        $fileName = 'order_' . $orderId . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                        $target = $imgDir . $fileName;
                        if (@file_put_contents($target, $binary) === false) throw new Exception('تعذر حفظ الصورة على الخادم');
                        $savedFilePaths[] = $target;
                        $savedImageUrls[] = 'https://app.sudra.sa/images/orders/' . $fileName;
                    } elseif (filter_var($rawImg, FILTER_VALIDATE_URL) || strpos($rawImg, 'images/') !== false) {
                        $savedImageUrls[] = $rawImg;
                    }
                }

                $firstImg = !empty($savedImageUrls) ? $savedImageUrls[0] : '';
                if (!empty($savedImageUrls)) {
                    $ins = $pdo->prepare("INSERT INTO order_images (order_id, image_path) VALUES (?, ?)");
                    foreach ($savedImageUrls as $u) {
                        $ins->execute([$orderId, $u]);
                    }
                    $pdo->prepare("UPDATE orders SET image_path = ? WHERE id = ?")->execute([$firstImg, $orderId]);
                }

                $pdo->commit();

                sendJsonResponse(true, 'تم إنشاء طلب الشحن وتوجيهه للمناديب في ' . $city, [
                    'id'           => $orderId,
                    'order_code'   => $orderCode,
                    'client_id'    => $clientId,
                    'client_name'  => $clientName,
                    'client_phone' => $clientPhone,
                    'city'         => $city,
                    'status'       => 'pending',
                    'images'       => $savedImageUrls,
                    'image_path'   => $firstImg
                ], 201);
            } catch (Throwable $e) {
                if ($pdo && $pdo->inTransaction()) $pdo->rollBack();
                foreach ($savedFilePaths as $fp) {
                    if (file_exists($fp)) @unlink($fp);
                }
                sendJsonResponse(false, $e->getMessage(), null, 400);
            }
        } else {
            sendJsonResponse(true, 'تم استلام طلب الشحن بنجاح', [
                'id'         => random_int(10, 999),
                'order_code' => $orderCode,
                'city'       => $city,
                'status'     => 'pending',
                'images'     => []
            ], 201);
        }
        break;

    // 2. استعراض طلبات العميل مع عزل أمني تام للحسابات
    case 'client_orders':
    case 'get_orders':
        if (!$authUser) {
            sendJsonResponse(false, 'تسجيل الدخول والتوكن مطلوب لعرض قائمة الطلبات', null, 401);
        }

        $phone    = sanitizeInput($_GET['phone'] ?? ($input['phone'] ?? ($_GET['client_phone'] ?? ($input['client_phone'] ?? ''))));
        $clientId = intval($_GET['client_id'] ?? ($input['client_id'] ?? ($_GET['user_id'] ?? ($input['user_id'] ?? 0))));

        // فرض هوية العميل من التوكن لمنع IDOR والتلاعب
        if ($authUser['role'] === 'client') {
            $clientId = intval($authUser['uid']);
            $phone = $authUser['phone'];
        }

        if ($pdo && (!empty($phone) || $clientId > 0)) {
            $cleanDigits = preg_replace('/[^0-9]/', '', $phone);
            $altPhone1 = !empty($cleanDigits) ? ltrim($cleanDigits, '0') : $phone;
            $altPhone2 = !empty($cleanDigits) ? '0' . $altPhone1 : $phone;

            if ($clientId > 0 && !empty($phone)) {
                $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_id = ? OR client_phone = ? OR client_phone = ? OR client_phone = ? ORDER BY id DESC");
                $stmt->execute([$clientId, $phone, $altPhone1, $altPhone2]);
            } elseif ($clientId > 0) {
                $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_id = ? ORDER BY id DESC");
                $stmt->execute([$clientId]);
            } else {
                $stmt = $pdo->prepare("SELECT * FROM orders WHERE client_phone = ? OR client_phone = ? OR client_phone = ? ORDER BY id DESC");
                $stmt->execute([$phone, $altPhone1, $altPhone2]);
            }

            $orders = $stmt->fetchAll();
            foreach ($orders as &$o) {
                $o['images'] = fetchOrderImages($o['id'], $pdo, $o['image_path'] ?? '');
            }
            sendJsonResponse(true, 'تم جلب طلبات العميل بنجاح', $orders);
        } else {
            // أمان تام: لا يتم إرجاع طلبات أي عميل آخر إطلاقاً، بل قائمة فارغة
            sendJsonResponse(true, 'لا توجد طلبات سابقة', []);
        }
        break;

    // 3. استعراض الطلبات المتاحة في مدينة السائق
    case 'driver_city_orders':
        $city        = sanitizeInput($_GET['city'] ?? ($input['city'] ?? 'الرياض'));
        $driverPhone = sanitizeInput($_GET['driver_phone'] ?? ($input['driver_phone'] ?? ''));

        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'غير مصرح للعميل باستعراض قائمة طلبات السائقين', null, 403);
        }

        if ($pdo && !empty($driverPhone)) {
            $chk = $pdo->prepare("SELECT is_active FROM users WHERE phone = ? AND role = 'driver' LIMIT 1");
            $chk->execute([$driverPhone]);
            $drv = $chk->fetch();
            if ($drv && empty($drv['is_active'])) {
                sendJsonResponse(false, 'حسابك قيد المراجعة أو موقوف من الإدارة ولا يمكنك استقبال الطلبات', null, 403);
            }
        }

        if ($pdo) {
            $stmt = $pdo->prepare("SELECT * FROM orders WHERE (city = ? OR ? = '') AND status = 'pending' ORDER BY id DESC");
            $stmt->execute([$city, $city]);
            $orders = $stmt->fetchAll();
            foreach ($orders as &$o) {
                $o['images'] = fetchOrderImages($o['id'], $pdo, $o['image_path'] ?? '');
            }
            sendJsonResponse(true, 'تم جلب طلبات المدينة للسائق', $orders);
        } else {
            sendJsonResponse(true, 'قائمة طلبات المدينة', []);
        }
        break;

    // 4. قبول السائق للطلب
    case 'driver_accept':
    case 'accept':
        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'عذراً! هذا الإجراء مخصص للسائقين فقط', null, 403);
        }

        $orderLookup = $input['order_id'] ?? ($_GET['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['id'] ?? ''))));
        $driverName  = sanitizeInput($input['driver_name'] ?? ($input['driverName'] ?? 'الكابتن'));
        $driverPhone = sanitizeInput($input['driver_phone'] ?? ($input['driverPhone'] ?? ''));

        if ($authUser && $authUser['role'] === 'driver') {
            $driverPhone = $authUser['phone'];
            if (!empty($authUser['name']) && $driverName === 'الكابتن') {
                $driverName = $authUser['name'];
            }
        }

        if (empty($orderLookup) || empty($driverPhone)) {
            sendJsonResponse(false, 'بيانات الطلب والسائق مطلوبة', null, 400);
        }

        if ($pdo) {
            $chk = $pdo->prepare("SELECT is_active FROM users WHERE phone = ? AND role = 'driver' LIMIT 1");
            $chk->execute([$driverPhone]);
            $drv = $chk->fetch();

            if ($drv && empty($drv['is_active'])) {
                sendJsonResponse(false, 'عذراً! حسابك موقوف أو بانتظار التفعيل من قبل الإدارة', null, 403);
            }

            if (is_numeric($orderLookup)) {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'accepted', driver_name = ?, driver_phone = ? WHERE id = ? AND status = 'pending'");
                $stmt->execute([$driverName, $driverPhone, intval($orderLookup)]);
            } else {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'accepted', driver_name = ?, driver_phone = ? WHERE order_code = ? AND status = 'pending'");
                $stmt->execute([$driverName, $driverPhone, $orderLookup]);
            }

            if ($stmt->rowCount() > 0) {
                sendJsonResponse(true, 'تم قبول الطلب بنجاح، توجه الآن لموقع العميل');
            } else {
                sendJsonResponse(false, 'الطلب غير متاح أو تم قبوله من سائق آخر', null, 409);
            }
        } else {
            sendJsonResponse(true, 'تم قبول الطلب بنجاح');
        }
        break;

    // 5. تأكيد تم التحميل من العميل بنجاح
    case 'driver_loaded':
    case 'loaded':
        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'عذراً! هذا الإجراء مخصص للسائقين فقط', null, 403);
        }

        $orderLookup     = $input['order_id'] ?? ($_GET['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['id'] ?? ''))));
        $collectedAmount = floatval($input['collectedAmount'] ?? ($input['collected_amount'] ?? 0.00));

        if (empty($orderLookup)) {
            sendJsonResponse(false, 'معرف الطلب غير صحيح', null, 400);
        }

        if ($pdo) {
            if (is_numeric($orderLookup)) {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'loaded', collected_amount = ?, loaded_at = NOW() WHERE id = ? AND status = 'accepted'");
                $stmt->execute([$collectedAmount, intval($orderLookup)]);
            } else {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'loaded', collected_amount = ?, loaded_at = NOW() WHERE order_code = ? AND status = 'accepted'");
                $stmt->execute([$collectedAmount, $orderLookup]);
            }
            sendJsonResponse(true, 'تم تسجيل تحميل الشحنة بنجاح وجاري التوصيل');
        } else {
            sendJsonResponse(true, 'تم تسجيل التحميل بنجاح');
        }
        break;

    // 6. تأكيد تسليم الشحنة
    case 'driver_delivered':
    case 'delivered':
        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'عذراً! هذا الإجراء مخصص للسائقين فقط', null, 403);
        }

        $orderLookup = $input['order_id'] ?? ($_GET['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['id'] ?? ''))));
        if (empty($orderLookup)) {
            sendJsonResponse(false, 'معرف الطلب غير صحيح', null, 400);
        }

        if ($pdo) {
            if (is_numeric($orderLookup)) {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'delivered' WHERE id = ?");
                $stmt->execute([intval($orderLookup)]);
            } else {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'delivered' WHERE order_code = ?");
                $stmt->execute([$orderLookup]);
            }
            sendJsonResponse(true, 'تم تسليم الشحنة للعميل بنجاح');
        } else {
            sendJsonResponse(true, 'تم تسليم الشحنة بنجاح');
        }
        break;

    // 7. تعذر الشحن وتوثيق السبب
    case 'driver_failed':
    case 'failed':
        if ($authUser && $authUser['role'] === 'client') {
            sendJsonResponse(false, 'عذراً! هذا الإجراء مخصص للسائقين فقط', null, 403);
        }

        $orderLookup = $input['order_id'] ?? ($_GET['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['id'] ?? ''))));
        $reason      = sanitizeInput($input['reason'] ?? ($input['failureReason'] ?? ($input['failure_reason'] ?? 'تعذر التواصل مع العميل')));

        if (empty($orderLookup)) {
            sendJsonResponse(false, 'معرف الطلب غير صحيح', null, 400);
        }

        if ($pdo) {
            if (is_numeric($orderLookup)) {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'failed', failure_reason = ? WHERE id = ?");
                $stmt->execute([$reason, intval($orderLookup)]);
            } else {
                $stmt = $pdo->prepare("UPDATE orders SET status = 'failed', failure_reason = ? WHERE order_code = ?");
                $stmt->execute([$reason, $orderLookup]);
            }
            sendJsonResponse(true, 'تم تسجيل تعذر الشحن وتوثيقه للإدارة');
        } else {
            sendJsonResponse(true, 'تم تسجيل تعذر الشحن بنجاح');
        }
        break;

    // 8. حذف الطلب
    case 'delete':
    case 'delete_order':
        $orderLookup = $input['order_id'] ?? ($_GET['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['id'] ?? ''))));
        if ($pdo && !empty($orderLookup)) {
            $targetId = 0;
            if (is_numeric($orderLookup)) {
                $targetId = intval($orderLookup);
            } else {
                $s = $pdo->prepare("SELECT id FROM orders WHERE order_code = ? LIMIT 1");
                $s->execute([$orderLookup]);
                $r = $s->fetch();
                if ($r) $targetId = intval($r['id']);
            }

            if ($targetId > 0) {
                $imgStmt = $pdo->prepare("SELECT image_path FROM order_images WHERE order_id = ?");
                $imgStmt->execute([$targetId]);
                $imgs = $imgStmt->fetchAll(PDO::FETCH_COLUMN);
                foreach ($imgs as $imgPath) {
                    $basename = basename(parse_url($imgPath, PHP_URL_PATH));
                    $localFile = __DIR__ . '/../images/orders/' . $basename;
                    if (file_exists($localFile)) @unlink($localFile);
                }
                $stmt = $pdo->prepare("DELETE FROM orders WHERE id = ?");
                $stmt->execute([$targetId]);
                sendJsonResponse(true, 'تم حذف الطلب وكافة صوره بنجاح');
            } else {
                sendJsonResponse(false, 'الطلب غير موجود', null, 404);
            }
        } else {
            sendJsonResponse(false, 'معرف الطلب مطلوب', null, 400);
        }
        break;

    default:
        sendJsonResponse(false, 'إجراء غير معروف', null, 404);
}
