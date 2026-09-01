import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

print("==================================================")
print("🛡️ اختبار التحقق وعزل الأدوار بين العميل والسائق")
print("==================================================")

# 1. Register / Ensure Client Account
client_phone = "0533333333"
client_email = "test_client_role@sudra.sa"
client_pass = "ClientPass123"

requests.post(f"{BASE_URL}/auth/register", json={
    "name": "عميل تجربة الأدوار",
    "email": client_email,
    "phone": client_phone,
    "password": client_pass,
    "city": "الرياض",
    "role": "client"
})

# 2. Register / Ensure Driver Account (and ensure active)
driver_phone = "0544444444"
driver_email = "test_driver_role@sudra.sa"
driver_pass = "DriverPass123"

requests.post(f"{BASE_URL}/auth/register", json={
    "name": "كابتن تجربة الأدوار",
    "email": driver_email,
    "phone": driver_phone,
    "password": driver_pass,
    "city": "الرياض",
    "role": "driver",
    "vehicle_plate": "أ ب ج 1234"
})

# Activate driver in DB directly via SSH/API or ensure is_active
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=15)
stdin, stdout, stderr = ssh.exec_command(f"mysql -u root -pe250eb38de998d02 shipping_db -e \"UPDATE users SET is_active = 1 WHERE phone = '{driver_phone}';\"")
stdout.read()
ssh.close()

# TEST 1: Client -> Client Login Endpoint
res_c_to_c = requests.post(f"{BASE_URL}/auth/client/login", json={
    "identifier": client_phone,
    "password": client_pass
})
print(f"1. Client -> Client App: Status={res_c_to_c.status_code}, Success={res_c_to_c.json().get('success')}")
assert res_c_to_c.status_code == 200
assert res_c_to_c.json().get('success') == True
client_token = res_c_to_c.json().get('data', {}).get('token')
print("   ✅ Test 1 PASS: Client successfully logs into Client App.")

# TEST 2: Client -> Driver Login Endpoint (MUST FAIL 403)
res_c_to_d = requests.post(f"{BASE_URL}/auth/driver/login", json={
    "identifier": client_phone,
    "password": client_pass
})
print(f"\n2. Client -> Driver App: Status={res_c_to_d.status_code}, Msg='{res_c_to_d.json().get('message')}'")
assert res_c_to_d.status_code == 403
assert res_c_to_d.json().get('success') == False
print("   ✅ Test 2 PASS: Client BLOCKED from Driver App (403 Forbidden).")

# TEST 3: Driver -> Driver Login Endpoint
res_d_to_d = requests.post(f"{BASE_URL}/auth/driver/login", json={
    "identifier": driver_phone,
    "password": driver_pass
})
print(f"\n3. Driver -> Driver App: Status={res_d_to_d.status_code}, Success={res_d_to_d.json().get('success')}")
assert res_d_to_d.status_code == 200
assert res_d_to_d.json().get('success') == True
driver_token = res_d_to_d.json().get('data', {}).get('token')
print("   ✅ Test 3 PASS: Driver successfully logs into Driver App.")

# TEST 4: Driver -> Client Login Endpoint (MUST FAIL 403)
res_d_to_c = requests.post(f"{BASE_URL}/auth/client/login", json={
    "identifier": driver_phone,
    "password": driver_pass
})
print(f"\n4. Driver -> Client App: Status={res_d_to_c.status_code}, Msg='{res_d_to_c.json().get('message')}'")
assert res_d_to_c.status_code == 403
assert res_d_to_c.json().get('success') == False
print("   ✅ Test 4 PASS: Driver BLOCKED from Client App (403 Forbidden).")

# TEST 5: Token Role Validation (Client token trying to accept order as driver -> MUST FAIL 403)
# Create a dummy order first
create_ord = requests.post(f"{BASE_URL}/orders", json={
    "clientName": "عميل الاختبار",
    "clientPhone": client_phone,
    "city": "الرياض",
    "packageCount": 1,
    "notes": "اختبار حماية التوكن"
}).json()
ord_id = create_ord.get('data', {}).get('id')

# Attempt accept with client token
res_tamper = requests.post(f"{BASE_URL}/orders/{ord_id}/accept", 
    headers={"Authorization": f"Bearer {client_token}"},
    json={"driverPhone": client_phone, "driverName": "عميل منتحل صفة كابتن"}
)
print(f"\n5. Client Token Tampering Driver API: Status={res_tamper.status_code}, Msg='{res_tamper.json().get('message')}'")
assert res_tamper.status_code == 403
print("   ✅ Test 5 PASS: Backend Role Authorization protects driver endpoints from client tokens!")

print("\n==================================================")
print("🎉 ALL ROLE ISOLATION TESTS PASSED 100%!")
print("==================================================")
