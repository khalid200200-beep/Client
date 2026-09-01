import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

# Disable insecure HTTPS warnings for self/test client
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

results = []

def run_test(name, method, endpoint, payload=None, expected_status=200, check_fn=None):
    url = f"{BASE_URL}{endpoint}" if endpoint.startswith("/") else f"{BASE_URL}/{endpoint}"
    print(f"\n🧪 [TEST] {name} -> {method} {url}")
    try:
        if method == 'GET':
            resp = session.get(url, timeout=10)
        elif method == 'POST':
            resp = session.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        elif method == 'DELETE':
            resp = session.delete(url, timeout=10)
        else:
            resp = session.request(method, url, json=payload, timeout=10)

        # 1. Verify JSON Content-Type
        ctype = resp.headers.get('Content-Type', '')
        is_json = 'application/json' in ctype
        status_ok = resp.status_code == expected_status

        data = None
        try:
            data = resp.json()
        except Exception:
            pass

        check_passed = True
        if check_fn and data:
            check_passed = check_fn(data)

        passed = status_ok and is_json and (data is not None) and check_passed
        res_str = "PASS ✅" if passed else "FAIL ❌"
        results.append({
            "name": name,
            "endpoint": endpoint,
            "method": method,
            "status_code": resp.status_code,
            "expected_status": expected_status,
            "is_json": is_json,
            "result": res_str,
            "data_snippet": str(data)[:120] if data else resp.text[:120]
        })
        print(f"   Status: {resp.status_code} (Expected: {expected_status}) | JSON: {is_json} | Result: {res_str}")
        if data:
            print(f"   Message: {data.get('message')}")
        return data, passed
    except Exception as e:
        print(f"   Exception: {e}")
        results.append({
            "name": name,
            "endpoint": endpoint,
            "method": method,
            "status_code": 0,
            "expected_status": expected_status,
            "is_json": False,
            "result": "FAIL (Exception) ❌",
            "data_snippet": str(e)
        })
        return None, False

