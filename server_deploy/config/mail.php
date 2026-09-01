<?php
/**
 * خدمات إرسال البريد الإلكتروني ورموز التحقق OTP - سودرا للشحن والتوصيل
 * يدعم الربط المباشر بـ SMTP مع التشفير ويدعم إدارة الإعدادات من لوحة التحكم
 */

require_once __DIR__ . '/db.php';

/**
 * جلب إعدادات مزود البريد من قاعدة البيانات مع قيم افتراضية آمنة
 */
function getMailSettings() {
    global $pdo;
    $defaults = [
        'smtp_host'       => '127.0.0.1',
        'smtp_port'       => '25',
        'smtp_username'   => '',
        'smtp_password'   => '',
        'smtp_encryption' => 'none',
        'sender_email'    => 'noreply@sudra.sa',
        'sender_name'     => 'سودرا للشحن والتوصيل',
    ];

    if (!$pdo) {
        return $defaults;
    }

    try {
        $stmt = $pdo->query("SELECT setting_key, setting_value FROM system_settings WHERE setting_key LIKE 'smtp_%' OR setting_key LIKE 'sender_%'");
        $rows = $stmt->fetchAll(PDO::FETCH_KEY_PAIR);
        if (!empty($rows)) {
            return array_merge($defaults, $rows);
        }
    } catch (Exception $e) {
        // Table might not exist yet
    }

    return $defaults;
}

/**
 * حفظ وتحديث إعدادات البريد من لوحة الإدارة
 */
function saveMailSettings($settings) {
    global $pdo;
    if (!$pdo) return false;

    $allowedKeys = ['smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_encryption', 'sender_email', 'sender_name'];

    try {
        $stmt = $pdo->prepare("INSERT INTO system_settings (setting_key, setting_value) VALUES (?, ?) ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)");
        foreach ($allowedKeys as $key) {
            if (isset($settings[$key])) {
                $val = trim($settings[$key]);
                // إذا كانت كلمة المرور فارغة، لا تقم بمسح كلمة المرور القديمة
                if ($key === 'smtp_password' && empty($val)) {
                    continue;
                }
                $stmt->execute([$key, $val]);
            }
        }
        return true;
    } catch (Exception $e) {
        error_log("[SUDRA-MAIL] Failed to save mail settings: " . $e->getMessage());
        return false;
    }
}

/**
 * إرسال بريد إلكتروني عبر بروتوكول SMTP المباشر مع دعم التشفير والتحقق الصارم
 */
