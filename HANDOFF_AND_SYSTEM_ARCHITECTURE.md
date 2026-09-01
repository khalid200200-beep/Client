# 📋 تقرير التسليم الشامل والتوثيق الهندسي الكامل للمشروع (Comprehensive System Handoff & Knowledge Base)

هذا التقرير يمثل التوثيق المرجعي الشامل والتسليم الدقيق لحالة النظام الحالية، موجهًا للمطورين ونماذج الذكاء الاصطناعي لفهم كافة تفاصيل المشروع دون الحاجة للرجوع إلى السجلات القديمة.

---

## 1. نظرة عامة على المشروع (Project Identity & Scope)
* **اسم المشروع التجاري:** منصة وتطبيقات بريد السودان (SUDAPOST) بالشراكة مع ربوع طيبة للشحن السريع الدولي والمحلي.
* **طبيعة النظام:** منظومة لوجستية رقمية متكاملة لربط العملاء بالمناديب وإدارة الشحنات والطرود والرحلات بين مدن السودان والمملكة العربية السعودية، مدعومة بلوحة تحكم إدارية مركزية، وسيرفر سحابي حي، وخوادم قواعد بيانات MySQL، وتطبيقات هجينة (Flutter للموبايل + HTML5/JS للويب).

---

## 2. البنية التحتية وبيئة التشغيل (Infrastructure & Live Environment)
* **الدومين الرئيسي والسيرفر الحي:**
  * النطاق الأساسي: `https://app.sudra.sa`
  * النطاق الإضافي المربوط: `https://app.asudra.com.sa`
  * عنوان الخادم (IP): `84.247.141.162` (منفذ SSH: `22`، المستخدم: `root`، كلمة المرور: `KkMm1416`).
  * مسار ملفات الويب على السيرفر: `/www/wwwroot/app.sudra.sa/`
* **لوحة إدارة الخادم (aaPanel):**
  * الرابط: `https://84.247.141.162:19106/99454e02`
  * المستخدم: `augwzldo` | كلمة المرور: `Admin12345`
* **بيئة السيرفر التقنية:**
  * نظام التشغيل: Linux (Ubuntu/Debian)
  * خادم الويب: Nginx مع قواعد إعادة توجيه (Rewrite Rules) لمعالجة مسارات `/api/*` وتوجيهها إلى `/api/index.php`.
  * لغة الباك إند: PHP 8.2 (مع امتدادات PDO, OpenSSL, BCrypt, cURL).
* **قاعدة البيانات (MySQL 8.x):**
  * المضيف والمنفذ: `127.0.0.1:3306`
  * اسم قاعدة البيانات: `shipping_db`
  * المستخدم: `root` | كلمة المرور: `e250eb38de998d02`

---

## 3. المعمارية البرمجية وهيكل المجلدات (Architecture & Directory Structure)

يتكون المستودع المحلي من الأقسام التالية:

```text
📁 تطبيق فلاتر/
│
├── 📱 client_app/                  # تطبيق فلاتر المستقل للعميل (Android / iOS / Web)
│   ├── assets/images/              # الشعار والبنرات الرسمية
│   ├── lib/
│   │   ├── main.dart               # نقطة البدء (MaterialApp + Provider + LoginView كشاشة أولى)
│   │   ├── models/                 # نماذج البيانات (UserModel, OrderModel, BannerItem)
│   │   ├── state/                  # إدارة الحالة (ClientState / ChangeNotifier)
│   │   ├── theme/                  # ثيم العميل (AppTheme: أخضر #009E49 وبورغندي #99001A)
│   │   ├── views/                  # شاشات العميل:
│   │   │   ├── auth/               # login_view.dart (بالإيميل), signup_view.dart (بالإيميل), otp_view.dart
│   │   │   ├── home/               # home_view.dart, quick_actions, hero_banner
│   │   │   ├── orders/             # create_order_view.dart (كاميرا ومعرض), my_orders_view.dart
│   │   │   └── profile/            # profile_view.dart (حذف الحساب وزر الخروج)
│   │   └── widgets/                # أزرار مخصصة، حقول إدخال، شريط تنقل سفلي
│   ├── android/ & ios/             # ملفات البناء والأذونات الأصلية (Camera, Storage, Privacy)
│   └── pubspec.yaml                # تعريف الحزم (provider, http, image_picker, google_fonts, intl)
│
├── 🚚 driver_app/                  # تطبيق فلاتر المستقل للسائق والمندوب (Android / iOS / Web)
│   ├── assets/images/              # الشعار والأيقونات
│   ├── lib/
│   │   ├── main.dart               # نقطة البدء (DriverLoginView كشاشة أولى)
│   │   ├── models/                 # DriverOrderModel (مع حقل collectedAmount)
│   │   ├── state/                  # DriverState (ChangeNotifier للطلبات الحية والإجراءات)
│   │   ├── theme/                  # DriverTheme (الأخضر اللوجستي والكحلي الداكن)
│   │   └── views/
│   │       ├── auth/               # driver_login_view.dart (بالإيميل), driver_signup_view.dart, driver_pending_view.dart
│   │       ├── driver_home_view.dart # استقبال الطلبات + نافذة إدخال المبلغ المحصل نقداً عند التحميل
│   │       └── driver_profile_view.dart # الملف الشخصي، حذف الحساب، وزر تسجيل الخروج
│   ├── android/ & ios/             # إعدادات النظام الأصلية
│   └── pubspec.yaml
│
├── 💻 backend_php/                 # محرك الباك إند المركزي ولوحة التحكم
│   ├── config/
│   │   ├── db.php                  # اتصال PDO + تشفير Bcrypt + مانع الهجمات Rate Limiting + CORS
│   │   └── backup_db.sh            # سكريبت الأتمتة للنسخ الاحتياطي اليومي لـ MySQL
│   ├── api/
│   │   ├── index.php               # موزع مسارات REST API المركزي
│   │   ├── auth.php                # تسجيل الدخول، إنشاء الحسابات، وحذف الحسابات
│   │   ├── orders.php              # إنشاء، قراءة، وتحديث حالات ومبالغ الطلبات
│   │   ├── banners.php             # استرجاع البنرات الترويجية الحية
│   │   ├── drivers.php             # استرجاع وتحديث حالة المناديب
│   │   └── clients.php             # إدارة العملاء
│   ├── admin/                      # لوحة التحكم الإدارية الكاملة
│   │   ├── index.php               # لوحة القيادة المركزية، الإحصائيات، وجداول الطرود والمناديب
│   │   ├── login.php               # تسجيل دخول المشرف المحمي
│   │   └── logout.php              # إنهاء الجلسة الآمن
│   └── database.sql                # مخطط الجداول وقواعد البيانات
│
├── 🌐 web_preview/                 # واجهات الويب التفاعلية الحية المستقلة (PWA / Web App)
│   ├── client.html                 # واجهة العميل للويب (تسجيل، دخول بالإيميل، كاميرا مضغوطة، إنشاء طرود)
│   ├── driver.html                 # واجهة السائق للويب (دخول بالإيميل، طلب انضمام، شاشة مراجعة، إدخال المبلغ)
│   ├── admin.html                  # واجهة تجريبية للوحة التحكم
│   ├── privacy.html                # سياسة الخصوصية الرسمية المتوافقة مع متطلبات Google Play & Apple App Store
│   └── style.css                   # ملف التنسيق العام للويب
│
├── 🚀 server_deploy/               # الحزمة المجهزة للنشر على السيرفر
└── 📦 ملفات الأرشيف المضغوطة (Downloadable ZIPs):
    ├── client_app_flutter_ready.zip # مشروع فلاتر العميل المنفصل الجاهز للتشغيل المباشر
    ├── driver_app_flutter_ready.zip # مشروع فلاتر السائق المنفصل الجاهز للتشغيل المباشر
    └── sudra_full_project_source_code.zip # الحزمة الشاملة للسورس كود بالكامل
```

---

## 4. مخطط قاعدة البيانات والعلاقات (Database Schema)

قاعدة البيانات `shipping_db` تحتوي على الجداول التالية:

