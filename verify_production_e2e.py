import sys
import json
import urllib.request
import ssl
import paramiko
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def api_call(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=UTF-8'
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            raw = res.read().decode('utf-8')
            parsed = json.loads(raw)
            return res.status, parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8')
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {"raw": raw}
    except Exception as e:
        return 0, {"error": str(e)}

def query_db(sql):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)
    cmd = f'mysql -u root -pe250eb38de998d02 shipping_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    ssh.close()
    return out, err

print("=================================================================")
print("  SUDRA PRODUCTION END-TO-END VERIFICATION SUITE")
print("=================================================================")

# 1. Customer A Login / Registration
print("\n--- 1. Customer A Login / Registration ---")
cust_a_phone = "0551122334"
cust_a_email = "test_customer_audit@sudra.sa"
cust_a_name = "عميل الفحص الشامل"
cust_a_pass = "password123"

# Register customer if not exists, or login
status, reg_res = api_call("/api/auth/register", method="POST", data={
    "name": cust_a_name,
    "email": cust_a_email,
    "phone": cust_a_phone,
    "password": cust_a_pass,
    "city": "الرياض",
    "role": "client"
})
if status == 201 and reg_res.get('success'):
    cust_a = reg_res.get('data', {})
    print(f"Registered new customer: {cust_a}")
else:
    status, login_res = api_call("/api/auth/login", method="POST", data={
        "email": cust_a_email,
        "phone": cust_a_phone,
        "password": cust_a_pass
    })
    cust_a = login_res.get('data', {}) or {}
    print(f"Logged in existing customer: {cust_a}")

cust_a_id = cust_a.get('id') or cust_a.get('user_id')
print(f"Customer A Verified: ID={cust_a_id}, Name={cust_a_name}, Phone={cust_a_phone}")

# 2. Create Order
print("\n--- 2. Customer A Creates Shipment ---")
order_payload = {
    "clientName": cust_a_name,
    "clientPhone": cust_a_phone,
    "clientId": cust_a_id,
    "city": "الرياض",
    "pickupAddress": "حي العليا - الرياض",
    "deliveryAddress": "حي الملز - الرياض",
    "packageCount": 2,
    "notes": "شحنة تجريبية - فحص شامل للترابط والانعكاس",
    "imagePath": ""
}
status, create_res = api_call("/api/orders", method="POST", data=order_payload)
print(f"Create Order Status: {status} | Success: {create_res.get('success')}")
order_data = create_res.get('data', {})
test_order_id = order_data.get('id')
test_order_code = order_data.get('order_code') or order_data.get('orderCode')
print(f"Created Order: ID={test_order_id}, Code={test_order_code}, ClientID={order_data.get('client_id')}, Status={order_data.get('status')}")

# 3. DB Verification
print("\n--- 3. Database Verification in MySQL ---")
db_out, db_err = query_db(f"SELECT id, order_code, client_id, client_name, client_phone, city, status, driver_name, driver_phone, collected_amount, created_at FROM orders WHERE id = {test_order_id};")
print(db_out)

# 4. Customer A "My Shipments" API Test
print("\n--- 4. Customer A 'My Shipments' API Test ---")
status, cust_orders_res = api_call(f"/api/orders?phone={cust_a_phone}&client_id={cust_a_id}", method="GET")
print(f"Customer Orders API Status: {status} | Success: {cust_orders_res.get('success')}")
orders_list = cust_orders_res.get('data', [])
print(f"Orders Returned for Customer A: {len(orders_list)}")
found_in_cust = any(o.get('id') == test_order_id or o.get('order_code') == test_order_code for o in orders_list)
print(f"Test Order #{test_order_id} ({test_order_code}) found in Customer A shipments: {found_in_cust}")

# 5. Customer Isolation Test (Customer B)
print("\n--- 5. Customer Isolation Test (Customer B) ---")
status, cust_b_res = api_call("/api/orders?phone=0550000000&client_id=3", method="GET")
cust_b_orders = cust_b_res.get('data') or []
found_in_cust_b = any(o.get('id') == test_order_id or o.get('order_code') == test_order_code for o in cust_b_orders)
print(f"Customer B sees Customer A's order: {found_in_cust_b} (Should be FALSE for isolation)")

# 6. Driver Orders API Test (Driver in Riyadh)
print("\n--- 6. Driver Orders API Test ---")
driver_phone = "0509876543" # Active Driver in Riyadh
# Ensure driver is active in DB
query_db(f"UPDATE users SET is_active = 1, city = 'الرياض' WHERE phone = '{driver_phone}';")
encoded_city = urllib.parse.quote("الرياض")
status, drv_orders_res = api_call(f"/api/orders?city={encoded_city}&driver_phone={driver_phone}", method="GET")
print(f"Driver Orders API Status: {status} | Success: {drv_orders_res.get('success')}")
drv_orders = drv_orders_res.get('data') or []
print(f"Driver City Orders Count: {len(drv_orders)}")
found_in_driver = any(o.get('id') == test_order_id or o.get('order_code') == test_order_code for o in drv_orders)
print(f"Test Order #{test_order_id} ({test_order_code}) found in Driver available orders: {found_in_driver}")

# 7. Driver Lifecycle: Accept Order
print("\n--- 7. Driver Accepts Order ---")
status, accept_res = api_call(f"/api/orders/{test_order_code}/accept", method="POST", data={
    "driverName": "كابتن الرياض المعتمد",
    "driverPhone": driver_phone,
    "action": "accept"
})
print(f"Driver Accept Status: {status} | Success: {accept_res.get('success')}")
print(f"Accept Response: {accept_res.get('message')}")

# 8. Driver Lifecycle: Mark Loaded
print("\n--- 8. Driver Marks Loaded ---")
status, loaded_res = api_call(f"/api/orders/{test_order_code}/status", method="POST", data={
    "status": "loaded",
    "collectedAmount": 5000.0,
    "action": "update_status"
})
print(f"Driver Loaded Status: {status} | Success: {loaded_res.get('success')}")
print(f"Loaded Response: {loaded_res.get('message')}")

# 9. Driver Lifecycle: Mark Delivered
print("\n--- 9. Driver Marks Delivered ---")
status, delivered_res = api_call(f"/api/orders/{test_order_code}/status", method="POST", data={
    "status": "delivered",
    "collectedAmount": 5000.0,
    "action": "update_status"
})
print(f"Driver Delivered Status: {status} | Success: {delivered_res.get('success')}")
print(f"Delivered Response: {delivered_res.get('message')}")

# 10. Final Verification of Customer My Shipments reflect updated status
print("\n--- 10. Customer 'My Shipments' Final Status Verification ---")
status, cust_final_res = api_call(f"/api/orders?phone={cust_a_phone}&client_id={cust_a_id}", method="GET")
cust_final_orders = cust_final_res.get('data', [])
matching = [o for o in cust_final_orders if o.get('id') == test_order_id or o.get('order_code') == test_order_code]
if matching:
    final_order = matching[0]
    print(f"Final Order Status for Customer: {final_order.get('status')}")
    print(f"Final Order Collected Amount: {final_order.get('collected_amount')}")
    print(f"Final Order Driver: {final_order.get('driver_name')} ({final_order.get('driver_phone')})")
else:
    print("Order not found in final check!")

print("\n--- DB Final Row Check ---")
db_final, _ = query_db(f"SELECT id, order_code, client_id, client_name, client_phone, city, status, driver_name, driver_phone, collected_amount FROM orders WHERE id = {test_order_id};")
print(db_final)
