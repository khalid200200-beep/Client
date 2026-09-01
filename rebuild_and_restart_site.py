import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=120)

sftp = ssh.open_sftp()

# 1. HTML version of support for app.sudra.sa/support.html
support_html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>مركز الدعم الفني | سودرا SUDRA Support</title>
  <link rel="stylesheet" href="/style.css">
  <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Tajawal', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 0; }
    .container { max-width: 900px; margin: 40px auto; padding: 20px; }
    .card { background: #1e293b; border-radius: 16px; padding: 30px; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); margin-bottom: 25px; }
    h1 { color: #10b981; font-size: 28px; margin-top: 0; }
    h2 { color: #38bdf8; font-size: 20px; border-bottom: 1px solid #334155; padding-bottom: 10px; }
    .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px; margin: 25px 0; }
    .contact-box { background: #0f172a; border: 1px solid #334155; padding: 20px; border-radius: 12px; text-align: center; }
    .btn { display: inline-block; background: #10b981; color: white; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; margin-top: 10px; }
    .btn:hover { background: #059669; }
    .faq-item { margin-bottom: 15px; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; }
    .faq-title { font-weight: bold; color: #10b981; margin-bottom: 5px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card" style="text-align: center;">
      <h1>مركز الدعم والمساعدة - منصة سودرا</h1>
      <p style="color: #94a3b8;">فريق خدمة العملاء والدعم الفني متاح لمساعدتكم على مدار الساعة</p>
    </div>

    <div class="contact-grid">
      <div class="contact-box">
        <h3 style="color: #10b981;">المحادثة الفورية</h3>
        <p style="color: #94a3b8; font-size: 13px;">تواصل مباشر وسريع عبر واتساب</p>
        <a href="https://wa.me/966551122334" class="btn" target="_blank">محادثة واتساب</a>
      </div>
      <div class="contact-box">
        <h3 style="color: #38bdf8;">البريد الإلكتروني</h3>
        <p style="color: #94a3b8; font-size: 13px;">support@sudra.sa</p>
        <a href="mailto:support@sudra.sa" class="btn" style="background: #0284c7;">إرسال بريد</a>
      </div>
      <div class="contact-box">
        <h3 style="color: #fbbf24;">الهاتف المباشر</h3>
        <p style="color: #94a3b8; font-size: 13px;">0551122334</p>
        <a href="tel:0551122334" class="btn" style="background: #d97706;">اتصال هاتف</a>
      </div>
    </div>

    <div class="card">
      <h2>الأسئلة الشائعة حول التطبيق</h2>
      <div class="faq-item">
        <div class="faq-title">1. كيف يمكنني إنشاء طلب شحن جديد؟</div>
        <p style="color: #cbd5e1; font-size: 14px; margin: 0;">من خلال الشاشة الرئيسية في تطبيق العميل، اضغط على "طلب شحن جديد"، وأدخل تفاصيل الشحنة مع إمكانية إرفاق حتى 5 صور للطرود.</p>
      </div>
      <div class="faq-item">
        <div class="faq-title">2. كيف أتابع حالة طردي؟</div>
        <p style="color: #cbd5e1; font-size: 14px; margin: 0;">من خلال تبويب "شحناتي" لمتابعة مسار الشحنة من وقت القبول والتحميل وحتى التسليم النهائي.</p>
      </div>
      <div class="faq-item">
        <div class="faq-title">3. كيف يتم حذف الحساب والبيانات؟</div>
        <p style="color: #cbd5e1; font-size: 14px; margin: 0;">من صفحة "حسابي"، اضغط على "حذف الحساب نهائياً" وسيتم محو البيانات فوراً وفق متطلبات الخصوصية.</p>
      </div>
    </div>
  </div>
</body>
</html>
"""

with sftp.file('/www/wwwroot/app.sudra.sa/support.html', 'w') as f:
    f.write(support_html)
print("✅ Created /www/wwwroot/app.sudra.sa/support.html")

# 2. Update app.sudra.sa/privacy.html
privacy_html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>سياسة الخصوصية وحماية البيانات | تطبيق سودرا SUDRA</title>
  <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Tajawal', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 0; line-height: 1.7; }
    .container { max-width: 900px; margin: 40px auto; padding: 20px; }
    .card { background: #1e293b; border-radius: 16px; padding: 35px; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
    h1 { color: #10b981; font-size: 26px; margin-top: 0; }
    h2 { color: #38bdf8; font-size: 18px; margin-top: 25px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
    p, li { color: #cbd5e1; font-size: 14px; }
    ul { padding-right: 20px; }
    .badge { display: inline-block; background: #065f46; color: #34d399; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <span class="badge">معايير Apple App Store</span>
      <h1>سياسة الخصوصية لمنصة وتطبيقات سودرا (SUDRA)</h1>
      <p style="color: #94a3b8; font-size: 12px;">تاريخ السريان: 31 أغسطس 2026</p>

      <h2>1. البيانات التي نجمعها</h2>
      <ul>
        <li><strong>بيانات الحساب:</strong> الاسم، رقم الجوال، والبريد الإلكتروني للتحقق برموز OTP وإدارة الحساب.</li>
        <li><strong>الصور والمستندات:</strong> التقاط وإرفاق صور الشحنات (حتى 5 صور) لتوثيق الطرود.</li>
        <li><strong>الموقع الجغرافي:</strong> الموقع التقريبي والدقيق لتحديد المدينة وتوجيه مسارات الشحن للكباتن.</li>
        <li><strong>معرفات الجلسة:</strong> تخزين رموز الدخول المشفرة في iOS Keychain للحفاظ على أمان الحساب.</li>
        <li><strong>بيانات المركبة (للسائقين):</strong> رقم اللوحة ونوع المركبة.</li>
      </ul>

      <h2>2. حماية وتشفير البيانات</h2>
      <p>يتم تشفير جميع الاتصالات عبر HTTPS/TLS 1.3 وتخزين كلمات المرور المشفرة ولا يتم مشاركة أي بيانات حساسة مع أطراف ثالثة.</p>

      <h2>3. عدم التتبع (No Tracking)</h2>
      <p>لا نستخدم أي تقنيات لتتبع المستخدم عبر مواقع أو تطبيقات أخرى، ولا نقوم ببيع بيانات المستخدمين لأي غرض.</p>

      <h2>4. حق حذف الحساب نهائياً</h2>
      <p>يتيح التطبيق إمكانية حذف الحساب ومسح البيانات فورياً من خلال شاشة "الملف الشخصي" وفق متطلبات Apple Guideline 5.1.1(v).</p>

      <h2>5. التواصل</h2>
      <p>لأي استفسار: <a href="mailto:privacy@sudra.sa" style="color: #10b981;">privacy@sudra.sa</a> أو زيارة <a href="https://sudra.sa/support" style="color: #38bdf8;">مركز الدعم الفني</a>.</p>
    </div>
  </div>
</body>
</html>
"""

with sftp.file('/www/wwwroot/app.sudra.sa/privacy.html', 'w') as f:
    f.write(privacy_html)
print("✅ Updated /www/wwwroot/app.sudra.sa/privacy.html")

sftp.close()

# 3. Add rewrite for /support to app.sudra.sa nginx configuration
run_nginx = """
if ! grep -q "location = /support" /www/server/panel/vhost/nginx/app.sudra.sa.conf; then
  sed -i '/location ~ .*\.(js|css)?\$/i location = /support { try_files /support.html =404; }' /www/server/panel/vhost/nginx/app.sudra.sa.conf
  nginx -s reload
fi
"""
stdin, stdout, stderr = ssh.exec_command(run_nginx)
print("Nginx rewrite update:", stdout.read().decode('utf-8'))

# 4. Build and restart Next.js for sudra.sa
print("Rebuilding Next.js for sudra.sa...")
cmd_build = "cd /www/wwwroot/sudra.sa && npm run build && pm2 restart sudra-app"
stdin, stdout, stderr = ssh.exec_command(cmd_build)
print("Build output:", stdout.read().decode('utf-8'))
print("Build error:", stderr.read().decode('utf-8'))

ssh.close()
