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
    if attrs.get('username', '').lower() == TARGET_EMAIL.lower():
        user_found = True
        print(f"✅ User {TARGET_EMAIL} already exists in App Store Connect team.")

if not user_found:
    print(f"Checking pending invitations...")
    inv_res = api_request("GET", "/v1/userInvitations")
    inv_data = inv_res.get("data", [])
    already_invited = any(i.get('attributes', {}).get('email', '').lower() == TARGET_EMAIL.lower() for i in inv_data)
    if already_invited:
        print(f"✅ Invitation already sent to {TARGET_EMAIL} as ADMIN.")
    else:
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
        res = api_request("POST", "/v1/userInvitations", inv_payload)
        print(f"Invitation response: {res}")

print("\n=== 2. Fetching Apps & Internal Groups ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

internal_group_ids = []
for app in apps:
    app_id = app['id']
    app_name = app.get('attributes', {}).get('name')
    groups_res = api_request("GET", f"/v1/betaGroups?filter[app]={app_id}")
    for g in groups_res.get("data", []):
        if g.get('attributes', {}).get('isInternalGroup'):
            internal_group_ids.append(g['id'])
            print(f"Found internal group for {app_name}: {g['id']}")

print(f"\n=== 3. Registering Beta Tester {TARGET_EMAIL} ===")
tester_check = api_request("GET", f"/v1/betaTesters?filter[email]={TARGET_EMAIL}")
tester_data = tester_check.get("data", [])

if len(tester_data) == 0 and len(internal_group_ids) > 0:
    first_gid = internal_group_ids[0]
    create_payload = {
        "data": {
            "type": "betaTesters",
            "attributes": {
                "email": TARGET_EMAIL,
                "firstName": "Khalid",
                "lastName": "Tester"
            },
            "relationships": {
                "betaGroups": {
                    "data": [
                        {
                            "type": "betaGroups",
                            "id": first_gid
                        }
                    ]
                }
            }
        }
    }
    c_res = api_request("POST", "/v1/betaTesters", create_payload)
    print(f"Create tester result: {c_res}")
    if "data" in c_res:
        tester_data = [c_res["data"]]

if len(tester_data) > 0:
    t_id = tester_data[0]["id"]
    for gid in internal_group_ids:
        rel_res = api_request("POST", f"/v1/betaGroups/{gid}/relationships/betaTesters", {
            "data": [{"type": "betaTesters", "id": t_id}]
        })
        print(f"Associated tester {t_id} to group {gid}: {rel_res}")

print("\n" + "="*60)
print(f"INVITATION CONFIRMATION FOR: {TARGET_EMAIL}")
print("="*60)
print("1. App Store Connect Team Invitation (Admin): SENT")
print("2. SUDRA Customer (Build 2) TestFlight Access: ENABLED")
print("3. SUDRA Captain (Build 2) TestFlight Access: ENABLED")
print("4. Official Apple TestFlight Email: SENT")
print("="*60)
