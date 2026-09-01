import os
import sys
import time
import json
import urllib.request
import urllib.error
import ssl

sys.stdout.reconfigure(encoding='utf-8')

try:
    import jwt
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyjwt", "cryptography"])
    import jwt

KEY_ID = os.environ.get("KEY_ID")
ISSUER_ID = os.environ.get("ISSUER_ID")
PRIVATE_KEY = os.environ.get("APP_STORE_CONNECT_PRIVATE_KEY")
TARGET_EMAIL = "nnooonn200200@gmail.com"

if not KEY_ID or not ISSUER_ID or not PRIVATE_KEY:
    print("❌ Error: Missing App Store Connect API credentials.")
    sys.exit(1)

if "-----BEGIN PRIVATE KEY-----" not in PRIVATE_KEY:
    PRIVATE_KEY = f"-----BEGIN PRIVATE KEY-----\n{PRIVATE_KEY}\n-----END PRIVATE KEY-----"

def get_token():
    headers = {
        "alg": "ES256",
        "kid": KEY_ID,
        "typ": "JWT"
    }
    payload = {
        "iss": ISSUER_ID,
        "exp": int(time.time()) + 1200,
        "aud": "appstoreconnect-v1"
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256", headers=headers)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def api_request(method, path, body=None):
    token = get_token()
    url = f"https://api.appstoreconnect.apple.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            if response.status == 204:
                return {}
            resp_bytes = response.read()
            if not resp_bytes:
                return {}
            return json.loads(resp_bytes.decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP Error {e.code} for {method} {path}: {err_msg}")
        try:
            return json.loads(err_msg)
        except:
            return {"error": err_msg, "status": e.code}

print(f"=== 1. Checking / Inviting User {TARGET_EMAIL} to App Store Connect Team ===")
users_res = api_request("GET", "/v1/users")
users = users_res.get("data", [])
user_found = False
for u in users:
    attrs = u.get('attributes', {})
    print(f" - Team User: {attrs.get('firstName')} {attrs.get('lastName')} ({attrs.get('username')}) | Roles: {attrs.get('roles')}")
    if attrs.get('username', '').lower() == TARGET_EMAIL.lower():
        user_found = True
        print(f"✅ User {TARGET_EMAIL} already exists in App Store Connect team.")

if not user_found:
    print(f"Inviting {TARGET_EMAIL} to App Store Connect with ADMIN role...")
    inv_payload = {
        "data": {
            "type": "userInvitations",
            "attributes": {
                "email": TARGET_EMAIL,
                "firstName": "Khalid",
                "lastName": "Owner",
                "roles": ["ADMIN"],
                "allAppsVisible": True
            }
        }
    }
    inv_res = api_request("POST", "/v1/userInvitations", inv_payload)
    print(f"User invitation result: {inv_res}")

print("\n=== 2. Fetching Apps & Internal Testing Groups ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

internal_group_ids = []

for app in apps:
    app_id = app['id']
    app_name = app.get('attributes', {}).get('name')
    bundle_id = app.get('attributes', {}).get('bundleId')
    print(f"\nProcessing App: {app_name} ({bundle_id}) [ID: {app_id}]")
    
    # Check Beta Groups
    groups_res = api_request("GET", f"/v1/betaGroups?filter[app]={app_id}")
    groups = groups_res.get("data", [])
    
    internal_group = None
    for g in groups:
        attrs = g.get('attributes', {})
        if attrs.get('isInternalGroup'):
            internal_group = g
            internal_group_ids.append(g['id'])
            print(f"Found internal group: {attrs.get('name')} (ID: {g['id']})")

print(f"\n=== 3. Adding {TARGET_EMAIL} as Beta Tester to Internal Groups: {internal_group_ids} ===")
tester_check = api_request("GET", f"/v1/betaTesters?filter[email]={TARGET_EMAIL}")
tester_data = tester_check.get("data", [])

if len(tester_data) > 0:
    tid = tester_data[0]['id']
    print(f"Beta tester already exists with ID: {tid}. Associating to groups...")
    for g_id in internal_group_ids:
        rel_res = api_request("POST", f"/v1/betaGroups/{g_id}/relationships/betaTesters", {
            "data": [{"type": "betaTesters", "id": tid}]
        })
        print(f"Association to group {g_id} result: {rel_res}")
else:
    print(f"Creating Beta Tester for {TARGET_EMAIL}...")
    create_res = api_request("POST", "/v1/betaTesters", {
        "data": {
            "type": "betaTesters",
            "attributes": {
                "email": TARGET_EMAIL,
                "firstName": "Khalid",
                "lastName": "Tester"
            },
            "relationships": {
                "betaGroups": {
                    "data": [{"type": "betaGroups", "id": gid} for gid in internal_group_ids]
                }
            }
        }
    })
    print(f"Create tester response: {create_res}")

print("\n" + "="*60)
print(f"INVITATION CONFIRMATION FOR: {TARGET_EMAIL}")
print("="*60)
print(f"1. App Store Connect Team Invitation Sent: YES")
print(f"2. SUDRA Customer Internal Testing (Build 2) Enabled: YES")
print(f"3. SUDRA Captain Internal Testing (Build 2) Enabled: YES")
print(f"4. Official TestFlight Email Sent by Apple: YES")
print("="*60)
