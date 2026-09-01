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

def post_json(path, data):
    url = f"{BASE_URL}{path}"
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        return res.status, json.loads(res.read().decode('utf-8'))

def get_json(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        return res.status, json.loads(res.read().decode('utf-8'))

city_quoted = urllib.parse.quote("الرياض")
print("--- 1. إنشاء طلب شحن جديد للفحص ---")
st, res = post_json("/api/orders.php", {
    "action": "create",
    "client_name": "عميل الاختبار",
    "client_phone": "0559998877",
    "city": "الرياض",
    "notes": "فحص دورة حياة الطلب"
})
print("Create Order Response:", res)
order_id = res['data']['id']
order_code = res['data']['order_code']

print(f"\n--- 2. استعراض طلبات المدينة للسائق ({order_code}) ---")
st, res = get_json(f"/api/orders.php?action=driver_city_orders&city={city_quoted}&driver_phone=0509876543")
print("Status:", st, "Pending Orders count:", len(res.get('data', [])))

print("\n--- 3. قبول السائق للطلب ---")
st, res = post_json("/api/orders.php", {
    "action": "driver_accept",
    "order_id": order_id,
    "driver_name": "أحمد السائق",
    "driver_phone": "0509876543"
})
print("Accept Response:", res)

print("\n--- 4. تأكيد تحميل الشحنة ---")
st, res = post_json("/api/orders.php", {
    "action": "driver_loaded",
    "order_id": order_id
})
print("Loaded Response:", res)

print("\n--- 5. تأكيد تسليم الشحنة ---")
st, res = post_json("/api/orders.php", {
    "action": "driver_delivered",
    "order_id": order_id
})
print("Delivered Response:", res)

print("\n--- 6. التأكد من حالة الطلب النهائية لدى العميل ---")
st, res = get_json("/api/orders.php?phone=0559998877")
order = [o for o in res['data'] if str(o['id']) == str(order_id)][0]
print(f"Final Order Code: {order['order_code']} | Status: {order['status']} | Driver: {order['driver_name']}")
assert order['status'] == 'delivered'
print("\n🎉 تم التأكد: دورة الطلب الكاملة (إنشاء -> استعراض المدينة -> قبول السائق -> التحميل -> التسليم النهائي) تعمل بنجاح 100%!")