function sendSmtpEmail($toEmail, $subject, $htmlBody, $customSettings = null) {
    $cfg = $customSettings ?: getMailSettings();

    $host       = trim($cfg['smtp_host'] ?: '127.0.0.1');
    $port       = intval($cfg['smtp_port'] ?: 25);
    $user       = trim($cfg['smtp_username'] ?? '');
    $pass       = $cfg['smtp_password'] ?? '';
    $encryption = strtolower(trim($cfg['smtp_encryption'] ?? 'none'));
    $fromEmail  = trim($cfg['sender_email'] ?: 'noreply@sudra.sa');
    $fromName   = trim($cfg['sender_name'] ?: 'سودرا للشحن والتوصيل');

    error_log("[SUDRA-MAIL] Attempting to send email to: {$toEmail} using SMTP Host: {$host}:{$port}, Enc: {$encryption}, From: {$fromEmail}");

    // الاتصال بمقبس الـ SMTP المباشر
    $socketTarget = ($encryption === 'ssl' ? "ssl://{$host}" : $host);
    $timeout = 10;
    $errno = 0;
    $errstr = '';

    $socket = @stream_socket_client("{$socketTarget}:{$port}", $errno, $errstr, $timeout);
    if (!$socket) {
        error_log("[SUDRA-MAIL] SMTP Connection Error to {$socketTarget}:{$port} - Error: {$errstr} ({$errno})");
        return false;
    }

    stream_set_timeout($socket, $timeout);

    $readResponse = function() use ($socket) {
        $response = '';
        while ($line = fgets($socket, 515)) {
            $response .= $line;
            if (isset($line[3]) && $line[3] === ' ') break;
        }
        return $response;
    };

    $sendCommand = function($cmd, $expectedCode = 250) use ($socket, $readResponse) {
        fputs($socket, $cmd . "\r\n");
        $resp = $readResponse();
        $code = intval(substr($resp, 0, 3));
        if ($expectedCode && $code !== $expectedCode) {
            error_log("[SUDRA-MAIL] SMTP Command Failed: " . substr($cmd, 0, 15) . "... -> Response: {$resp}");
            return false;
        }
        return $resp;
    };

    // 1. Read Greeting (220)
    $greet = $readResponse();
    if (intval(substr($greet, 0, 3)) !== 220) {
        error_log("[SUDRA-MAIL] Invalid SMTP Greeting: {$greet}");
        fclose($socket);
        return false;
    }

    // 2. EHLO / HELO
    $hostname = gethostname() ?: 'sudra.sa';
    $ehloResp = $sendCommand("EHLO {$hostname}", 250);
    if (!$ehloResp) {
        $sendCommand("HELO {$hostname}", 250);
    }

    // 3. STARTTLS if requested
    if ($encryption === 'tls') {
        $tlsResp = $sendCommand("STARTTLS", 220);
        if ($tlsResp) {
            $crypto = @stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT | STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT);
            if (!$crypto) {
                error_log("[SUDRA-MAIL] Failed to enable TLS encryption on SMTP connection");
                fclose($socket);
                return false;
            }
            $sendCommand("EHLO {$hostname}", 250);
        }
    }

    // 4. Authentication if credentials exist
    if (!empty($user) && !empty($pass)) {
        $authResp = $sendCommand("AUTH LOGIN", 334);
        if ($authResp) {
            $userResp = $sendCommand(base64_encode($user), 334);
            if (!$userResp) {
                error_log("[SUDRA-MAIL] SMTP Username rejected for: {$user}");
                fclose($socket);
                return false;
            }
            $passResp = $sendCommand(base64_encode($pass), 235);
            if (!$passResp) {
                error_log("[SUDRA-MAIL] SMTP Password authentication failed for user: {$user}");
                fclose($socket);
                return false;
            }
        }
    }

    // 5. MAIL FROM
    if (!$sendCommand("MAIL FROM:<{$fromEmail}>", 250)) {
        error_log("[SUDRA-MAIL] MAIL FROM rejected: {$fromEmail}");
        fclose($socket);
        return false;
    }

    // 6. RCPT TO
    if (!$sendCommand("RCPT TO:<{$toEmail}>", 250)) {
        error_log("[SUDRA-MAIL] RCPT TO rejected: {$toEmail}");
        fclose($socket);
        return false;
    }

    // 7. DATA
    if (!$sendCommand("DATA", 354)) {
        error_log("[SUDRA-MAIL] DATA command rejected");
        fclose($socket);
        return false;
    }

    // 8. Message Body & Headers
    $encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    $encodedFromName = '=?UTF-8?B?' . base64_encode($fromName) . '?=';

    $msg  = "From: {$encodedFromName} <{$fromEmail}>\r\n";
    $msg .= "To: <{$toEmail}>\r\n";
    $msg .= "Subject: {$encodedSubject}\r\n";
    $msg .= "Date: " . date('r') . "\r\n";
    $msg .= "MIME-Version: 1.0\r\n";
    $msg .= "Content-Type: text/html; charset=UTF-8\r\n";
    $msg .= "Content-Transfer-Encoding: 8bit\r\n";
    $msg .= "X-Mailer: SUDRA-SMTP-Engine/2.0\r\n\r\n";
    $msg .= $htmlBody . "\r\n.\r\n";

    fputs($socket, $msg);
    $dataResp = $readResponse();
    $success = (intval(substr($dataResp, 0, 3)) === 250);

    if ($success) {
        error_log("[SUDRA-MAIL] Email successfully accepted by SMTP server for: {$toEmail}");
    } else {
        error_log("[SUDRA-MAIL] SMTP Data transmission failed for: {$toEmail} -> {$dataResp}");
    }

    $sendCommand("QUIT", 221);
    fclose($socket);

    return $success;
}

/**
 * دالة إرسال رمز التحقق OTP إلى البريد الإلكتروني بقالب احترافي
 */
