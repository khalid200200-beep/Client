<?php
/**
 * Whats-CRM WhatsApp Message Dispatcher Gateway
 * منظومة إرسال رسائل ورموز التحقق OTP عبر واتساب - سودرا
 * Gateway URL: https://whats-crm.shcs.ae/api/v1/send-text
 */

require_once __DIR__ . '/db.php';

/**
 * جلب إعدادات واتساب من قاعدة البيانات
 */
function getWhatsAppSettings() {
    global $pdo;
    $defaults = [
        'whatsapp_enabled'     => '1',
        'whatsapp_base_url'    => 'https://whats-crm.shcs.ae/api/v1/send-text',
        'whatsapp_token'       => '',
        'whatsapp_instance_id' => '',
        'default_country_code' => '966'
    ];

    if (!$pdo) return $defaults;

    try {
        $stmt = $pdo->query("SELECT setting_key, setting_value FROM system_settings WHERE setting_key LIKE 'whatsapp_%' OR setting_key = 'default_country_code'");
        $rows = $stmt->fetchAll(PDO::FETCH_KEY_PAIR);
        if (!empty($rows)) {
            return array_merge($defaults, $rows);
        }
    } catch (Exception $e) {
        error_log("[WHATSAPP] Failed to fetch settings: " . $e->getMessage());
    }

    return $defaults;
}

/**
 * حفظ إعدادات واتساب في قاعدة البيانات
 */
function saveWhatsAppSettings($settings) {
    global $pdo;
    if (!$pdo) return false;

    $allowed = ['whatsapp_enabled', 'whatsapp_base_url', 'whatsapp_token', 'whatsapp_instance_id', 'default_country_code'];
    try {
        $stmt = $pdo->prepare("INSERT INTO system_settings (setting_key, setting_value) VALUES (?, ?) ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)");
        foreach ($allowed as $key) {
            if (isset($settings[$key])) {
                $val = trim($settings[$key]);
                if (($key === 'whatsapp_token' || $key === 'whatsapp_instance_id') && empty($val)) {
                    continue; // لا تقم بمسح التوكن إن ترك الحقل فارغاً
                }
                $stmt->execute([$key, $val]);
            }
        }
        return true;
    } catch (Exception $e) {
        error_log("[WHATSAPP] Failed to save settings: " . $e->getMessage());
        return false;
    }
}

/**
 * تحويل رقم الهاتف إلى صيغة JID المعتمدة في واتساب
 * Rules:
 * 1. Remove spaces, dashes, brackets
 * 2. Remove leading + or 00
 * 3. 05... -> 9665... / 09... / 01... -> 249... (أو حسب الدولة)
 * 4. Append @s.whatsapp.net
 */
function formatWhatsAppJid($phone, $defaultCountry = '966') {
    if (empty($phone)) return null;

    // إزالة كافة الرموز والمسافات
    $clean = preg_replace('/[^0-9]/', '', (string)$phone);
    if (empty($clean)) return null;

    // إزالة 00 في البداية
    if (strpos($clean, '00') === 0) {
        $clean = substr($clean, 2);
    }

    // معالجة الأرقام المحلية
    if (strpos($clean, '05') === 0) {
        // رقم سعودي محلي
        $clean = '966' . substr($clean, 1);
    } elseif (strpos($clean, '09') === 0 || strpos($clean, '01') === 0) {
        // رقم سوداني محلي
        $clean = '249' . substr($clean, 1);
    } elseif (strpos($clean, '5') === 0 && strlen($clean) === 9) {
        // رقم سعودي بدون صفر
        $clean = '966' . $clean;
    } elseif (strpos($clean, '9') === 0 && strlen($clean) === 9) {
        // رقم سوداني بدون صفر
        $clean = '249' . $clean;
    }

    return $clean . '@s.whatsapp.net';
}

/**
 * إرسال رسالة نصية عبر بوابة Whats-CRM API
 */
