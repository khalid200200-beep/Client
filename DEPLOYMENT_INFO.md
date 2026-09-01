# 🚀 توثيق وبيانات نشر المشروع على السيرفر والدومين
# Server Deployment & Verification Report - app.sudra.sa

تم فحص واختبار كامل أجزاء المنظومة والتأكد من أنها **مترابطة وتعمل بكامل خصائصها بنسبة 100%** على السيرفر والدومين المخصص.

---

## 📌 1. الروابط المباشرة والخدمات المتاحة

| الخدمة | الرابط المباشر | حالة الفحص |
| :--- | :--- | :--- |
| 🛡️ **لوحة تحكم الإدارة (Admin Panel)** | [https://app.sudra.sa/admin/login.php](https://app.sudra.sa/admin/login.php) | 🟢 يعمل بكامل الصلاحيات (`HTTP 200`) |
| 🖥️ **الصفحة الرئيسية (Landing Page)** | [https://app.sudra.sa](https://app.sudra.sa) | 🟢 مباشر عبر HTTPS (`HTTP 200`) |
| ⚡ **واجهات الـ Backend API** | [https://app.sudra.sa/api/banners.php](https://app.sudra.sa/api/banners.php) | 🟢 متصل بقاعدة البيانات ومتجاوب |
| 📜 **سياسة الخصوصية الرسمية** | [https://app.sudra.sa/privacy.html](https://app.sudra.sa/privacy.html) | 🟢 معتمد للمتاجر (`HTTP 200`) |
| 📱 **معاينة تطبيق العميل (Web)** | [https://app.sudra.sa/client.html](https://app.sudra.sa/client.html) | 🟢 تفاعلي بالكامل |
| 🚗 **معاينة تطبيق السائق (Web)** | [https://app.sudra.sa/driver.html](https://app.sudra.sa/driver.html) | 🟢 تفاعلي بالكامل |

---

## 🧪 2. نتائج اختبار التكامل والترابط الشامل (End-to-End Test Results)

تم إجراء اختبارات آلية حية ومباشرة على السيرفر وتمت جميعها بنجاح:

1. ✅ **واجهة المصادقة والحسابات (`/api/auth.php`):**
   - تسجيل حساب جديد للعميل والسائق.
   - التحقق من عدم تكرار أرقام الجوال والحماية بكلمة مرور مشفرة.
   - تسجيل الدخول وتوليد رموز الجلسات الآمنة.
   - ميزة حذف الحساب الإلزامية لمتجر Apple App Store.

2. ✅ **واجهة الشحنات والطلبات (`/api/orders.php`):**
   - إنشاء طلب شحن جديد وتوليد كود بوليصة فريد تلقائياً (`ORD-XXXX`).
   - استعلام العميل عن حالة وتاريخ شحناته.
   - توزيع وتوجيه الطلبات تلقائياً لسائقي المدينة المحددة (مثل: الرياض).
   - قبول السائق للطلب وتحديث الحالة إلى `accepted`.
   - تسجيل تحميل الشحنة وتحديث الحالة إلى `loaded`.
   - تسجيل تسليم الشحنة بنجاح وتحديث الحالة إلى `delivered`.

3. ✅ **واجهة البانرات والعروض الترويجية (`/api/banners.php`):**
   - جلب البانرات النشطة تلقائياً لتطبيقات الموبايل والموقع.
   - إمكانية الإضافة والتعديل والتحكم من لوحة تحكم المشرف.

4. ✅ **لوحة التحكم المشرف (`/admin/`):**
   - حماية ضد هجمات CSRF و Session Fixation و SQL Injection.
   - إحصائيات حية للطلبات، السائقين، والمستخدمين.
   - إمكانية تفعيل/إيقاف السائقين الجدد قبل السماح لهم باستقبال الشحنات.

---

## 🔐 3. بيانات الدخول إلى لوحة التحكم (Admin Credentials)

* **رابط الدخول المحمي:** [https://app.sudra.sa/admin/login.php](https://app.sudra.sa/admin/login.php)
* **رابط لوحة التحكم المباشرة:** [https://app.sudra.sa/admin.html](https://app.sudra.sa/admin.html)
* **اسم المستخدم / البريد الإلكتروني:** `KHALID200200@GMAIL.COM`
* **كلمة المرور:** `123456`

---

## 🗄️ 4. بيانات قاعدة البيانات على السيرفر (MySQL)

```text
Host          : 127.0.0.1 (أو localhost)
Port          : 3306
Database Name : shipping_db
Database User : root
Password      : e250eb38de998d02
Encoding      : utf8mb4 / utf8mb4_unicode_ci
```

---

## 📱 5. إعدادات تطبيق فلاتر (Flutter Mobile App)

ملف الإعدادات: `client_app/lib/core/constants/api_constants.dart`
```dart
class ApiConstants {
  static const String baseUrl = "https://app.sudra.sa/api";
  static const String authEndpoint = "$baseUrl/auth.php";
  static const String ordersEndpoint = "$baseUrl/orders.php";
  static const String bannersEndpoint = "$baseUrl/banners.php";
}
```
