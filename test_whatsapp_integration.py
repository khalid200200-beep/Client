import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

print("==================================================")
print("🧪 اختبار تكامل إرسال OTP عبر البريد وواتساب")
print("==================================================")

# Test Registration send-otp with both email and phone
res = requests.post(f"{BASE_URL}/auth/send-otp", json={
    "email": "test_whatsapp_otp@sudra.sa",
    "phone": "0560060938",
    "type": "register"
}).json()
print("1. Send OTP (Email + Phone) Response:", res)
assert res.get("success") == True

# Test forgot-password OTP
res_forgot = requests.post(f"{BASE_URL}/auth/forgot-password", json={
    "identifier": "0560060938"
}).json()
print("2. Forgot Password Response:", res_forgot)
assert res_forgot.get("success") == True

print("\n==================================================")
print("✅ تكامل الإرسال عبر البريد وواتساب جاهز بنجاح 100%!")
print("==================================================")
