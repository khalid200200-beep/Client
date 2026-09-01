<?php
session_start([
    'cookie_httponly' => true,
    'cookie_samesite' => 'Strict'
]);
require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../config/mail.php';

$admin_name = $_SESSION['admin_name'] ?? 'مدير النظام';
$csrf_token = generateCsrfToken();

// معالجة حفظ إعدادات البريد ومزود SMTP
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_mail_settings'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $saved = saveMailSettings($_POST);
    header("Location: index.php?tab=mail_settings&msg=" . ($saved ? "mail_saved" : "mail_error"));
    exit();
}

// معالجة اختبار اتصال البريد
$mail_test_output = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test_mail_action'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $test_email = filter_var(trim($_POST['test_email'] ?? ''), FILTER_VALIDATE_EMAIL);
    if ($test_email) {
        $mail_test_output = testSmtpConnection($test_email);
    } else {
        $mail_test_output = ['success' => false, 'message' => 'البريد الإلكتروني المدخل للاختبار غير صالح'];
    }
}

// معالجة تغيير حالة الشحنة (محمية بـ CSRF)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['update_status'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $order_id = intval($_POST['order_id']);
    $new_status = sanitizeInput($_POST['new_status']);
    $allowed_statuses = ['pending', 'accepted', 'loaded', 'failed'];

    if ($pdo && in_array($new_status, $allowed_statuses, true)) {
        $stmt = $pdo->prepare("UPDATE orders SET status = ? WHERE id = ?");
        $stmt->execute([$new_status, $order_id]);
    }
    header("Location: index.php?msg=order_updated");
    exit();
}

// معالجة تشغيل أو إيقاف حساب السائق (محمية بـ POST و CSRF لمنع هجمات GET CSRF)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['toggle_driver_action'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $driver_id = intval($_POST['driver_id']);
    $new_active_state = intval($_POST['set_state']) === 1 ? 1 : 0;
    if ($pdo && $driver_id > 0) {
        $stmt = $pdo->prepare("UPDATE users SET is_active = ? WHERE id = ? AND role = 'driver'");
        $stmt->execute([$new_active_state, $driver_id]);
    }
    header("Location: index.php?tab=drivers&msg=driver_status_changed");
    exit();
}

// معالجة إضافة مستخدم جديد (محمية بـ CSRF)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['add_user'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $name = sanitizeInput($_POST['u_name']);
    $phone = sanitizeInput($_POST['u_phone']);
    $city = sanitizeInput($_POST['u_city']);
    $role = in_array($_POST['u_role'], ['client', 'driver']) ? $_POST['u_role'] : 'client';
    $plate = sanitizeInput($_POST['u_plate'] ?? '');
    $is_active = ($role === 'driver') ? 0 : 1;
    $pass = password_hash('123456', PASSWORD_DEFAULT);

    if ($pdo && !empty($name) && !empty($phone)) {
        $stmt = $pdo->prepare("INSERT INTO users (name, phone, city, vehicle_plate, password, role, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)");
        $stmt->execute([$name, $phone, $city, $plate, $pass, $role, $is_active]);
    }
    header("Location: index.php?tab=" . ($role === 'driver' ? 'drivers' : 'clients') . "&msg=user_added");
    exit();
}

// معالجة حذف مستخدم (محمية بـ POST و CSRF)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete_user_action'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $uid = intval($_POST['user_id']);
    if ($pdo && $uid > 0) {
        $stmt = $pdo->prepare("DELETE FROM users WHERE id = ?");
        $stmt->execute([$uid]);
    }
    header("Location: index.php?msg=user_deleted");
    exit();
}

