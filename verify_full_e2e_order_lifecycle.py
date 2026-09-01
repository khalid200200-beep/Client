import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://app.sudra.sa/api"
session = requests.Session()
session.verify = False

def main():
    print("==================================================")
    print("🚀 بدء اختبار دورة حياة الطلب المتكاملة (Full End-to-End Order Flow)")
    print("==================================================")

    ts = int(time.time())
    client_email = f"e2e_customer_{ts}@sudra.sa"
    client_phone = f"057{ts % 10000000:07d}"
    driver_phone = "0509876543"
    driver_name  = "الكابتن أحمد"

    # Step 1: Customer Registration
    print("\n1️⃣ [Customer] تسجيل حساب عميل جديد...")
    r_reg = session.post(f"{BASE_URL}/auth/register", json={
        "name": "العميل محمد إبراهيم",
        "email": client_email,
        "phone": client_phone,
        "password": "Password@123",
        "city": "الخرطوم",
        "role": "client"
    }, timeout=10)
    data_reg = r_reg.json()
    assert r_reg.status_code == 201 and data_reg['success'], f"Registration failed: {r_reg.text}"
    token = data_reg['data']['token']
    print(f"   ✅ تم إنشاء الحساب بنجاح: {client_email} (Token: {token[:12]}...)")

    # Step 2: Customer Login
    print("\n2️⃣ [Customer] تسجيل الدخول والتحقق من الجلسة...")
    r_login = session.post(f"{BASE_URL}/auth/login", json={
        "email": client_email,
        "password": "Password@123"
    }, timeout=10)
    data_login = r_login.json()
    assert r_login.status_code == 200 and data_login['success'], f"Login failed: {r_login.text}"
    print(f"   ✅ تم تسجيل الدخول بنجاح للمستخدم: {data_login['data']['name']}")

    # Step 3: Customer Creates Order
    print("\n3️⃣ [Customer] إنشاء طلب شحن جديد...")
    r_order = session.post(f"{BASE_URL}/orders", json={
        "clientName": "العميل محمد إبراهيم",
        "clientPhone": client_phone,
        "city": "الخرطوم",
        "pickupAddress": "الخرطوم - حي المعمورة",
        "deliveryAddress": "بورتسودان - حي الشاطئ",
        "packageCount": 2,
        "notes": "طرد إلكترونيات حساس جداً",
        "imagePath": ""
    }, timeout=10)
    data_order = r_order.json()
    assert r_order.status_code == 201 and data_order['success'], f"Create order failed: {r_order.text}"
    order_id = data_order['data']['id']
    order_code = data_order['data']['order_code']
    print(f"   ✅ تم إنشاء الطلب برقم المعرف [{order_id}] والرمز [{order_code}] وحالة [pending]")

    # Step 4: Verification in Admin & Database (Querying all orders)
    print("\n4️⃣ [Admin & DB] التحقق من استلام الطلب في قاعدة البيانات وظهوره للإدارة...")
    r_list = session.get(f"{BASE_URL}/orders", timeout=10)
    data_list = r_list.json()
    found_order = next((o for o in data_list['data'] if o['id'] == order_id), None)
    assert found_order is not None, f"Order {order_id} not found in database!"
    print(f"   ✅ تم العثور على الطلب في لوحة الإدارة وقاعدة البيانات: Status={found_order['status']}")

    # Step 5: Driver Accepts Order
    print("\n5️⃣ [Driver] قبول السائق للطلب...")
    r_accept = session.post(f"{BASE_URL}/orders/{order_id}/accept", json={
        "driverName": driver_name,
        "driverPhone": driver_phone
    }, timeout=10)
    data_accept = r_accept.json()
    assert r_accept.status_code == 200 and data_accept['success'], f"Driver accept failed: {r_accept.text}"
    print(f"   ✅ تم قبول الطلب وإسناده للسائق: {driver_name} (الحالة: {data_accept['data']['status']})")

    # Step 6: Driver Updates Status to Loaded with collected_amount
    print("\n6️⃣ [Driver] السائق يقوم بتحميل الشحنة وتحصيل المبلغ (180.00 ر.س)...")
    r_load = session.post(f"{BASE_URL}/orders/{order_id}/status", json={
        "status": "loaded",
        "collectedAmount": 180.00
    }, timeout=10)
    data_load = r_load.json()
    assert r_load.status_code == 200 and data_load['data']['status'] == 'loaded', f"Mark loaded failed: {r_load.text}"
    assert float(data_load['data']['collected_amount']) == 180.00, "Collected amount mismatch!"
    print(f"   ✅ تم توثيق التحميل وتحديث المبلغ المحصل: {data_load['data']['collected_amount']} ر.س")

    # Step 7: Driver Updates Status to Delivered
    print("\n7️⃣ [Driver] السائق يسلّم الشحنة بنجاح للوجهة النهائية...")
    r_deliver = session.post(f"{BASE_URL}/orders/{order_id}/status", json={
        "status": "delivered",
        "collectedAmount": 180.00
    }, timeout=10)
    data_deliver = r_deliver.json()
    assert r_deliver.status_code == 200 and data_deliver['data']['status'] == 'delivered', f"Mark delivered failed: {r_deliver.text}"
    print(f"   ✅ تم تحديث حالة الشحنة إلى [delivered] بنجاح!")

    # Step 8: Customer Verification
    print("\n8️⃣ [Customer] العميل يستعلم عن تفاصيل طلبه ومتابعة الحالة النهائية...")
    r_cust_check = session.get(f"{BASE_URL}/orders/{order_id}", timeout=10)
    data_cust = r_cust_check.json()
    assert data_cust['data']['status'] == 'delivered', "Customer view status mismatch!"
    print(f"   ✅ العميل يرى تفاصيل الشحنة كاملة: الكابتن={data_cust['data']['driver_name']} | الحالة={data_cust['data']['status']} | المبلغ المحصل={data_cust['data']['collected_amount']}")

    print("\n==================================================")
    print("🎉 دورة حياة الطلب المتكاملة End-to-End اجتازت الاختبار بنجاح تام 100% (RESULT: PASS ✅)!")
    print("==================================================")

if __name__ == '__main__':
    main()
