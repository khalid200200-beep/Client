import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'https://app.sudra.sa/api'

print('=== 1. TEST LOGIN CLIENT ===')
r = requests.post(f'{BASE}/auth/login', json={'email': 'khalid_test_client@sudra.sa', 'password': 'password123'})
print(f'Status: {r.status_code}, Body: {r.text[:120]}')

print('\n=== 2. TEST REGISTER DRIVER (is_active=0) ===')
reg_data = {
    'name': 'كابتن فحص أمني',
    'email': 'driver_sec_test@sudra.sa',
    'phone': '0999887766',
    'city': 'الخرطوم',
    'vehiclePlate': 'خ 9999',
    'password': 'password123',
    'role': 'driver'
}
r = requests.post(f'{BASE}/auth/register', json=reg_data)
print(f'Status: {r.status_code}, Body: {r.text[:120]}')

print('\n=== 3. TEST LOGIN UNAPPROVED DRIVER (403 Expected) ===')
r = requests.post(f'{BASE}/auth/login', json={'email': 'driver_sec_test@sudra.sa', 'password': 'password123'})
is_pending = 'isPending' in r.text
print(f'Status: {r.status_code}, isPending detected: {is_pending}, Body: {r.text[:120]}')

print('\n=== 4. TEST CREATE ORDER ===')
order_data = {
    'clientName': 'خالد الأحمد',
    'clientPhone': '0911223344',
    'city': 'الخرطوم',
    'packageCount': 2,
    'notes': 'فحص شحنة حية واختبار القبول المتزامن',
    'imagePath': 'data:image/jpeg;base64,sample'
}
r = requests.post(f'{BASE}/orders', json=order_data)
order_id = r.json().get('data', {}).get('id')
print(f'Status: {r.status_code}, Created Order ID: {order_id}')

print('\n=== 5. TEST ACCEPT ORDER BY DRIVER A ===')
r = requests.patch(f'{BASE}/orders/{order_id}', json={'status': 'accepted', 'driver': 'كابتن أحمد', 'driver_phone': '0901234567'})
print(f'Status: {r.status_code}, Body: {r.text[:120]}')

print('\n=== 6. TEST RACE CONDITION (DRIVER B ACCEPTS SAME ORDER -> 409 CONFLICT) ===')
r = requests.patch(f'{BASE}/orders/{order_id}', json={'status': 'accepted', 'driver': 'كابتن محمد', 'driver_phone': '0907777777'})
print(f'Status: {r.status_code}, Body: {r.text[:120]}')

print('\n=== 7. TEST MARK LOADED WITH COLLECTED AMOUNT ===')
r = requests.patch(f'{BASE}/orders/{order_id}', json={'status': 'loaded', 'collectedAmount': 7500.0})
print(f'Status: {r.status_code}, Body: {r.text[:120]}')

print('\n=== 8. TEST GET ORDERS ===')
r = requests.get(f'{BASE}/orders')
orders = r.json().get('data', [])
print(f'Status: {r.status_code}, Total Orders Count: {len(orders)}')

print('\n=== 9. TEST DELETE ACCOUNT & ANONYMIZATION ===')
r = requests.post(f'{BASE}/auth/delete_account', json={'phone': '0911223344'})
print(f'Status: {r.status_code}, Body: {r.text[:120]}')

print('\n=== 10. VERIFY ANONYMIZATION OF CLIENT ORDERS IN DB ===')
r = requests.get(f'{BASE}/orders/{order_id}')
data = r.json().get('data', {})
print(f'Order {order_id} client_name: {data.get("client_name")}, client_phone: {data.get("client_phone")}, pickup_address: {data.get("pickup_address")}')