// معالجة إضافة بانر جديد (محمية بـ CSRF)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['add_banner'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $title = sanitizeInput($_POST['title']);
    $subtitle = sanitizeInput($_POST['subtitle']);
    $badge = sanitizeInput($_POST['badge_text']);
    $image_url = filter_var($_POST['image_url'], FILTER_SANITIZE_URL);
    $button_text = sanitizeInput($_POST['button_text']) ?: 'اطلب شحن الآن';
    
    // التحقق من صحة رابط الصورة وأنه يبدأ بـ http/https لمنع XSS / javascript: URIs
    if ($pdo && !empty($title) && preg_match('/^https?:\/\//i', $image_url)) {
        $stmt = $pdo->prepare("INSERT INTO banners (title, subtitle, badge_text, image_url, button_text) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([$title, $subtitle, $badge, $image_url, $button_text]);
    }
    header("Location: index.php?tab=banners&msg=banner_added");
    exit();
}

// معالجة حذف بانر (محمية بـ POST و CSRF)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete_banner_action'])) {
    if (!verifyCsrfToken($_POST['csrf_token'] ?? '')) {
        die('خطأ أمني: طلب غير مصرح به (Invalid CSRF Token)');
    }
    $banner_id = intval($_POST['banner_id']);
    if ($pdo && $banner_id > 0) {
        $stmt = $pdo->prepare("DELETE FROM banners WHERE id = ?");
        $stmt->execute([$banner_id]);
    }
    header("Location: index.php?tab=banners&msg=banner_deleted");
    exit();
}

// جلب البيانات من MySQL مع التجهيز الآمن
$orders = [];
$clients = [];
$drivers = [];
$banners = [];
$stats = ['total' => 0, 'pending' => 0, 'accepted' => 0, 'loaded' => 0, 'failed' => 0, 'clients_count' => 0, 'drivers_count' => 0, 'pending_drivers' => 0];