function sendOtpEmail($email, $otp, $actionType = 'register') {
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        error_log("[SUDRA-MAIL] Invalid recipient email for OTP: " . $email);
        return false;
    }

    $titles = [
        'register'       => 'تأكيد البريد الإلكتروني وإنشاء الحساب',
        'login'          => 'رمز الدخول السريع إلى حسابك',
        'reset_password' => 'استعادة كلمة المرور',
    ];

    $actionTitle = $titles[$actionType] ?? 'رمز التحقق الخاص بك';
    $subject = "رمز التحقق: {$otp} - سودرا للشحن والتوصيل";

    $htmlBody = <<<HTML
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$actionTitle}</title>
    <style>
        body { margin: 0; padding: 0; background-color: #F8FAFC; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1E293B; direction: rtl; }
        .wrapper { width: 100%; background-color: #F8FAFC; padding: 40px 15px; }
        .email-card { max-width: 520px; margin: 0 auto; background: #FFFFFF; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid #E2E8F0; overflow: hidden; text-align: center; }
        .header { background: linear-gradient(135deg, #009E49 0%, #006837 100%); padding: 32px 20px; color: #FFFFFF; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }
        .header p { margin: 6px 0 0 0; font-size: 14px; opacity: 0.9; }
        .content { padding: 36px 28px; }
        .greeting { font-size: 18px; font-weight: 700; color: #0F172A; margin-bottom: 12px; }
        .description { font-size: 14px; color: #64748B; line-height: 1.6; margin-bottom: 28px; }
        .otp-container { background: #F0FDF4; border: 2px dashed #009E49; border-radius: 18px; padding: 20px; margin: 0 auto 28px auto; display: inline-block; min-width: 220px; }
        .otp-code { font-size: 40px; font-weight: 900; color: #009E49; letter-spacing: 14px; margin-right: -14px; font-family: 'Courier New', Courier, monospace; }
        .expiry-badge { display: inline-flex; align-items: center; background: #FEF3C7; color: #92400E; padding: 6px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 700; margin-bottom: 24px; }
        .footer { background: #F1F5F9; padding: 20px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; }
        .footer a { color: #009E49; text-decoration: none; }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="email-card">
            <div class="header">
                <h1>🚚 سودرا للشحن والتوصيل</h1>
                <p>{$actionTitle}</p>
            </div>
            <div class="content">
                <div class="greeting">مرحباً بك،</div>
                <div class="description">
                    لتأكيد طلبك والمتابعة في تطبيق سودرا للشحن (Sudra Express)، يرجى إدخال رمز التحقق (OTP) التالي في التطبيق:
                </div>
                <div class="otp-container">
                    <div class="otp-code">{$otp}</div>
                </div>
                <div>
                    <span class="expiry-badge">⏱️ الرمز صالح لمدة 10 دقائق فقط</span>
                </div>
                <div style="font-size: 12.5px; color: #94A3B8; margin-top: 15px;">
                    إذا لم تكن أنت من قام بهذا الطلب، يمكنك تجاهل هذه الرسالة بأمان.
                </div>
            </div>
            <div class="footer">
                © 2026 سودرا للشحن والخدمات اللوجستية • <a href="https://app.sudra.sa">app.sudra.sa</a>
            </div>
        </div>
    </div>
</body>
</html>
HTML;

    return sendSmtpEmail($email, $subject, $htmlBody);
}

/**
 * اختبار الاتصال وإرسال رسالة تجريبية
 */
function testSmtpConnection($testEmail, $customSettings = null) {
    if (!filter_var($testEmail, FILTER_VALIDATE_EMAIL)) {
        return ['success' => false, 'message' => 'البريد الإلكتروني المدخل للاختبار غير صالح'];
    }

    $subject = "رسالة اختبار الاتصال - سودرا للشحن والتوصيل";
    $time = date('Y-m-d H:i:s');
    $htmlBody = <<<HTML
<div style="font-family: Arial, sans-serif; direction: rtl; text-align: center; padding: 30px; background: #F8FAFC;">
    <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 16px; border: 1px solid #E2E8F0;">
        <h2 style="color: #009E49;">✅ نجح اختبار اتصال مزود البريد!</h2>
        <p style="color: #475569; font-size: 14px;">تم إرسال هذه الرسالة بنجاح عبر إعدادات SMTP المحددة في لوحة تحكم إدارة سودرا.</p>
        <p style="color: #94A3B8; font-size: 12px;">وقت الاختبار: {$time}</p>
    </div>
</div>
HTML;

    $sent = sendSmtpEmail($testEmail, $subject, $htmlBody, $customSettings);
    if ($sent) {
        return ['success' => true, 'message' => "تم إرسال البريد التجريبي بنجاح إلى {$testEmail} ✅"];
    } else {
        return ['success' => false, 'message' => "فشل إرسال البريد التجريبي. يرجى مراجعة إعدادات المضيف، المنفذ، والتشفير ❌"];
    }
}
