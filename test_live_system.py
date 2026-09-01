import sys
import json
import urllib.request
import urllib.parse
import ssl

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def make_request(path, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    url = f"{BASE_URL}{path}"
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            res_body = res.read().decode('utf-8')
            return res.status, res_body
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        return e.code, res_body
    except Exception as e:
        return 0, str(e)

print("==========================================")
print("🔍 1. اختبار واجهات البانرات (Banners API)")
print("==========================================")
status, res = make_request("/api/banners.php")
print(f"Status: {status}")
try:
    banners_data = json.loads(res)
    print(f"Success: {banners_data.get('success')}")
    print(f"Banners count: {len(banners_data.get('data', []))}")
    for b in banners_data.get('data', []):
        print(f" - [{b.get('id')}] {b.get('title')} ({b.get('badge_text')})")
except Exception as e:
    print(f"Parse error: {e}, Response: {res[:200]}")

print("\n==========================================")
print("🔍 2. اختبار تسجيل حساب عميل جديد (Auth Register API)")
print("==========================================")
test_client_phone = "0559998877"
reg_payload = {
    "action": "register",
    "name": "عميل تجريبي",
    "phone": test_client_phone,
    "password": "password123",
    "city": "الرياض",
    "role": "client"
}
status, res = make_request("/api/auth.php", method="POST", data=reg_payload)
print(f"Status: {status}")
print(f"Response: {res}")

print("\n==========================================")
print("🔍 3. اختبار تسجيل الدخول (Auth Login API)")
print("==========================================")
login_payload = {
    "action": "login",
    "phone": test_client_phone,
    "password": "password123"
}
status, res = make_request("/api/auth.php", method="POST", data=login_payload)
print(f"Status: {status}")
print(f"Response: {res}")

print("\n==========================================")
print("🔍 4. اختبار إنشاء طلب شحن جديد (Create Order API)")
print("==========================================")
order_payload = {
    "action": "create_order",
    "client_phone": test_client_phone,
    "client_name": "عميل تجريبي",
    "pickup_city": "الرياض",
    "pickup_address": "حي النخيل - شارع التخصصي",
    "delivery_city": "جدة",
    "delivery_address": "حي الروضة - طريق الكورنيش",
    "package_type": "طرد متوسط",
    "weight_kg": 5.5,
    "price": 120.0,
    "notes": "شحنة قابلة للكسر برجاء الحذر"
}
status, res = make_request("/api/orders.php", method="POST", data=order_payload)
print(f"Status: {status}")
print(f"Response: {res}")

print("\n==========================================")
print("🔍 5. اختبار استعلام طلبات العميل (Get Orders API)")
print("==========================================")
status, res = make_request(f"/api/orders.php?phone={test_client_phone}")
print(f"Status: {status}")
print(f"Response: {res}")

print("\n==========================================")
print("🔍 6. اختبار فحص الصفحات الثابتة ولوحة التحكم")
print("==========================================")
pages = [
    ("/", "الصفحة الرئيسية"),
    ("/privacy.html", "سياسة الخصوصية"),
    ("/client.html", "تطبيق العميل ويب"),
    ("/driver.html", "تطبيق السائق ويب"),
    ("/admin/login.php", "تسجيل دخول المشرف"),
    ("/admin/index.php", "لوحة التحكم الرئيسية (حماية المشرف)")
]
for p, desc in pages:
    st, body = make_request(p)
    print(f"Page: {desc:35} | Status: {st} | Length: {len(body)} bytes")

print("\n==========================================")
print("✅ اكتمل الفحص الشامل.")
print("==========================================")
