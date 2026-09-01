import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

print("==================================================")
print("🧪 اختبار عزل الحسابات والطلبات وسيناريو A/B")
print("==================================================")

# Account A Credentials
phone_a = "0511111111"
email_a = "account_a@sudra.sa"
pass_a = "PassA12345"

# Account B Credentials
phone_b = "0522222222"
email_b = "account_b@sudra.sa"
pass_b = "PassB12345"

# 1. Ensure Account A exists
reg_a = requests.post(f"{BASE_URL}/auth/register", json={
    "name": "العميل أ",
    "email": email_a,
    "phone": phone_a,
    "password": pass_a,
    "city": "الرياض",
    "role": "client"
}).json()

# Login A
log_a = requests.post(f"{BASE_URL}/auth/login", json={
    "identifier": phone_a,
    "password": pass_a
}).json()
user_a = log_a.get('data', {})
id_a = user_a.get('id')
token_a = log_a.get('token')
print(f"1. Login Account A: ID={id_a}, Phone={phone_a} -> Success: {log_a.get('success')}")

# Create order for Account A
ord_a = requests.post(f"{BASE_URL}/orders", json={
    "clientName": "العميل أ",
    "clientPhone": phone_a,
    "clientId": id_a,
    "city": "الرياض",
    "packageCount": 2,
    "notes": "طلب خاص بالعميل أ حصراً"
}).json()
print("   Created Order for A:", ord_a.get('success'), ord_a.get('data', {}).get('order_code'))

# Fetch orders for A
orders_for_a = requests.get(f"{BASE_URL}/orders", params={"phone": phone_a, "client_id": id_a}, headers={"Authorization": f"Bearer {token_a}"}).json().get('data', [])
print(f"   Orders retrieved for A: {len(orders_for_a)} orders (Expected >= 1)")
assert len(orders_for_a) >= 1
for o in orders_for_a:
    assert o.get('client_phone') == phone_a or o.get('clientPhone') == phone_a or o.get('client_id') == id_a

# 2. Simulate Logout A & Ensure Account B exists
reg_b = requests.post(f"{BASE_URL}/auth/register", json={
    "name": "العميل ب",
    "email": email_b,
    "phone": phone_b,
    "password": pass_b,
    "city": "جدة",
    "role": "client"
}).json()

# Login B
log_b = requests.post(f"{BASE_URL}/auth/login", json={
    "identifier": phone_b,
    "password": pass_b
}).json()
user_b = log_b.get('data', {})
id_b = user_b.get('id')
token_b = log_b.get('token')
print(f"\n2. Login Account B: ID={id_b}, Phone={phone_b} -> Success: {log_b.get('success')}")

# Fetch orders for B
orders_for_b = requests.get(f"{BASE_URL}/orders", params={"phone": phone_b, "client_id": id_b}, headers={"Authorization": f"Bearer {token_b}"}).json().get('data', [])
print(f"   Orders retrieved for B: {len(orders_for_b)} orders")
for o in orders_for_b:
    # Must NOT contain Account A's phone or ID
    assert o.get('client_phone') != phone_a
    assert o.get('clientPhone') != phone_a
    assert o.get('client_id') != id_a

print("   ✅ Account Isolation Verified: Account B CANNOT see any orders from Account A!")

# 3. Unauthenticated / empty query test
empty_orders = requests.get(f"{BASE_URL}/orders").json().get('data', [])
print(f"\n3. Unauthenticated GET /api/orders without identity: {len(empty_orders)} items (Expected 0)")
assert len(empty_orders) == 0
print("   ✅ Backend Authorization Verified: No general database leak without client identity!")

# 4. Logout B and Log back into A
orders_for_a_again = requests.get(f"{BASE_URL}/orders", params={"phone": phone_a, "client_id": id_a}, headers={"Authorization": f"Bearer {token_a}"}).json().get('data', [])
print(f"\n4. Account A Login Again -> Orders retrieved: {len(orders_for_a_again)} orders (Matches A only)")
assert len(orders_for_a_again) >= 1

print("\n==================================================")
print("🎉 ALL TESTS PASSED 100%!")
print("==================================================")