def main():
    print("==================================================")
    print("🚀 بدء تشغيل حزمة الفحص الشامل لواجهات الـ API (End-to-End Suite)")
    print("==================================================")

    ts = int(time.time())
    test_email = f"audit_test_{ts}@sudra.sa"
    test_phone = f"059{ts % 10000000:07d}"

    # 1. Test Banners
    run_test("جلب البانرات الترويجية", "GET", "/banners", expected_status=200, check_fn=lambda d: d.get('success') == True and isinstance(d.get('data'), list))

    # 2. Test OTP Send
    otp_data, _ = run_test("إرسال رمز OTP للبريد", "POST", "/auth/send-otp", payload={"email": test_email, "type": "register"}, expected_status=200, check_fn=lambda d: d.get('success') == True)

    # 3. Test Invalid OTP verification
    run_test("فحص رفض OTP غير صحيح", "POST", "/auth/verify-otp", payload={"email": test_email, "otp": "999999"}, expected_status=400, check_fn=lambda d: d.get('success') == False)

    # 4. Test Customer Register
    client_reg, _ = run_test("تسجيل حساب عميل جديد", "POST", "/auth/register", payload={
        "name": "عميل الاختبار الشامل",
        "email": test_email,
        "phone": test_phone,
        "password": "Password@123",
        "city": "الخرطوم",
        "role": "client"
    }, expected_status=201, check_fn=lambda d: d.get('success') == True and d.get('data', {}).get('token') is not None)

    # 5. Test Duplicate Registration Conflict (409)
    run_test("فحص منع تكرار التسجيل لنفس الجوال", "POST", "/auth/register", payload={
        "name": "عميل مكرر",
        "email": f"other_{ts}@sudra.sa",
        "phone": test_phone,
        "password": "Password@123"
    }, expected_status=409, check_fn=lambda d: d.get('success') == False)

    # 6. Test Customer Login
    run_test("تسجيل دخول العميل", "POST", "/auth/login", payload={
        "email": test_email,
        "password": "Password@123"
    }, expected_status=200, check_fn=lambda d: d.get('success') == True and d.get('data', {}).get('token') is not None)

    # 7. Test Login Wrong Password
    run_test("فحص رفض كلمة المرور الخاطئة", "POST", "/auth/login", payload={
        "email": test_email,
        "password": "WrongPassword999"
    }, expected_status=401, check_fn=lambda d: d.get('success') == False)

    # 8. Test Driver Register
    driver_phone = f"058{ts % 10000000:07d}"
    driver_email = f"driver_{ts}@sudra.sa"
    run_test("تسجيل حساب سائق جديد (قيد الاعتماد)", "POST", "/auth/register", payload={
        "name": "كابتن الاختبار الشامل",
        "email": driver_email,
        "phone": driver_phone,
        "password": "DriverPassword@123",
        "city": "الخرطوم",
        "vehicle_plate": "س د ر 5555",
        "role": "driver"
    }, expected_status=201, check_fn=lambda d: d.get('success') == True and d.get('data', {}).get('is_active') == 0)

    # 9. Test Driver Pending Login Rejection (403)
    run_test("فحص رفض دخول السائق قبل الاعتماد", "POST", "/auth/login", payload={
        "email": driver_email,
        "password": "DriverPassword@123"
    }, expected_status=403, check_fn=lambda d: d.get('success') == False)

    # 10. Test Create Order
    order_res, _ = run_test("إنشاء طلب شحن جديد للعميل", "POST", "/orders", payload={
        "clientName": "عميل الاختبار الشامل",
        "clientPhone": test_phone,
        "city": "الخرطوم",
        "pickupAddress": "الخرطوم - حي الرياض",
        "deliveryAddress": "بورتسودان - الميناء الشمالي",
        "packageCount": 3,
        "notes": "شحنة تجريبية عاجلة لفحص النظام",
        "imagePath": ""
    }, expected_status=201, check_fn=lambda d: d.get('success') == True and d.get('data', {}).get('id') is not None)

    order_id = order_res.get('data', {}).get('id') if order_res else None

    # 11. Test List Orders
    run_test("جلب قائمة الطلبات", "GET", "/orders", expected_status=200, check_fn=lambda d: d.get('success') == True and len(d.get('data', [])) > 0)

    if order_id:
        # 12. Test Get Single Order
        run_test("جلب تفاصيل الطلب برقم المعرف", "GET", f"/orders/{order_id}", expected_status=200, check_fn=lambda d: d.get('data', {}).get('id') == order_id)

        # 13. Test Driver Accept Order
        run_test("قبول الطلب من قبل السائق", "POST", f"/orders/{order_id}/accept", payload={
            "driverName": "الكابتن أحمد",
            "driverPhone": "0509876543"
        }, expected_status=200, check_fn=lambda d: d.get('data', {}).get('status') == 'accepted')

        # 14. Test Update Status to Loaded with collected_amount
        run_test("تحديث حالة الطلب إلى تم التحميل وتحديد المبلغ", "POST", f"/orders/{order_id}/status", payload={
            "status": "loaded",
            "collectedAmount": 150.00
        }, expected_status=200, check_fn=lambda d: d.get('data', {}).get('status') == 'loaded' and float(d.get('data', {}).get('collected_amount', 0)) == 150.00)

        # 15. Test Update Status to Delivered
        run_test("تحديث حالة الطلب إلى تم التسليم بنجاح", "POST", f"/orders/{order_id}/status", payload={
            "status": "delivered",
            "collectedAmount": 150.00
        }, expected_status=200, check_fn=lambda d: d.get('data', {}).get('status') == 'delivered')

    # 16. Test Drivers List
    run_test("جلب قائمة السائقين", "GET", "/drivers", expected_status=200, check_fn=lambda d: d.get('success') == True)

    # 17. Test Users List
    run_test("جلب قائمة المستخدمين", "GET", "/users", expected_status=200, check_fn=lambda d: d.get('success') == True)

    # 18. Test 404 Route Not Found
    run_test("فحص مسار غير موجود (404 JSON Response)", "GET", "/non-existent-route", expected_status=404, check_fn=lambda d: d.get('success') == False)

    print("\n==================================================")
    print("📊 ملخص نتائج اختبارات الـ API الشاملة:")
    print("==================================================")
    print(f"{'Endpoint':<35} | {'Method':<6} | {'Status':<6} | {'Result':<10}")
    print("-" * 65)
    all_passed = True
    for r in results:
        print(f"{r['endpoint']:<35} | {r['method']:<6} | {r['status_code']:<6} | {r['result']}")
        if "FAIL" in r['result']:
            all_passed = False

    print("==================================================")
    if all_passed:
        print("🎉 جميع اختبارات الـ API اجتازت الفحص بنسبة 100% (ALL TESTS PASSED)!")
    else:
        print("⚠️ توجد بعض الاختبارات التي تحتاج مراجعة.")
    print("==================================================")

if __name__ == '__main__':
    main()
