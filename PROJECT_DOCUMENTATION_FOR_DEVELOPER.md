# 📦 دليل السورس كود وهندسة المشروع للمبرمج (Developer Full Architecture Guide)
**مشروع:** منصة وتطبيقات بريد السودان للشحن والتوصيل المتكاملة (SUDAPOST)  
**الدومين الحي والسيرفر:** [https://app.sudra.sa](https://app.sudra.sa) | IP: `84.247.141.162`  
**تاريخ الإصدار:** أغسطس 2026  

---

## 🏗️ 1. هيكل المجلدات والسورس كود (Project Structure)

```text
📁 تطبيق فلاتر/
│
├── 📱 client_app/                  # تطبيق العميل (Flutter Client App)
│   ├── lib/
│   │   ├── core/constants/         # ثوابت الـ API (https://app.sudra.sa/api)
│   │   ├── models/                 # نماذج البيانات (UserModel, OrderModel, BannerItem)
│   │   ├── state/                  # إدارة الحالة (Provider / ClientState)
│   │   ├── theme/                  # ثيم وتصميم التطبيق (الأخضر والبورغندي)
│   │   └── views/                  # شاشات العميل (Home, Orders, Profile, Auth)
│   ├── android/                    # إعدادات أندرويد والأذونات (Camera, Storage, Internet)
│   ├── ios/                        # إعدادات آيفون (Info.plist, App Store Guidelines)
│   └── pubspec.yaml                # تبعيات وحزم فلاتر
│
├── 🚚 driver_app/                  # تطبيق السائق والمندوب (Flutter Driver App)
│   ├── lib/
│   │   ├── models/                 # نموذج طلب السائق (DriverOrderModel مع collectedAmount)
│   │   ├── state/                  # حالة السائق واستقبال الطلبات الحية (DriverState)
│   │   ├── theme/                  # ثيم وتصميم السائق (DriverTheme)
│   │   └── views/                  # شاشات المندوب (DriverHomeView, DriverProfileView)
│   └── pubspec.yaml
│
├── 💻 backend_php/                 # الباك إند وواجهات الـ REST API ولوحة التحكم
│   ├── config/
│   │   ├── db.php                  # اتصال قاعدة البيانات PDO + حماية XSS, CSRF, Rate Limiting, Bcrypt
│   │   └── backup_db.sh            # سكريبت النسخ الاحتياطي التلقائي اليومي
│   ├── api/
│   │   ├── index.php               # الموزع المركزي لـ REST API (/api/orders, /api/auth, /api/banners)
│   │   ├── auth.php                # مصادقة المستخدمين وحذف الحسابات
│   │   ├── orders.php              # إدارة عمليات الشحنات
│   │   ├── banners.php             # البنرات الترويجية
│   │   ├── drivers.php             # المناديب
│   │   └── clients.php             # العملاء
│   ├── admin/                      # لوحة التحكم الإدارية الكاملة (PHP + Bootstrap)
│   │   ├── index.php               # الشاشة الرئيسية والإحصائيات وإدارة المناديب والطلبات
│   │   ├── login.php               # تسجيل دخول المشرف المحمي
│   │   ├── logout.php              # تسجيل الخروج الآمن
│   │   └── orders.php              # جدول إدارة الشحنات
│   └── database.sql                # مخطط وهيكل قاعدة بيانات MySQL
│
├── 🌐 web_preview/                 # الواجهات التفاعلية المستقلة للويب
│   ├── client.html                 # واجهة العميل للويب (مع الكاميرا، المعرض، وتتبع الشحنات)
│   ├── driver.html                 # واجهة المندوب للويب (قبول الطلبات، تسجيل المبالغ المستلمة)
│   ├── admin.html                  # واجهة لوحة الإدارة التجريبية
│   ├── privacy.html                # سياسة الخصوصية الرسمية المتوافقة مع متاجر آبل وجوجل
│   └── style.css                   # ملف التنسيق العام لكافة واجهات الويب
│
└── 📄 README.md & DEPLOYMENT_INFO.md # وثائق السيرفر والإعدادات
```

---

## 🔐 2. معلومات الدخول وقواعد البيانات (Credentials & Database)

* **رابط السيرفر:** `https://app.sudra.sa`
* **لوحة تحكم السيرفر (aaPanel):** `https://84.247.141.162:19106/99454e02` (User: `augwzldo`, Pass: `Admin12345`)
* **قاعدة البيانات (MySQL):**
  * Database Name: `shipping_db`
  * Host: `127.0.0.1:3306`
  * User: `root`
  * Pass: `e250eb38de998d02`
* **دخول المدير العام (Admin Login):**
  * Email / Username: `KHALID200200@GMAIL.COM`
  * Password: `123456` (مخزنة بتشفير `PASSWORD_BCRYPT`)
* **دخول المندوب:** `0901234567` / `123456`
* **دخول العميل:** `0912345678` / `123456`

---

## 🌐 3. نقاط نهاية الـ REST API (Endpoints Map)

| Method | Endpoint | الوصف |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | تسجيل دخول العميل أو المندوب (محمي بـ Rate Limiter) |
| `POST` | `/api/auth/admin-login` | تسجيل دخول المسؤول المشفر |
| `POST` | `/api/auth/register` | تسجيل حساب جديد |
| `POST` | `/api/auth?action=delete_account` | حذف الحساب والبيانات نهائياً (متطلب آبل 5.1.1(v)) |
| `GET` | `/api/orders` | جلب جميع الطلبات الحية |
| `POST` | `/api/orders` | إنشاء طلب شحن جديد مع صورة الطرد وملاحظات التوصيل |
| `PATCH` | `/api/orders/{id}` | تحديث حالة الطلب (`accepted`, `loaded`, `failed`) مع حماية التزامن والمبلغ المستلم (`collectedAmount`) |
| `GET` | `/api/banners` | جلب بنرات السلايدر الترويجي النشطة |
| `GET` | `/api/drivers` | جلب قائمة المناديب وحالة الاعتماد |
| `GET` | `/api/clients` | جلب قائمة العملاء المسجلين |

---

## 🚀 4. كيفية تشغيل وتجربة المشروع محلياً (Local Setup)

### أ. تطبيقات فلاتر (Flutter Apps):
```bash
# تشغيل تطبيق العميل
cd client_app
flutter pub get
flutter run -d chrome # أو عبر جهاز متصل / محاكي

# تشغيل تطبيق المندوب
cd driver_app
flutter pub get
flutter run -d chrome
```

### ب. تشغيل السيرفر المحلي:
```bash
cd backend_php
php -S localhost:8000
```
ثم فتح `http://localhost:8000/admin/login.php` لتجربة لوحة التحكم.

---

## 🛡️ 5. الميزات الأمنية والامتثال المطبق (Compliance & Security)
1. **متطلب متجر آبل App Store (Guideline 5.1.1(v)):** زر حذف الحساب نهائياً متوفر في واجهة العميل والسائق ومربوط بـ API الحذف.
2. **التشفير:** تشفير Bcrypt لكافة كلمات المرور في قاعدة البيانات.
3. **حماية التزامن (Concurrency Lock):** استخدام `Database Transaction (SELECT ... FOR UPDATE)` عند قبول الطلب لمنع قبوله من أكثر من سائق.
4. **حماية هجمات التخمين (Rate Limiting):** حظر الـ IP لمدة 15 دقيقة بعد 5 محاولات خاطئة.
5. **ضغط الصور (Image Compression):** ضغط فوري لصور الكاميرا على مستوى المتصفح لتخفيف استهلاك السيرفر وسرعة الإرسال.
