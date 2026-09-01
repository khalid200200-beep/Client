# 🚀 دليل أسرار وخطوات رفع SUDRA إلى App Store عبر GitHub Actions

---

## 📌 1. المتغيرات السرية المطلوبة (GitHub Repository Secrets)

قم بالدخول إلى رابط إعدادات المستودع:
🔗 **[https://github.com/khalid200200-beep/Client/settings/secrets/actions](https://github.com/khalid200200-beep/Client/settings/secrets/actions)**

ثم اضغط على زر **`New repository secret`** وأضف المتغيرات التالية:

---

### 🔑 السر الأول: `APP_STORE_CONNECT_KEY_ID`
* **Name:** `APP_STORE_CONNECT_KEY_ID`
* **Value:**
```text
KDDV3TG35U
```

---

### 🔑 السر الثاني: `APP_STORE_CONNECT_ISSUER_ID`
* **Name:** `APP_STORE_CONNECT_ISSUER_ID`
* **Value:**
```text
2cad879f-f7a8-410d-bc49-d6c9081625e4
```

---

### 🔑 السر الثالث: `APPLE_CERTIFICATE_P12_PASSWORD`
* **Name:** `APPLE_CERTIFICATE_P12_PASSWORD`
* **Value:**
```text
SudraSecure2026!
```

---

### 🔑 السر الرابع: `APPLE_CERTIFICATE_P12_BASE64`
* **Name:** `APPLE_CERTIFICATE_P12_BASE64`
* **Value:** *(انسخ النص بالكامل من الملف: `ios_signing/prepared_secrets.json` تحت مفتاح `APPLE_CERTIFICATE_P12_BASE64`)*

---

### 🔑 السر الخامس: `APPLE_PROVISION_PROFILE_CLIENT_BASE64`
* **Name:** `APPLE_PROVISION_PROFILE_CLIENT_BASE64`
* **Value:** *(انسخ النص بالكامل من الملف: `ios_signing/prepared_secrets.json` تحت مفتاح `APPLE_PROVISION_PROFILE_CLIENT_BASE64`)*

---

### 🔑 السر السادس: `APPLE_PROVISION_PROFILE_DRIVER_BASE64`
* **Name:** `APPLE_PROVISION_PROFILE_DRIVER_BASE64`
* **Value:** *(انسخ النص بالكامل من الملف: `ios_signing/prepared_secrets.json` تحت مفتاح `APPLE_PROVISION_PROFILE_DRIVER_BASE64`)*

---

### 🔑 السر السابع (مفتاح API الخاص): `APP_STORE_CONNECT_PRIVATE_KEY`
* **Name:** `APP_STORE_CONNECT_PRIVATE_KEY`
* **Value:** *(محتوى ملف المفتاح `AuthKey_KDDV3TG35U.p8` الذي قمت بتحميله من حساب مطوري آبل)*

---

## ⚡ 2. طريقة تشغيل الرفع التلقائي (Run Workflow)

1. ادخل إلى صفحة الـ Actions في المستودع:
   🔗 **[https://github.com/khalid200200-beep/Client/actions](https://github.com/khalid200200-beep/Client/actions)**
2. اختر من القائمة اليسرى: **`Build & Deploy SUDRA iOS to TestFlight / App Store`**
3. اضغط على زر **`Run workflow`** في اليمين:
   - اختر التطبيق: `client_app` أو `driver_app` أو `both`
   - اضغط الزر الأخضر **`Run workflow`**.
4. سيقوم سيرفر GitHub macOS تلقائياً بـ:
   - سحب الكود وبناء Flutter iOS
   - توقيع التطبيق بشهادة الإنتاج `distribution_certificate.p12`
   - رفع ملف الـ `.ipa` مباشرة إلى **TestFlight / App Store Connect**.

---

## 📱 3. بيانات المراجعة للمتجر (App Store Review Notes)

عند فتح صفحة التطبيق في App Store Connect للمراجعة:

* **حساب تجربة تطبيق العميل (Client App):**
  - **Phone / Email:** `0551122334` / `review@sudra.sa`
  - **Password:** `Review12345!`
* **حساب تجربة تطبيق السائق (Driver App):**
  - **Phone / Email:** `0500000000` / `driver_review@sudra.sa`
  - **Password:** `DriverReview12345!`
* **روابط الدعم والخصوصية:**
  - Support URL: `https://sudra.sa/support`
  - Privacy Policy URL: `https://sudra.sa/privacy`