if ($pdo) {
    $stmt = $pdo->query("SELECT * FROM orders ORDER BY id DESC");
    $orders = $stmt->fetchAll();

    $uStmt = $pdo->query("SELECT * FROM users ORDER BY id DESC");
    $allUsers = $uStmt->fetchAll();
    $clients = array_filter($allUsers, fn($u) => $u['role'] === 'client');
    $drivers = array_filter($allUsers, fn($u) => $u['role'] === 'driver');

    $bStmt = $pdo->query("SELECT * FROM banners ORDER BY id DESC");
    $banners = $bStmt->fetchAll();

    $stats['total']           = count($orders);
    $stats['pending']         = count(array_filter($orders, fn($o) => $o['status'] === 'pending'));
    $stats['accepted']        = count(array_filter($orders, fn($o) => $o['status'] === 'accepted'));
    $stats['loaded']          = count(array_filter($orders, fn($o) => $o['status'] === 'loaded'));
    $stats['failed']          = count(array_filter($orders, fn($o) => $o['status'] === 'failed'));
    $stats['clients_count']   = count($clients);
    $stats['drivers_count']   = count($drivers);
    $stats['pending_drivers'] = count(array_filter($drivers, fn($d) => empty($d['is_active']) || $d['is_active'] == 0));
} else {
    $orders = [
        ['id' => 1, 'order_code' => 'ORD-9821', 'client_name' => 'خالد', 'client_phone' => '0551234567', 'city' => 'الرياض', 'package_count' => 3, 'notes' => 'يرجى التعامل بحذر', 'status' => 'pending', 'driver_name' => null, 'failure_reason' => null],
        ['id' => 2, 'order_code' => 'ORD-8714', 'client_name' => 'سارة العتيبي', 'client_phone' => '0542233445', 'city' => 'الرياض', 'package_count' => 1, 'notes' => 'عند البوابة الرئيسية', 'status' => 'accepted', 'driver_name' => 'أحمد كابتن التوصيل', 'failure_reason' => null],
    ];
    $clients = [
        ['id' => 1, 'name' => 'خالد العميل', 'phone' => '0551234567', 'city' => 'الرياض'],
        ['id' => 2, 'name' => 'سارة العتيبي', 'phone' => '0542233445', 'city' => 'الرياض']
    ];
    $drivers = [
        ['id' => 3, 'name' => 'أحمد كابتن التوصيل', 'phone' => '0509876543', 'city' => 'الرياض', 'vehicle_plate' => 'أ ب ج 1234', 'is_active' => 1],
        ['id' => 4, 'name' => 'سعيد القحطاني', 'phone' => '0561122334', 'city' => 'جدة', 'vehicle_plate' => 'س ع د 5678', 'is_active' => 0]
    ];
    $banners = [
        ['id' => 1, 'title' => 'شحنك يصل إليك', 'subtitle' => 'بسرعة • أمان • موثوقية', 'badge_text' => 'الأكثر طلباً', 'image_url' => 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800', 'button_text' => 'اطلب شحن الآن'],
    ];
    $stats = ['total' => 2, 'pending' => 1, 'accepted' => 1, 'loaded' => 0, 'failed' => 0, 'clients_count' => 2, 'drivers_count' => 2, 'pending_drivers' => 1];
}
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم المحصنة أمنياً | منظومة الشحن</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #E51D24;
            --dark: #1E242B;
            --bg: #F4F6F9;
            --card: #FFFFFF;
            --text-muted: #8A94A6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg); color: var(--dark); padding: 24px; }
        .container { max-width: 1280px; margin: 0 auto; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; background: #fff; padding: 16px 24px; border-radius: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); }
        .header h1 { font-size: 22px; font-weight: 900; display: flex; align-items: center; gap: 10px; }
        .header-actions { display: flex; align-items: center; gap: 14px; }
        .user-info { font-size: 13px; font-weight: 700; }
        .btn-logout { background: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; padding: 8px 16px; border-radius: 12px; font-size: 13px; font-weight: 800; text-decoration: none; }

        .tabs-nav { display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 4px; }
        .tab-btn { background: #fff; border: 1.5px solid #E2E8F0; padding: 10px 20px; border-radius: 14px; font-size: 13.5px; font-weight: 800; cursor: pointer; color: #475569; }
        .tab-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); box-shadow: 0 4px 12px rgba(229, 29, 36, 0.25); }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px; }
        .stat-box { background: var(--card); padding: 18px; border-radius: 18px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); border-bottom: 4px solid transparent; }
        .stat-box.primary { border-color: var(--primary); }
        .stat-box.warning { border-color: #F59E0B; }
        .stat-box.info { border-color: #3B82F6; }
        .stat-box.success { border-color: #10B981; }
        .stat-box.danger { border-color: #EF4444; }
        .stat-num { font-size: 26px; font-weight: 900; display: block; margin-top: 4px; }
        .stat-label { font-size: 12px; color: var(--text-muted); font-weight: 600; }

        .card { background: var(--card); border-radius: 20px; padding: 24px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); margin-bottom: 24px; }
        .card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
        .card-head h3 { font-size: 18px; font-weight: 800; }

        .form-box { background: #F8FAFC; padding: 18px; border-radius: 16px; margin-bottom: 20px; }
        .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 14px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-group label { font-size: 12.5px; font-weight: 700; }
        .form-input { padding: 10px 14px; border: 1px solid #CBD5E1; border-radius: 10px; font-size: 13px; font-family: inherit; }
        .btn-submit { background: var(--primary); color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 800; cursor: pointer; }
        
        .btn-activate { background: #16A34A; color: #fff; border: none; font-size: 12px; font-weight: 800; padding: 6px 12px; border-radius: 8px; cursor: pointer; }
        .btn-pause { background: #DC2626; color: #fff; border: none; font-size: 12px; font-weight: 800; padding: 6px 12px; border-radius: 8px; cursor: pointer; }
        .btn-delete { color: #DC2626; background: none; border: 1px solid #FCA5A5; font-size: 12px; font-weight: 700; padding: 5px 8px; border-radius: 6px; cursor: pointer; }

        table { width: 100%; border-collapse: collapse; text-align: right; }
        th { background: #F8FAFC; padding: 14px 16px; font-size: 13px; color: var(--text-muted); font-weight: 700; border-radius: 8px; }
        td { padding: 16px; border-bottom: 1px solid #F1F5F9; font-size: 13.5px; }
        tr:hover td { background: #FAFAFA; }

        .status-badge { padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; display: inline-block; }
        .status-loaded { background: #D1FAE5; color: #065F46; }
        .status-pending { background: #FEF3C7; color: #B45309; }
        .status-paused { background: #FEE2E2; color: #991B1B; }

        .banners-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 16px; }
        .banner-item { border: 1px solid #E2E8F0; border-radius: 18px; overflow: hidden; background: #fff; }
        .banner-img-preview { width: 100%; height: 130px; object-fit: cover; }
        .banner-info { padding: 14px; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>
            🛡️ لوحة التحكم والإدارة (محصنة بنظام الحماية السيبراني)
        </h1>
        <div class="header-actions">
            <div class="user-info"><span>👤 مرحباً، <?php echo htmlspecialchars($admin_name, ENT_QUOTES, 'UTF-8'); ?></span></div>
            <a href="logout.php" class="btn-logout">تسجيل الخروج 🚪</a>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-nav">
        <button class="tab-btn active" onclick="showTab('orders')">📦 سجل الشحنات المباشر</button>
        <button class="tab-btn" onclick="showTab('drivers')">
            🚚 إدارة واعتماد السائقين 
            <?php if($stats['pending_drivers'] > 0): ?>
                <span style="background:#EF4444; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px;"><?php echo $stats['pending_drivers']; ?> بانتظار الاعتماد</span>
            <?php endif; ?>
        </button>
        <button class="tab-btn" onclick="showTab('clients')">👥 إدارة حسابات العملاء (<?php echo $stats['clients_count']; ?>)</button>
        <button class="tab-btn" onclick="showTab('banners')">🖼️ إدارة بانرات السلايدر</button>
        <button class="tab-btn" id="btn-mail_settings" onclick="showTab('mail_settings')">📧 إعدادات مزود البريد</button>
    </div>

    <!-- KPI Statistics -->
    <div class="stats-grid">
        <div class="stat-box primary"><span class="stat-label">إجمالي الشحنات</span><span class="stat-num"><?php echo $stats['total']; ?></span></div>
        <div class="stat-box warning"><span class="stat-label">بانتظار سائق</span><span class="stat-num"><?php echo $stats['pending']; ?></span></div>
        <div class="stat-box info"><span class="stat-label">مقبولة من الكابتن</span><span class="stat-num"><?php echo $stats['accepted']; ?></span></div>
        <div class="stat-box success"><span class="stat-label">تم التحميل ✅</span><span class="stat-num"><?php echo $stats['loaded']; ?></span></div>
        <div class="stat-box danger"><span class="stat-label">سائقين بانتظار التفعيل</span><span class="stat-num"><?php echo $stats['pending_drivers']; ?></span></div>
        <div class="stat-box info"><span class="stat-label">كباتن معتمدين</span><span class="stat-num"><?php echo ($stats['drivers_count'] - $stats['pending_drivers']); ?></span></div>
    </div>

    <!-- TAB 1: ORDERS -->
    <div class="tab-content active" id="tab-orders">
        <div class="card">
            <div class="card-head"><h3>سجل وحالات الشحنات المباشرة</h3></div>
            <table>
                <thead>
                    <tr>
                        <th>كود الشحنة</th>
                        <th>العميل</th>
                        <th>رقم الجوال</th>
                        <th>المدينة</th>
                        <th>عدد القطع</th>
                        <th>السائق المعين</th>
                        <th>الملاحظات / سبب التعذر</th>
                        <th>الحالة</th>
                        <th>تعديل وتحديث</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($orders as $o): ?>
                    <tr>
                        <td><strong>#<?php echo htmlspecialchars($o['order_code'], ENT_QUOTES, 'UTF-8'); ?></strong></td>
                        <td><?php echo htmlspecialchars($o['client_name'], ENT_QUOTES, 'UTF-8'); ?></td>
                        <td><?php echo htmlspecialchars($o['client_phone'], ENT_QUOTES, 'UTF-8'); ?></td>
                        <td><?php echo htmlspecialchars($o['city'], ENT_QUOTES, 'UTF-8'); ?> 📍</td>
                        <td><strong><?php echo intval($o['package_count']); ?></strong></td>
                        <td><?php echo !empty($o['driver_name']) ? '🚚 ' . htmlspecialchars($o['driver_name'], ENT_QUOTES, 'UTF-8') : '-'; ?></td>
                        <td><?php echo !empty($o['failure_reason']) ? '<span style="color:#DC2626; font-weight:700;">تعذر: ' . htmlspecialchars($o['failure_reason'], ENT_QUOTES, 'UTF-8') . '</span>' : htmlspecialchars($o['notes'] ?? '', ENT_QUOTES, 'UTF-8'); ?></td>
                        <td><span class="status-badge status-<?php echo htmlspecialchars($o['status'], ENT_QUOTES, 'UTF-8'); ?>"><?php echo htmlspecialchars($o['status'], ENT_QUOTES, 'UTF-8'); ?></span></td>
                        <td>
                            <form method="POST" style="display:flex; gap:6px;">
                                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                                <input type="hidden" name="order_id" value="<?php echo intval($o['id']); ?>">
                                <select name="new_status" class="form-input" style="padding:4px 8px; font-size:12px;">
                                    <option value="pending" <?php if($o['status']=='pending') echo 'selected'; ?>>بانتظار سائق</option>
                                    <option value="accepted" <?php if($o['status']=='accepted') echo 'selected'; ?>>تم القبول</option>
                                    <option value="loaded" <?php if($o['status']=='loaded') echo 'selected'; ?>>تم التحميل</option>
                                    <option value="failed" <?php if($o['status']=='failed') echo 'selected'; ?>>تعذر الشحن</option>
                                </select>
                                <button type="submit" name="update_status" class="btn-submit" style="padding:6px 12px; font-size:12px;">حفظ</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>

    <!-- TAB 2: DRIVERS (WITH SECURE CSRF ACTIVATION & SUSPENSION) -->
    <div class="tab-content" id="tab-drivers">
        <div class="card">
            <div class="card-head">
                <h3>🚚 إدارة واعتماد وتفعيل حسابات السائقين والكباتن</h3>
                <span style="font-size:12px; color:var(--text-muted);">تحكم آمن ومباشر لمنع أي سائق غير معتمد من العمل</span>
            </div>

            <!-- إضافة سائق جديد -->
            <form method="POST" class="form-box">
                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="u_role" value="driver">
                <h4 style="font-size:14px; margin-bottom:12px;">+ تسجيل حساب كابتن جديد</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label>اسم الكابتن</label>
                        <input type="text" name="u_name" class="form-input" placeholder="مثال: صالح القحطاني" required>
                    </div>
                    <div class="form-group">
                        <label>رقم الجوال</label>
                        <input type="text" name="u_phone" class="form-input" placeholder="05xxxxxxxx" required>
                    </div>
                    <div class="form-group">
                        <label>نطاق التغطية (المدينة)</label>
                        <input type="text" name="u_city" class="form-input" value="الرياض" required>
                    </div>
                    <div class="form-group">
                        <label>لوحة المركبة</label>
                        <input type="text" name="u_plate" class="form-input" placeholder="د هـ و 7890">
                    </div>
                </div>
                <button type="submit" name="add_user" class="btn-submit" style="background:#2563EB;">+ تسجيل الكابتن (قيد المراجعة)</button>
            </form>

            <table>
                <thead>
                    <tr>
                        <th>اسم الكابتن</th>
                        <th>رقم الجوال</th>
                        <th>نطاق المدينة</th>
                        <th>لوحة المركبة</th>
                        <th>حالة الحساب</th>
                        <th>التحكم والتشغيل</th>
                        <th>إجراء</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($drivers as $d): 
                        $isActive = !empty($d['is_active']) && $d['is_active'] == 1;
                    ?>
                    <tr>
                        <td><strong>🚚 <?php echo htmlspecialchars($d['name'], ENT_QUOTES, 'UTF-8'); ?></strong></td>
                        <td><?php echo htmlspecialchars($d['phone'], ENT_QUOTES, 'UTF-8'); ?></td>
                        <td><?php echo htmlspecialchars($d['city'], ENT_QUOTES, 'UTF-8'); ?> 📍</td>
                        <td><strong><?php echo htmlspecialchars($d['vehicle_plate'] ?? 'أ ب ج 1234', ENT_QUOTES, 'UTF-8'); ?></strong></td>
                        <td>
                            <?php if ($isActive): ?>
                                <span class="status-badge status-loaded">معتمد ونشط (يستقبل الطلبات) ✅</span>
                            <?php else: ?>
                                <span class="status-badge status-paused">موقوف / بانتظار الاعتماد ⛔</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <form method="POST" style="display:inline;">
                                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                                <input type="hidden" name="driver_id" value="<?php echo intval($d['id']); ?>">
                                <input type="hidden" name="set_state" value="<?php echo $isActive ? '0' : '1'; ?>">
                                <?php if ($isActive): ?>
                                    <button type="submit" name="toggle_driver_action" class="btn-pause" onclick="return confirm('إيقاف حساب هذا السائق عن استقبال الطلبات؟');">⛔ إيقاف الحساب</button>
                                <?php else: ?>
                                    <button type="submit" name="toggle_driver_action" class="btn-activate" onclick="return confirm('اعتماد وتشغيل حساب السائق لاستقبال الطلبات؟');">✅ تفعيل وتشغيل الحساب</button>
                                <?php endif; ?>
                            </form>
                        </td>
                        <td>
                            <form method="POST" style="display:inline;">
                                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                                <input type="hidden" name="user_id" value="<?php echo intval($d['id']); ?>">
                                <button type="submit" name="delete_user_action" class="btn-delete" onclick="return confirm('حذف حساب السائق نهائياً؟');">حذف 🗑️</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>

    <!-- TAB 3: CLIENTS -->
    <div class="tab-content" id="tab-clients">
        <div class="card">
            <div class="card-head"><h3>👥 إدارة حسابات العملاء</h3></div>
            <form method="POST" class="form-box">
                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="u_role" value="client">
                <h4 style="font-size:14px; margin-bottom:12px;">+ إضافة حساب عميل جديد</h4>
                <div class="form-row">
                    <div class="form-group"><label>اسم العميل</label><input type="text" name="u_name" class="form-input" placeholder="خالد محمد" required></div>
                    <div class="form-group"><label>رقم الجوال</label><input type="text" name="u_phone" class="form-input" placeholder="05xxxxxxxx" required></div>
                    <div class="form-group"><label>المدينة</label><input type="text" name="u_city" class="form-input" value="الرياض" required></div>
                </div>
                <button type="submit" name="add_user" class="btn-submit">+ إنشاء حساب العميل</button>
            </form>

            <table>
                <thead>
                    <tr><th>الاسم</th><th>رقم الجوال</th><th>المدينة</th><th>الدور</th><th>الحالة</th><th>إجراء</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($clients as $c): ?>
                    <tr>
                        <td><strong>👤 <?php echo htmlspecialchars($c['name'], ENT_QUOTES, 'UTF-8'); ?></strong></td>
                        <td><?php echo htmlspecialchars($c['phone'], ENT_QUOTES, 'UTF-8'); ?></td>
                        <td><?php echo htmlspecialchars($c['city'], ENT_QUOTES, 'UTF-8'); ?> 📍</td>
                        <td><span style="color:#2563EB; font-weight:700;">عميل</span></td>
                        <td><span class="status-badge status-loaded">نشط ✅</span></td>
                        <td>
                            <form method="POST" style="display:inline;">
                                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                                <input type="hidden" name="user_id" value="<?php echo intval($c['id']); ?>">
                                <button type="submit" name="delete_user_action" class="btn-delete" onclick="return confirm('حذف هذا الحساب نهائياً؟');">حذف 🗑️</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>

    <!-- TAB 4: BANNERS -->
    <div class="tab-content" id="tab-banners">
        <div class="card">
            <div class="card-head"><h3>🖼️ إدارة وتغيير بانرات وسلايدر الواجهة الرئيسية</h3></div>
            <form method="POST" class="form-box">
                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                <h4 style="font-size:14px; margin-bottom:12px;">+ إضافة بانر وعرض جديد</h4>
                <div class="form-row">
                    <div class="form-group"><label>عنوان البانر</label><input type="text" name="title" class="form-input" required></div>
                    <div class="form-group"><label>الوصف الفرعي</label><input type="text" name="subtitle" class="form-input" required></div>
                    <div class="form-group"><label>الشارة</label><input type="text" name="badge_text" class="form-input" value="عرض مميز 🔥"></div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="grid-column: span 2;"><label>رابط الصورة</label><input type="url" name="image_url" class="form-input" value="https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=800" required></div>
                    <div class="form-group"><label>نص الزر</label><input type="text" name="button_text" class="form-input" value="اطلب شحن الآن"></div>
                </div>
                <button type="submit" name="add_banner" class="btn-submit">حفظ ونشر البانر 🚀</button>
            </form>

            <div class="banners-grid">
                <?php foreach ($banners as $b): ?>
                <div class="banner-item">
                    <img src="<?php echo htmlspecialchars($b['image_url'], ENT_QUOTES, 'UTF-8'); ?>" class="banner-img-preview" onerror="this.src='https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=600'">
                    <div class="banner-info">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="background:#FFF1F2; color:var(--primary); font-size:11px; font-weight:700; padding:2px 8px; border-radius:8px;"><?php echo htmlspecialchars($b['badge_text'] ?? 'عرض', ENT_QUOTES, 'UTF-8'); ?></span>
                            <form method="POST" style="display:inline;">
                                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                                <input type="hidden" name="banner_id" value="<?php echo intval($b['id']); ?>">
                                <button type="submit" name="delete_banner_action" class="btn-delete" onclick="return confirm('حذف هذا البانر؟');">حذف 🗑️</button>
                            </form>
                        </div>
                        <h4><?php echo htmlspecialchars($b['title'], ENT_QUOTES, 'UTF-8'); ?></h4>
                        <p style="font-size:12px; color:var(--text-muted);"><?php echo htmlspecialchars($b['subtitle'], ENT_QUOTES, 'UTF-8'); ?></p>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        </div>
    </div>

    <!-- TAB 5: MAIL SETTINGS -->
    <div class="tab-content" id="tab-mail_settings">
        <div class="card">
            <div class="card-head">
                <h3>📧 إعدادات مزود خدمة البريد الإلكتروني (SMTP Settings)</h3>
            </div>
            
            <?php if (isset($_GET['msg']) && $_GET['msg'] === 'mail_saved'): ?>
                <div style="background:#D1FAE5; color:#065F46; padding:12px 16px; border-radius:12px; font-weight:700; margin-bottom:16px;">
                    ✅ تم حفظ وتحديث إعدادات البريد بنجاح!
                </div>
            <?php endif; ?>

            <?php $m_set = getMailSettings(); ?>
            <form method="POST" class="form-box">
                <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                <h4 style="font-size:14px; margin-bottom:14px;">⚙️ بيانات الاتصال بالمزود (SMTP Provider)</h4>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>خادم البريد (SMTP Host)</label>
                        <input type="text" name="smtp_host" class="form-input" value="<?php echo htmlspecialchars($m_set['smtp_host'] ?? '127.0.0.1', ENT_QUOTES, 'UTF-8'); ?>" placeholder="mail.sudra.sa أو 127.0.0.1" required>
                    </div>
                    <div class="form-group">
                        <label>منفذ الاتصال (SMTP Port)</label>
                        <input type="number" name="smtp_port" class="form-input" value="<?php echo htmlspecialchars($m_set['smtp_port'] ?? '25', ENT_QUOTES, 'UTF-8'); ?>" placeholder="25, 465, 587" required>
                    </div>
                    <div class="form-group">
                        <label>نوع التشفير (Encryption Type)</label>
                        <select name="smtp_encryption" class="form-input">
                            <option value="none" <?php echo ($m_set['smtp_encryption'] ?? '') === 'none' ? 'selected' : ''; ?>>بدون تشفير (None / Local)</option>
                            <option value="tls" <?php echo ($m_set['smtp_encryption'] ?? '') === 'tls' ? 'selected' : ''; ?>>STARTTLS (Port 587/25)</option>
                            <option value="ssl" <?php echo ($m_set['smtp_encryption'] ?? '') === 'ssl' ? 'selected' : ''; ?>>SSL / TLS (Port 465)</option>
                        </select>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>اسم المستخدم (SMTP Username)</label>
                        <input type="text" name="smtp_username" class="form-input" value="<?php echo htmlspecialchars($m_set['smtp_username'] ?? '', ENT_QUOTES, 'UTF-8'); ?>" placeholder="noreply@sudra.sa">
                    </div>
                    <div class="form-group">
                        <label>كلمة المرور (SMTP Password)</label>
                        <input type="password" name="smtp_password" class="form-input" placeholder="•••••••• (اتركه فارغاً للاحتفاظ بكلمة المرور الحالية)">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>البريد الإلكتروني للمرسل (Sender Email)</label>
                        <input type="email" name="sender_email" class="form-input" value="<?php echo htmlspecialchars($m_set['sender_email'] ?? 'noreply@sudra.sa', ENT_QUOTES, 'UTF-8'); ?>" placeholder="noreply@sudra.sa" required>
                    </div>
                    <div class="form-group">
                        <label>اسم المرسل الظاهر (Sender Name)</label>
                        <input type="text" name="sender_name" class="form-input" value="<?php echo htmlspecialchars($m_set['sender_name'] ?? 'سودرا للشحن والتوصيل', ENT_QUOTES, 'UTF-8'); ?>" placeholder="سودرا للشحن والتوصيل" required>
                    </div>
                </div>

                <button type="submit" name="save_mail_settings" class="btn-submit">حفظ إعدادات البريد 💾</button>
            </form>

            <!-- TEST EMAIL CARD -->
            <div style="margin-top:24px; border-top:1px solid #E2E8F0; padding-top:20px;">
                <h4 style="font-size:15px; margin-bottom:12px; font-weight:800;">🧪 اختبار الاتصال / إرسال بريد تجريبي</h4>
                <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">أدخل بريداً إلكترونياً لإرسال رسالة فحص والتأكد من صحة اتصال وسيرفر البريد بشكل فوري.</p>
                
                <?php if ($mail_test_output !== null): ?>
                    <div style="padding:14px; border-radius:12px; margin-bottom:16px; font-weight:700; <?php echo $mail_test_output['success'] ? 'background:#D1FAE5; color:#065F46;' : 'background:#FEE2E2; color:#991B1B;'; ?>">
                        <?php echo htmlspecialchars($mail_test_output['message'], ENT_QUOTES, 'UTF-8'); ?>
                    </div>
                <?php endif; ?>

                <form method="POST" style="display:flex; gap:12px; max-width:600px; align-items:flex-end;">
                    <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token, ENT_QUOTES, 'UTF-8'); ?>">
                    <div class="form-group" style="flex:1;">
                        <label>البريد الإلكتروني للاختبار</label>
                        <input type="email" name="test_email" class="form-input" placeholder="name@example.com" required value="<?php echo htmlspecialchars($_POST['test_email'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">
                    </div>
                    <button type="submit" name="test_mail_action" class="btn-submit" style="background:#0F172A; white-space:nowrap; padding:11px 20px;">إرسال بريد تجريبي 🚀</button>
                </form>
            </div>
        </div>
    </div>

</div>

<script>
    function showTab(t) {
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        var el = document.getElementById('tab-' + t);
        if (el) el.classList.add('active');
        var btn = document.getElementById('btn-' + t) || (event && event.target && event.target.classList.contains('tab-btn') ? event.target : null);
        if (btn) btn.classList.add('active');
    }

    // تفعيل التبويب الممرر عبر URL
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab') || '<?php echo !empty($mail_test_output) ? "mail_settings" : ""; ?>';
    if (activeTab) {
        showTab(activeTab);
    }
</script>
</body>
</html>
