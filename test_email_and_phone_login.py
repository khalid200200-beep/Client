import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

print("==================================================")
print("🧪 اختبار تسجيل الدخول بالبريد الإلكتروني ورقم الجوال")
print("==================================================")

test_email = "universal_login_test@sudra.sa"
test_phone = "0977112233"
test_pass = "MySecretPass2026!"

# 1. Register Client User
reg_res = requests.post(f"{BASE_URL}/auth/register", json={
    "name": "مستخدم الدخول الشامل",
    "email": test_email,
    "phone": test_phone,
    "city": "الخرطوم",
    "password": test_pass,
    "role": "client"
}).json()
print("Register Response:", reg_res.get("message"))

# 2. Test Client Login with EMAIL
print("\n1. تسجيل دخول العميل عبر البريد الإلكتروني:")
res_email = requests.post(f"{BASE_URL}/auth/login", json={
    "email": test_email,
    "password": test_pass
}).json()
print("   Success:", res_email.get("success"), "| User:", res_email.get("data", {}).get("name"))
assert res_email.get("success") == True, "Login with email failed!"

# 3. Test Client Login with PHONE
print("\n2. تسجيل دخول العميل عبر رقم الجوال:")
res_phone = requests.post(f"{BASE_URL}/auth/login", json={
    "phone": test_phone,
    "password": test_pass
}).json()
print("   Success:", res_phone.get("success"), "| User:", res_phone.get("data", {}).get("name"))
assert res_phone.get("success") == True, "Login with phone failed!"

# 4. Test Client Login with identifier field containing EMAIL (UPPERCASE)
print("\n3. تسجيل دخول العميل بالبريد بأحرف كبيرة (Case-Insensitive):")
res_upper_email = requests.post(f"{BASE_URL}/auth/login", json={
    "identifier": test_email.upper(),
    "password": test_pass
}).json()
print("   Success:", res_upper_email.get("success"), "| User:", res_upper_email.get("data", {}).get("name"))
assert res_upper_email.get("success") == True

# 5. Test Client Login with identifier field containing PHONE without leading zero
print("\n4. تسجيل دخول العميل برقم الجوال بدون الصفر الأول:")
res_no_zero = requests.post(f"{BASE_URL}/auth/login", json={
    "identifier": test_phone.lstrip('0'),
    "password": test_pass
}).json()
print("   Success:", res_no_zero.get("success"), "| User:", res_no_zero.get("data", {}).get("name"))
assert res_no_zero.get("success") == True

# 6. Test Driver User Registration and Login with Email & Phone
drv_email = "driver_universal@sudra.sa"
drv_phone = "0988112233"
drv_pass = "DriverSecret2026!"

requests.post(f"{BASE_URL}/auth/register", json={
    "name": "كابتن الدخول الشامل",
    "email": drv_email,
    "phone": drv_phone,
    "city": "الخرطوم",
    "vehiclePlate": "س د 555",
    "password": drv_pass,
    "role": "driver"
})

# Login with Driver Email
print("\n5. تسجيل دخول السائق عبر البريد الإلكتروني:")
drv_res_email = requests.post(f"{BASE_URL}/auth/login", json={
    "identifier": drv_email,
    "password": drv_pass
}).json()
print("   Driver Status (isPending):", drv_res_email.get("isPending") or drv_res_email.get("data", {}).get("isPending"), "| Msg:", drv_res_email.get("message"))
assert drv_res_email.get("isPending") == True or drv_res_email.get("data", {}).get("isPending") == True or drv_res_email.get("success") == True

# Login with Driver Phone
print("\n6. تسجيل دخول السائق عبر رقم الجوال:")
drv_res_phone = requests.post(f"{BASE_URL}/auth/login", json={
    "identifier": drv_phone,
    "password": drv_pass
}).json()
print("   Driver Status (isPending):", drv_res_phone.get("isPending") or drv_res_phone.get("data", {}).get("isPending"), "| Msg:", drv_res_phone.get("message"))
assert drv_res_phone.get("isPending") == True or drv_res_phone.get("data", {}).get("isPending") == True or drv_res_phone.get("success") == True

print("\n==================================================")
print("🎉 كافة اختبارات الدخول بالبريد الإلكتروني أو رقم الجوال تعمل بنسبة 100%!")
print("==================================================")
