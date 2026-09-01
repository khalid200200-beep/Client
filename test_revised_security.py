import requests
import json
import base64
import hmac
import hashlib
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

def make_token(uid, role, phone, email, name):
    payload = {
        'uid': uid,
        'role': role,
        'phone': phone,
        'email': email,
        'name': name,
        'iat': int(time.time()),
        'exp': int(time.time()) + (60 * 86400)
    }
    j = json.dumps(payload)
    b64 = base64.b64encode(j.encode('utf-8')).decode('utf-8').replace('+', '-').replace('/', '_').rstrip('=')
    sig = hmac.new('SUDRA_SECURE_KEY_2026_PROD_SHIPPING_EXP'.encode('utf-8'), b64.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"

# Tokens
token_client = make_token(47, 'client', '0551111111', 'client_a_audit@sudra.sa', 'العميل أ')
token_driver = make_token(49, 'driver', '0553333333', 'driver_1_audit@sudra.sa', 'الكابتن 1')
token_admin  = make_token(1, 'admin', '0500000000', 'admin@sudra.sa', 'مدير النظام')

# 1. POST /api/orders No Token
r_post_orders_notoken = requests.post(f"{BASE_URL}/orders", json={"city":"الرياض", "packageCount":1, "notes":"test"})
res_1 = f"{r_post_orders_notoken.status_code}"

# 2. GET /api/orders No Token
r_get_orders_notoken = requests.get(f"{BASE_URL}/orders")
res_2 = f"{r_get_orders_notoken.status_code}"

# 3. Client Order Creation
r_client_create = requests.post(f"{BASE_URL}/orders", 
    headers={"Authorization": f"Bearer {token_client}"}, 
    json={"city":"الرياض", "packageCount":1, "notes":"طلب موثوق من العميل"}
)
res_3 = "PASS" if r_client_create.status_code == 201 and r_client_create.json().get('success') == True else f"FAIL ({r_client_create.status_code})"

# 4. Driver Order Creation
r_driver_create = requests.post(f"{BASE_URL}/orders", 
    headers={"Authorization": f"Bearer {token_driver}"}, 
    json={"city":"الرياض", "packageCount":1, "notes":"طلب من سائق"}
)
res_4 = f"{r_driver_create.status_code}"

# 5. Client Order Isolation (Client sees only own orders)
r_client_orders = requests.get(f"{BASE_URL}/orders", headers={"Authorization": f"Bearer {token_client}"}).json().get('data', [])
res_5 = "PASS" if isinstance(r_client_orders, list) else "FAIL"

# 6. Driver Isolation (Driver sees city/assigned orders, not arbitrary client lists)
r_driver_orders = requests.get(f"{BASE_URL}/orders", headers={"Authorization": f"Bearer {token_driver}"}).json().get('data', [])
res_6 = "PASS" if isinstance(r_driver_orders, list) else "FAIL"

# 7. delete_account Admin
r_del_admin = requests.post(f"{BASE_URL}/auth/delete_account", headers={"Authorization": f"Bearer {token_admin}"})
res_7 = f"{r_del_admin.status_code}"

all_pass = (
    r_post_orders_notoken.status_code == 401 and
    r_get_orders_notoken.status_code == 401 and
    res_3 == "PASS" and
    r_driver_create.status_code == 403 and
    res_5 == "PASS" and
    res_6 == "PASS" and
    r_del_admin.status_code == 403
)

print(f"POST /api/orders No Token: {res_1}")
print(f"GET /api/orders No Token: {res_2}")
print(f"Client Order Creation: {res_3}")
print(f"Driver Order Creation: {res_4}")
print(f"Client Order Isolation: {res_5}")
print(f"Driver Isolation: {res_6}")
print(f"delete_account Admin: {res_7}")
print(f"Final Permission Audit: {'PASS' if all_pass else 'FAIL'}")
