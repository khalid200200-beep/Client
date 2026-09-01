<?php
require_once __DIR__ . '/../config/db.php';

$input = json_decode(file_get_contents('php://input'), true) ?? $_POST;
$action = $_GET['action'] ?? ($input['action'] ?? 'list');

switch ($action) {
    // 1. جلب قائمة البانرات النشطة
    case 'list':
        if ($pdo) {
            $stmt = $pdo->query("SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC, id DESC");
            $banners = $stmt->fetchAll();
            sendJsonResponse(true, 'تم جلب البانرات بنجاح', $banners);
        } else {
            sendJsonResponse(true, 'بيانات تجريبية للبانرات', [
                [
                    'id' => 1,
                    'title' => 'شحنك يصل إليك',
                    'subtitle' => 'بسرعة • أمان • موثوقية',
                    'badge_text' => 'الأكثر طلباً',
                    'image_url' => 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800',
                    'button_text' => 'اطلب شحن الآن'
                ],
                [
                    'id' => 2,
                    'title' => 'خصم 20% على الشحن السريع',
                    'subtitle' => 'شحن آمن وفوري بين جميع المدن',
                    'badge_text' => 'عرض محدود 🔥',
                    'image_url' => 'https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=800',
                    'button_text' => 'احصل على العرض'
                ],
                [
                    'id' => 3,
                    'title' => 'خدمة التوصيل في نفس اليوم',
                    'subtitle' => 'كباتن معتمدون بالقرب منك على مدار الساعة',
                    'badge_text' => 'خدمة VIP ⚡',
                    'image_url' => 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800',
                    'button_text' => 'شحن فوري'
                ]
            ]);
        }
        break;

    // 2. إضافة بانر جديد من لوحة الإدارة
    case 'create':
        $title       = trim($input['title'] ?? '');
        $subtitle    = trim($input['subtitle'] ?? '');
        $badge       = trim($input['badge_text'] ?? 'عرض خاص');
        $imageUrl    = trim($input['image_url'] ?? '');
        $buttonText  = trim($input['button_text'] ?? 'اطلب شحن الآن');

        if (empty($title) || empty($imageUrl)) {
            sendJsonResponse(false, 'عنوان البانر ورابط الصورة مطلوبان', null, 400);
        }

        if ($pdo) {
            $stmt = $pdo->prepare("INSERT INTO banners (title, subtitle, badge_text, image_url, button_text) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute([$title, $subtitle, $badge, $imageUrl, $buttonText]);
            sendJsonResponse(true, 'تمت إضافة البانر بنجاح');
        } else {
            sendJsonResponse(true, 'تمت الإضافة تجريبياً');
        }
        break;

    // 3. حذف بانر
    case 'delete':
        $id = intval($input['id'] ?? 0);
        if ($pdo && $id > 0) {
            $stmt = $pdo->prepare("DELETE FROM banners WHERE id = ?");
            $stmt->execute([$id]);
            sendJsonResponse(true, 'تم حذف البانر بنجاح');
        } else {
            sendJsonResponse(true, 'تم الحذف');
        }
        break;

    default:
        sendJsonResponse(false, 'إجراء غير معروف', null, 404);
}
