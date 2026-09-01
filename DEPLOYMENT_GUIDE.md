# 📱 الدليل الشامل لرفع ونشر التطبيقات على App Store و Google Play

تم إعداد هذا الدليل الاستراتيجي خطوة بخطوة لضمان قبول **تطبيق العميل (`client_app`)** و **تطبيق السائق (`driver_app`)** في متجري **Apple App Store** و **Google Play** من أول مراجعة وبدون أي رفض.

---

## 🍏 الجزء الأول: متطلبات وشروط النشر على متجر Apple App Store

### 1. قائمة التحقق الإلزامية لـ Apple (App Store Review Guidelines):
- [x] **ميزة حذف الحساب الإلزامية (Guideline 5.1.1(v)):** متوفرة ومطبقة في صفحة `حسابي` وزر الحذف النهائي مرتبط بالـ API.
- [x] **نصوص طلب الأذونات والخصوصية (`Info.plist`):**
  - `NSCameraUsageDescription`: لتصوير الشحنة والطرود.
  - `NSPhotoLibraryUsageDescription`: لاختيار صور الشحنات من المعرض.
  - `NSLocationWhenInUseUsageDescription`: لتحديد موقع العميل وتوجيه أقرب سائق.
  - `NSLocationAlwaysAndWhenInUseUsageDescription`: لتتبع مسار توصيل الشحنة.
- [x] **صفحة سياسة الخصوصية (Privacy Policy URL):** متوفرة وجاهزة للنشر على الرابط: `privacy.html`.
- [x] **بيانات حساب المراجع (App Review Demo Account):**
  - رقم الجوال: `0551234567`
  - كلمة المرور: `123456`
  - رمز الـ SMS OTP التجريبي: `1234`

### 2. خطوات بناء ملف الرفع (iOS Archive):
1. افتح المشروع في بيئة macOS عبر برنامج Xcode:
   ```bash
   cd client_app
   flutter build ipa --release
   ```
2. في Xcode: اختر `Product > Archive` ثم `Distribute App > App Store Connect > Upload`.
3. كرر نفس الخطوة لتطبيق السائق `driver_app`.

---

## 🤖 الجزء الثاني: متطلبات وشروط النشر على متجر Google Play

### 1. قائمة التحقق لسياسات Google Play (Developer Policy):
- [x] **Target SDK Level 34+ (Android 14/15):** التطبيق مهيأ للعمل مع أحدث مستويات أندرويد.
- [x] **صيغة الحزمة (Android App Bundle - `.aab`):** إلزامية لجميع التطبيقات الجديدة.
- [x] **نموذج أمان البيانات (Data Safety Form):** الإفصاح عن جمع (رقم الجوال، الاسم، الموقع التقريبي، والصور لأغراض الشحن).
- [x] **رابط حذف الحساب:** إدخال رابط أو ميزة الحذف من داخل التطبيق.

### 2. خطوات توليد حزمة النشر (`.aab`):
1. افتح موجه الأوامر في مجلد التطبيق:
   ```bash
   # لتطبيق العميل:
   cd client_app
   flutter build appbundle --release

   # لتطبيق السائق:
   cd driver_app
   flutter build appbundle --release
   ```
2. ستجد ملف الحزمة الجاهز للرفع في المسار:
   `build/app/outputs/bundle/release/app-release.aab`
3. في **Google Play Console**: انتقل إلى `Production > Create new release` وارفع ملف `.aab`.

---

## 🌐 الجزء الثالث: استضافة الخلفية ولوحة التحكم (PHP & MySQL)

1. ارفع مجلد `backend_php` إلى أي استضافة تدعم PHP 8.1+ و MySQL (مثل cPanel, VPS, أو Hostinger).
2. استورد ملف `database.sql` في قاعدة بيانات MySQL.
3. عدّل بيانات الاتصال في `backend_php/config/db.php` (اسم السيرفر، المستخدم، وكلمة المرور).
4. حدّث رابط الـ `baseUrl` في تطبيق الفلاتر:
   - في ملف `client_app/lib/services/api_service.dart`: ضع رابط موقعك مثل `https://yourdomain.com/backend_php/api/`.

---

## 🔗 روابط مهمة تم تجهيزها لك في المشروع:
- **سياسة الخصوصية الرسمية:** [privacy.html](file:///c:/Users/khalid/Downloads/تطبيق%20فلاتر/web_preview/privacy.html)
- **لوحة التحكم المحصنة:** [admin.html](file:///c:/Users/khalid/Downloads/تطبيق%20فلاتر/web_preview/admin.html)