1. **`users` (المستخدمون والمدراء والسائقون):**
   * `id`: INT AUTO_INCREMENT PRIMARY KEY
   * `name`: VARCHAR(100)
   * `email`: VARCHAR(150) (مفهرس ويدعم تسجيل الدخول بالبريد)
   * `phone`: VARCHAR(20) (مفهرس)
   * `password`: VARCHAR(255) (مخزن بتشفير `PASSWORD_BCRYPT` القوي)
   * `city`: VARCHAR(50)
   * `vehicle_plate`: VARCHAR(50) (خاص بالسائقين)
   * `role`: ENUM('client', 'driver', 'admin') DEFAULT 'client'
   * `is_active`: TINYINT(1) DEFAULT 1 للعملاء، و 0 للسائقين الجدد (بانتظار موافقة الإدارة).
   * `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

2. **`orders` (الشحنات والطرود):**
   * `id`: INT AUTO_INCREMENT PRIMARY KEY
   * `order_code`: VARCHAR(20) UNIQUE (مثل: `ORD-4220`)
   * `client_id`: INT NULL
   * `client_name`: VARCHAR(100)
   * `client_phone`: VARCHAR(20)
   * `city`: VARCHAR(50)
   * `pickup_address`: VARCHAR(255)
   * `delivery_address`: VARCHAR(255)
   * `package_count`: INT DEFAULT 1
   * `image_path`: LONGTEXT (يدعم روابط الصور وسلاسل Base64 المضغوطة)
   * `notes`: TEXT
   * `status`: ENUM('pending', 'accepted', 'loaded', 'failed', 'delivered') DEFAULT 'pending'
   * `driver_name`: VARCHAR(100) NULL
   * `driver_phone`: VARCHAR(20) NULL
   * `collected_amount`: DECIMAL(10,2) DEFAULT 0.00 (المبلغ النقدي المحصل من العميل عند الاستلام)
   * `failure_reason`: TEXT NULL (سبب تعذر الاستلام في حال فشل الشحنة)
   * `loaded_at`: TIMESTAMP NULL
   * `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

3. **`login_attempts` (محرك الحماية ومنع هجمات التخمين Brute-Force):**
   * `id`: INT AUTO_INCREMENT PRIMARY KEY
   * `ip_address`: VARCHAR(45)
   * `endpoint`: VARCHAR(50)
   * `attempt_time`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   * الفهرس: `(ip_address, endpoint, attempt_time)`

4. **`banners` (البنرات الترويجية الحية):**
   * `id`: INT AUTO_INCREMENT PRIMARY KEY
   * `title`, `subtitle`, `badge_text`, `image_url`, `button_text`, `sort_order`, `is_active`

5. **`order_logs` (سجل تدقيق وتتبع حركات الطرد):**
   * `id`: INT AUTO_INCREMENT PRIMARY KEY
   * `order_id`: INT
   * `action`: VARCHAR(50)
   * `performed_by`: VARCHAR(100)
   * `details`: TEXT
   * `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 5. واجهات الـ REST API المركزية (REST Endpoints Specification)

جميع الاستدعاءات تتم عبر `https://app.sudra.sa/api/...` مع دعم JSON و CORS و UTF-8:

* `POST /api/auth/login`
  * يقبل: `email` (أو `phone`) + `password`.
  * يتحقق من كلمة المرور عبر `password_verify` ومحمي بـ Rate Limiter (بحد أقصى 5 محاولات خاطئة ثم حظر 15 دقيقة).
  * للسائقين: إذا كان `is_active == 0` يرجع كود `403` مع `isPending: true` لعرض شاشة الانتظار.
* `POST /api/auth/register`
  * يقبل: `name`, `email`, `phone`, `city`, `password`, `role`, `vehiclePlate`.
  * للعميل: ينشأ فوراً بحالة نشطة (`is_active = 1`).
  * للسائق: ينشأ بحالة غير نشطة (`is_active = 0`) حتى تفعله الإدارة.
* `POST /api/auth?action=delete_account` (أو `/api/auth/delete_account`)
  * حذف الحساب وكافة البيانات فوراً استجابة للمتطلب الصارم لمتجر آبل (Apple App Store Guideline 5.1.1(v)).
* `GET /api/orders`
  * يرجع قائمة الطلبات مرتبة تنازلياً، مع توفير كافة الحقول بالصيغ الموحدة (`client_name` / `clientName` / `client`، و `collected_amount` / `collectedAmount`).
* `POST /api/orders`
  * إنشاء طلب جديد وتوليد كود بوليصة عشوائي فريد `ORD-XXXX`.
* `PATCH /api/orders/{id}`
  * تحديث الحالة:
    * عند `status = 'accepted'`: يتم تفعيل قفل قاعدة البيانات `SELECT ... FOR UPDATE` داخل Database Transaction لمنع قبول الطلب من أكثر من سائق في نفس اللحظة (Race Condition Prevention).
    * عند `status = 'loaded'`: يتم تخزين وقت التحميل `loaded_at = NOW()` وحفظ المبلغ المستلم في حقل `collected_amount`.
    * عند `status = 'failed'`: يتم حفظ سبب التعذر في `failure_reason`.
* `GET /api/banners`
  * استرجاع بنرات السلايدر النشطة مرتبة حسب `sort_order`.
* `GET /api/drivers` و `GET /api/clients`
  * قوائم المستخدمين والمناديب للإدارة.

---

