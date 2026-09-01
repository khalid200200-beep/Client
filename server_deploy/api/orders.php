<?php
require_once __DIR__ . '/../config/db.php';

$rawBody = file_get_contents('php://input');
$input = json_decode($rawBody, true) ?? [];
if (empty($input) && !empty($_POST)) {
    $input = $_POST;
}

$action = $_GET['action'] ?? ($input['action'] ?? '');
if (empty($action) && isset($_GET['phone'])) {
    $action = 'client_orders';
}

switch ($action) {
    // 1. إنشاء طلب شحن جديد من العميل
    case 'create':
    case 'create_order':
        $clientName     = sanitizeInput($input['client_name'] ?? ($input['clientName'] ?? 'عميل'));
        $clientPhone    = sanitizeInput($input['client_phone'] ?? ($input['clientPhone'] ?? ($input['phone'] ?? '')));
        $clientId       = intval($input['client_id'] ?? ($input['clientId'] ?? ($input['user_id'] ?? 0)));
        $city           = sanitizeInput($input['city'] ?? ($input['pickup_city'] ?? ($input['pickupCity'] ?? 'الخرطوم')));
        $pickupAddress  = sanitizeInput($input['pickup_address'] ?? ($input['pickupAddress'] ?? ''));
        $deliveryAddress= sanitizeInput($input['delivery_address'] ?? ($input['deliveryAddress'] ?? ($input['delivery_city'] ?? ($input['deliveryCity'] ?? ''))));
        $packageCount   = max(1, min(100, intval($input['package_count'] ?? ($input['packageCount'] ?? 1))));
        $imagePath      = $input['image_path'] ?? ($input['imagePath'] ?? ($input['image'] ?? ''));
        $notes          = sanitizeInput($input['notes'] ?? 'لا توجد ملاحظات');
        $orderCode      = 'ORD-' . random_int(1000, 9999);

        if (empty($clientPhone)) {
            sendJsonResponse(false, 'رقم جوال العميل مطلوب لإنشاء الطلب', null, 400);
        }

        if ($pdo) {
            // إذا لم يتم تمرير client_id، ابحث عن معرف المستخدم برقم الجوال
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

            $stmt = $pdo->prepare("INSERT INTO orders (order_code, client_id, client_name, client_phone, city, pickup_address, delivery_address, package_count, image_path, notes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')");
            $stmt->execute([$orderCode, ($clientId > 0 ? $clientId : null), $clientName, $clientPhone, $city, $pickupAddress, $deliveryAddress, $packageCount, $imagePath, $notes]);
            $orderId = $pdo->lastInsertId();

            sendJsonResponse(true, 'تم إنشاء طلب الشحن وتوجيهه للمناديب في ' . $city, [
                'id'           => $orderId,
                'order_code'   => $orderCode,
                'client_id'    => $clientId,
                'client_name'  => $clientName,
                'client_phone' => $clientPhone,
                'city'         => $city,
                'status'       => 'pending'
            ], 201);
        } else {
            sendJsonResponse(true, 'تم استلام طلب الشحن بنجاح', [
                'id'         => random_int(10, 999),
                'order_code' => $orderCode,
                'city'       => $city,
                'status'     => 'pending'
            ], 201);
        }
        break;

    // 2. استعراض طلبات العميل
    case 'client_orders':
    case 'get_orders':
        $phone    = sanitizeInput($_GET['phone'] ?? ($input['phone'] ?? ($_GET['client_phone'] ?? ($input['client_phone'] ?? ''))));
        $clientId = intval($_GET['client_id'] ?? ($input['client_id'] ?? ($_GET['user_id'] ?? ($input['user_id'] ?? 0))));

        if ($pdo && (!empty($phone) || $clientId > 0)) {
            $stmt = $pdo->prepare("SELECT * FROM orders WHERE (client_phone = ? AND ? != '') OR (client_id = ? AND ? > 0) ORDER BY id DESC");
            $stmt->execute([$phone, $phone, $clientId, $clientId]);
            $orders = $stmt->fetchAll();
            sendJsonResponse(true, 'تم جلب طلبات العميل بنجاح', $orders);
        } else if ($pdo) {
            $stmt = $pdo->query("SELECT * FROM orders ORDER BY id DESC LIMIT 100");
            $orders = $stmt->fetchAll();
            sendJsonResponse(true, 'أحدث الطلبات', $orders);
        } else {
            sendJsonResponse(true, 'قائمة الطلبات', []);
        }
        break;

    // 3. استعراض الطلبات المتاحة في مدينة السائق
    case 'driver_city_orders':
        $city        = sanitizeInput($_GET['city'] ?? ($input['city'] ?? 'الرياض'));
        $driverPhone = sanitizeInput($_GET['driver_phone'] ?? ($input['driver_phone'] ?? ''));

        // فحص أمني: التحقق من أن السائق مفعل ونشط قبل عرض الشحنات
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
            sendJsonResponse(true, 'تم جلب طلبات المدينة للسائق', $orders);
        } else {
            sendJsonResponse(true, 'قائمة طلبات المدينة', []);
        }
        break;

    // 4. قبول السائق للطلب (مع التحقق الأمني من حالة تفعيل السائق)
    case 'driver_accept':
    case 'accept':
        $orderLookup = $input['order_id'] ?? ($_GET['order_id'] ?? ($input['orderId'] ?? ($input['order_code'] ?? ($input['id'] ?? ''))));
        $driverName  = sanitizeInput($input['driver_name'] ?? ($input['driverName'] ?? 'الكابتن'));
        $driverPhone = sanitizeInput($input['driver_phone'] ?? ($input['driverPhone'] ?? ''));

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

    default:
        sendJsonResponse(false, 'إجراء غير معروف', null, 404);
}