function sendWhatsAppMessage($phone, $message, $customSettings = null) {
    $cfg = $customSettings ?: getWhatsAppSettings();

    if (($cfg['whatsapp_enabled'] ?? '1') === '0' || ($cfg['whatsapp_enabled'] ?? '1') === 'false') {
        error_log("[WHATSAPP] WhatsApp gateway is disabled in settings.");
        return ['success' => false, 'message' => 'بوابة واتساب معطلة حالياً'];
    }

    $token = trim($cfg['whatsapp_token'] ?? '');
    $instanceId = trim($cfg['whatsapp_instance_id'] ?? '');
    $baseUrl = trim($cfg['whatsapp_base_url'] ?: 'https://whats-crm.shcs.ae/api/v1/send-text');

    if (empty($token) || empty($instanceId)) {
        error_log("[WHATSAPP] Missing Token or Instance ID for Whats-CRM.");
        return ['success' => false, 'message' => 'بيانات التوكن أو Instance ID غير مكتملة'];
    }

    $jid = formatWhatsAppJid($phone, $cfg['default_country_code'] ?? '966');
    if (!$jid) {
        error_log("[WHATSAPP] Invalid phone number for JID formatting: " . $phone);
        return ['success' => false, 'message' => 'رقم الهاتف غير صالح للإرسال عبر واتساب'];
    }

    $queryParams = http_build_query([
        'token'       => $token,
        'instance_id' => $instanceId,
        'jid'         => $jid,
        'msg'         => $message
    ]);

    $requestUrl = $baseUrl . '?' . $queryParams;

    error_log("[WHATSAPP] Dispatching message to JID: {$jid} via Whats-CRM...");

    // إرسال الطلب عبر cURL أو file_get_contents
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $requestUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'GET');
    curl_setopt($ch, CURLOPT_TIMEOUT, 12);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'User-Agent: SUDRA-WhatsApp-Dispatcher/1.0',
        'Accept: application/json'
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlErr  = curl_error($ch);
    curl_close($ch);

    if ($curlErr) {
        error_log("[WHATSAPP] cURL Error: " . $curlErr);
        return ['success' => false, 'message' => 'تعذر الاتصال ببوابة واتساب: ' . $curlErr];
    }

    $decoded = json_decode($response, true);
    error_log("[WHATSAPP] Response (HTTP {$httpCode}): " . $response);

    if ($httpCode >= 200 && $httpCode < 300 && (!empty($decoded['success']) || isset($decoded['response']))) {
        return [
            'success'  => true,
            'message'  => 'تم إرسال رسالة واتساب بنجاح ✅',
            'data'     => $decoded,
            'jid'      => $jid
        ];
    }

    return [
        'success'  => false,
        'message'  => $decoded['message'] ?? 'فشل إرسال رسالة واتساب',
        'httpCode' => $httpCode,
        'raw'      => $response
    ];
}

/**
 * إرسال رمز التحقق OTP عبر واتساب
 */
function sendWhatsAppOtp($phone, $otp, $actionType = 'register') {
    if (empty($phone)) return false;

    $titles = [
        'register'       => 'تأكيد الحساب الجديد',
        'login'          => 'تسجيل الدخول السريع',
        'reset_password' => 'استعادة كلمة المرور',
    ];

    $title = $titles[$actionType] ?? 'رمز التحقق';

    $msg = "🚚 *سُودرا للشحن والخدمات اللوجستية*\n"
         . "━━━━━━━━━━━━━━━━━━━\n"
         . "طلب: *{$title}*\n\n"
         . "رمز التحقق (OTP) الخاص بك هو:\n"
         . "🔑 *{$otp}*\n\n"
         . "⏱️ الرمز صالح للاستخدام لمدة 10 دقائق فقط.\n"
         . "⚠️ لا تشارك هذا الرمز مع أي شخص للحفاظ على أمان حسابك.\n"
         . "━━━━━━━━━━━━━━━━━━━\n"
         . "سُودرا - دائماً في خدمتك 📦";

    $result = sendWhatsAppMessage($phone, $msg);
    return $result['success'] ?? false;
}