## 6. سير العمل والمنطق التشغيلي للتطبيقات (Application Workflows)

### أ. تدفق تطبيق العميل (Client App Flow):
1. **شاشة الدخول الأولى:** يدخل العميل بريده الإلكتروني وكلمة المرور.
2. **إنشاء حساب:** إدخال الاسم، البريد الإلكتروني، رقم الجوال، المدينة، وكلمة المرور ثم كود التفعيل التجريبي والدخول للتطبيق.
3. **الشاشة الرئيسية:** سلايدر بنرات متحرك مع نقاط تفاعلية، وشبكة خدمات سريعة، وسجل آخر الشحنات.
4. **إنشاء شحنة:** إدخال بيانات الطرد مع ميزة التقاط الصورة عبر الكاميرا أو اختيارها من المعرض، وتتضمن معالجة ضغط الصور في المتصفح عبر HTML5 Canvas لحجم خفيف (~100KB) لتجنب أخطاء WebKit Safari.
5. **متابعة الشحنة:** يرى العميل حالة الطرد الحية، واسم المندوب ورقم هاتفه مع رابط اتصال مباشر `tel:`, وعندما يتم استلام الشحنة يظهر للعميل: `المبلغ المسدد للمندوب: XX 💵`.
6. **الملف الشخصي:** يحتوي على بيانات العميل، وزر حذف الحساب، وزر تسجيل الخروج.

### ب. تدفق تطبيق السائق (Driver App Flow):
1. **شاشة الدخول الأولى:** يدخل السائق ببريده الإلكتروني وكلمة المرور.
2. **إنشاء حساب كابتن جديد:** يدخل الاسم، البريد، الجوال، المدينة، بيانات المركبة، وكلمة المرور.
3. **شاشة بانتظار موافقة الإدارة (Pending Screen):** يرى بياناته ورسالة تفيد بأن الحساب قيد المراجعة مع زر لفحص وتحديث حالة التفعيل مباشرة.
4. **الشاشة الرئيسية الحية:** فور اعتماد الحساب، يرى السائق قائمة الطرود الحية في ولايته.
5. **قبول الشحنة:** يضغط السائق "قبول الطلب الحي ✅" فتتحول الشحنة إليه وتظهر بيانات العميل ورقم هاتفه للاتصال به.
6. **الاستلام والتحميل:** عند الوصول للعميل يضغط "تم التحميل ✅"، فتظهر له نافذة منبثقة تسأله عن: **المبلغ النقدي المحصل من العميل**؛ فور إدخاله وتأكيده يتم حفظ المبلغ وتحديث الشحنة.
7. **المحفظة:** يحسب التطبيق إجمالي المبالغ النقدية المحصلة من كافة الشحنات المحملة.
8. **الملف الشخصي:** يشمل بيانات السائق، زر حذف الحساب، وزر تسجيل الخروج.

---

## 7. القرارات البرمجية وتاريخ التعديلات السابقة (Design Decisions & Change History)

1. **الاعتماد على البريد الإلكتروني (Email Authentication):**
   * تم تحويل شاشات الدخول والتسجيل في تطبيقي العميل والسائق لتعتمد أساساً على البريد الإلكتروني مع كلمة المرور بدلاً من الاقتصار على رقم الجوال.
2. **حذف النموذج المالي ومحرك التسعير المعقد:**
   * بناءً على توجيه المستخدم الصريح ("لا اريد تعديل النمودج المالي و التسعير التجاري احذفها")، تم إزالة كافة حسابات العمولات التلقائية والرسوم المقيدة، وإبقاء دورة الطلب بسيطة، مع إضافة ميزة تسجيل **المبلغ النقدي المستلم فعلياً بواسطة السائق** (`collected_amount`).
3. **نظام اعتماد السائقين من الإدارة:**
   * السائق الجديد لا يدخل فوراً إلى شاشة الطلبات، بل يدخل في حالة `is_active = 0` وتظهر له شاشة انتظار الموافقة مع زر لإعادة الفحص.
4. **حل مشكلة تضخم الشعار (Logo Aspect Ratio):**
   * تم تقييد أبعاد الشعار في الـ CSS بـ `height: 60px; object-fit: contain;` لمنع تمدده على كامل الشاشة.
5. **الأمان والنسخ الاحتياطي:**
   * تشفير كلمات المرور بـ Bcrypt.
   * منع التزامن غير المرغوب فيه بـ Database Locking.
   * سكريبت نسخ احتياطي مجدول بـ Cron يومياً الساعة 3:00 فجراً في المسار `/www/backup/database/`.

