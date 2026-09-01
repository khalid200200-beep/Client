import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'https://app.sudra.sa/api'

results = []

def run_test(name, fn):
    try:
        ok, msg = fn()
        results.append({'name': name, 'ok': ok, 'msg': msg})
        status = '✅ PASS' if ok else '❌ FAIL'
        print(f'{status} | {name}: {msg}')
    except Exception as e:
        results.append({'name': name, 'ok': False, 'msg': str(e)})
        print(f'❌ FAIL | {name}: {e}')

# 1. Customer Login
def test_customer_login():
    r = requests.post(f'{BASE}/auth/login', json={'email': 'client_e2e@sudra.sa', 'password': 'password123'})
    data = r.json()
    return r.status_code == 200 and 'token' in (data.get('user') or {}), f'HTTP {r.status_code}'

# 2. Customer Register (duplicate prevention)
def test_customer_register_dup():
    r = requests.post(f'{BASE}/auth/register', json={'name': 'عميل مكرر', 'email': 'client_e2e@sudra.sa', 'phone': '0911002233', 'role': 'client'})
    return r.status_code == 409, f'HTTP {r.status_code} (Conflict prevented)'

# 3. Create Order
def test_create_order():
    order_data = {
        'clientName': 'أحمد مختبر',
        'clientPhone': '0955443322',
        'city': 'الخرطوم',
        'packageCount': 2,
        'notes': 'اختبار نهائي للشحنة',
        'imagePath': 'data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    }
    r = requests.post(f'{BASE}/orders', json=order_data)
    order_id = r.json().get('data', {}).get('id')
    return r.status_code == 200 and order_id is not None, f'Created Order ID: {order_id}'

# 4. Driver Register (is_active=0)
def test_driver_register():
    r = requests.post(f'{BASE}/auth/register', json={
        'name': 'كابتن اختبار نهائي',
        'email': 'driver_final_test@sudra.sa',
        'phone': '0988776655',
        'city': 'الخرطوم',
        'vehiclePlate': 'ط 1234',
        'password': 'password123',
        'role': 'driver'
    })
    return r.status_code in [200, 409], f'HTTP {r.status_code}'

# 5. Unapproved Driver Login (403 Expected)
def test_unapproved_driver_login():
    r = requests.post(f'{BASE}/auth/login', json={'email': 'driver_final_test@sudra.sa', 'password': 'password123'})
    is_pending = 'isPending' in r.text
    return r.status_code == 403 and is_pending, f'HTTP {r.status_code} with isPending: {is_pending}'

# 6. Unapproved Driver Cannot Accept Orders (403 Expected)
def test_unapproved_driver_accept():
    # create order first
    r = requests.post(f'{BASE}/orders', json={'clientName': 'فحص', 'clientPhone': '0900000001', 'packageCount': 1})
    oid = r.json().get('data', {}).get('id')
    r2 = requests.patch(f'{BASE}/orders/{oid}', json={'status': 'accepted', 'driver': 'كابتن غير معتمد', 'driver_phone': '0988776655'})
    return r2.status_code == 403, f'HTTP {r2.status_code} (Unauthorized driver rejected)'

# 7. Approved Driver Acceptance & Race Condition
def test_race_condition():
    r = requests.post(f'{BASE}/orders', json={'clientName': 'فحص التزامن', 'clientPhone': '0900000002', 'packageCount': 1})
    oid = r.json().get('data', {}).get('id')
    
    # Driver 1 accepts
    r1 = requests.patch(f'{BASE}/orders/{oid}', json={'status': 'accepted', 'driver': 'كابتن أول', 'driver_phone': '0901111111'})
    # Driver 2 tries to accept same
    r2 = requests.patch(f'{BASE}/orders/{oid}', json={'status': 'accepted', 'driver': 'كابتن ثاني', 'driver_phone': '0902222222'})
    
    return r1.status_code == 200 and r2.status_code == 409, f'D1 HTTP {r1.status_code}, D2 HTTP {r2.status_code}'

# 8. Mark Loaded with Collected Amount
def test_loaded_collected_amount():
    r = requests.post(f'{BASE}/orders', json={'clientName': 'فحص المبلغ', 'clientPhone': '0900000003', 'packageCount': 1})
    oid = r.json().get('data', {}).get('id')
    requests.patch(f'{BASE}/orders/{oid}', json={'status': 'accepted', 'driver': 'كابتن', 'driver_phone': '0901111111'})
    r2 = requests.patch(f'{BASE}/orders/{oid}', json={'status': 'loaded', 'collectedAmount': 8500.0})
    return r2.status_code == 200 and r2.json().get('data', {}).get('collectedAmount') == 8500.0, f'HTTP {r2.status_code}, collectedAmount: 8500'

# 9. Mark Failed Shipment
def test_failed_shipment():
    r = requests.post(f'{BASE}/orders', json={'clientName': 'فحص التعذر', 'clientPhone': '0900000004', 'packageCount': 1})
    oid = r.json().get('data', {}).get('id')
    requests.patch(f'{BASE}/orders/{oid}', json={'status': 'accepted', 'driver': 'كابتن', 'driver_phone': '0901111111'})
    r2 = requests.patch(f'{BASE}/orders/{oid}', json={'status': 'failed', 'failureReason': 'العميل لا يجيب على الهاتف'})
    return r2.status_code == 200, f'HTTP {r2.status_code}'

# 10. Delete Account & DB Anonymization
def test_delete_account_anonymization():
    test_phone = '0955443322'
    r = requests.post(f'{BASE}/auth/delete_account', json={'phone': test_phone})
    orders_resp = requests.get(f'{BASE}/orders')
    all_orders = orders_resp.json().get('data', [])
    for o in all_orders:
        if o.get('phone') == test_phone or o.get('client_phone') == test_phone:
            return False, 'Phone was not scrubbed from orders!'
    return r.status_code == 200, f'HTTP {r.status_code}, phone anonymized from orders table'

print('=== STARTING SENSITIVE ENDPOINTS TEST SUITE ===')
run_test('1. Customer Login', test_customer_login)
run_test('2. Customer Register (Dup Prevention)', test_customer_register_dup)
run_test('3. Create Order with Image', test_create_order)
run_test('4. Driver Register', test_driver_register)
run_test('5. Unapproved Driver Login (403)', test_unapproved_driver_login)
run_test('6. Unapproved Driver Accept Attempt (403)', test_unapproved_driver_accept)
run_test('7. Race Condition on Order Acceptance (409)', test_race_condition)
run_test('8. Loaded Status & Collected Amount', test_loaded_collected_amount)
run_test('9. Failed Shipment with Reason', test_failed_shipment)
run_test('10. Delete Account & DB Anonymization', test_delete_account_anonymization)

passed = sum(1 for r in results if r['ok'])
print(f'\nTotal Passed: {passed}/{len(results)}')