---

## 8. الحزم والمكتبات المستخدمة (Dependencies & Tech Stack)

* **Flutter Framework (Dart 3.x):**
  * `provider: ^6.1.1` (إدارة الحالة)
  * `http: ^1.2.0` (اتصال الشبكة و REST APIs)
  * `image_picker: ^1.0.7` (الكاميرا والمعرض)
  * `google_fonts: ^6.1.0` (خط Cairo العربي)
  * `intl: ^0.19.0` (التنسيق والأوقات)
  * `shared_preferences: ^2.2.2` (التخزين المحلي)
* **الباك إند وقواعد البيانات:**
  * PHP 8.2 PDO
  * MySQL 8.x InnoDB Engine
* **الويب والواجهات التفاعلية:**
  * Vanilla HTML5 / CSS3 / JavaScript
  * Lucide Icons (Web CDN)

---

# CURRENT PROJECT STATE

1. **حالة السيرفر والباك إند:** الخادم الحي `https://app.sudra.sa` يعمل بنسبة 100%، وقواعد البيانات مهيأة بجميع الجداول والحقول المطلوبة (بما فيها `email` للمستخدمين، و `collected_amount` في جدول الطلبات).
2. **حالة واجهات الويب (Web App):**
   * واجهة العميل `client.html`: تدعم الدخول والتسجيل بالإيميل، التقاط الصور، وإنشاء الشحنات وتتبعها.
   * واجهة السائق `driver.html`: تدعم الدخول والتسجيل بالإيميل، شاشة بانتظار موافقة الإدارة، قبول الطرود الحية، ونافذة إدخال المبلغ المحصل نقداً عند التحميل.
3. **حالة مشاريع فلاتر (Flutter Projects):**
   * `client_app`: مشروع فلاتر مستقل ومتكامل يحتوي على كافة ملفات الدارت والأصول والأذونات ومربوط بمنطق الدخول بالإيميل.
   * `driver_app`: مشروع فلاتر مستقل ومتكامل يحتوي على كافة ملفات الدارت وشاشات الدخول، التسجيل، شاشة الانتظار، وشاشة الطلبات مع نافذة إدخال المبلغ المحصل.
4. **حزم التحميل المضغوطة المتاحة على السيرفر:**
   * `https://app.sudra.sa/client_app_flutter_ready.zip` (1.90 MB)
   * `https://app.sudra.sa/driver_app_flutter_ready.zip` (1.89 MB)
   * `https://app.sudra.sa/sudra_full_project_source_code.zip` (7.71 MB)
5. **الموقف الحالي:** النظام مستقر بالكامل، وتم إيقاف أي تعديلات برمجية جديدة بناءً على طلبك، وجاهز للمناقشة أو التسليم لأي جهة برمجية.

---

# CONTEXT FOR ANOTHER AI

```yaml
context_summary:
  project_name: "SUDAPOST & Robou Taiba Logistics Shipping Platform"
  live_domain: "https://app.sudra.sa"
  server_ip: "84.247.141.162"
  ssh_user: "root"
  ssh_pass: "KkMm1416"
  db_name: "shipping_db"
  db_user: "root"
  db_pass: "e250eb38de998d02"
  admin_credentials:
    email: "KHALID200200@GMAIL.COM"
    pass: "123456"
  driver_credentials:
    email: "driver@sudra.sa"
    pass: "123456"
  architecture:
    client_mobile: "Flutter 3.x (Dart) in /client_app"
    driver_mobile: "Flutter 3.x (Dart) in /driver_app"
    backend: "PHP 8.2 REST API with PDO in /backend_php"
    web_previews: "Vanilla HTML5/JS/CSS in /web_preview (client.html, driver.html, admin.html)"
  key_business_rules:
    - "Users and drivers authenticate via Email + Password (Bcrypt hashed)."
    - "New drivers register with is_active=0 and must wait for admin approval."
    - "When drivers mark orders as 'loaded', they input the cash amount collected from the client, stored in orders.collected_amount."
    - "No complex pricing or automatic commission calculations exist; order creation records direct parcel details."
    - "Order acceptance employs DB transaction locking to prevent race conditions among drivers."
    - "Apple App Store Guideline 5.1.1(v) account deletion is implemented across all client and driver interfaces."
  download_artifacts:
    client_zip: "https://app.sudra.sa/client_app_flutter_ready.zip"
    driver_zip: "https://app.sudra.sa/driver_app_flutter_ready.zip"
    master_zip: "https://app.sudra.sa/sudra_full_project_source_code.zip"
```
