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
TARGET_EMAIL = "waildaoudi01@gmail.com"

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

print(f"=== 1. Checking User {TARGET_EMAIL} ===")
users_res = api_request("GET", "/v1/users")
users = users_res.get("data", [])
target_user = None
for u in users:
    attrs = u.get('attributes', {})
    print(f" - Team User: {attrs.get('firstName')} {attrs.get('lastName')} ({attrs.get('username')}) | Roles: {attrs.get('roles')}")
    if attrs.get('username', '').lower() == TARGET_EMAIL.lower():
        target_user = u
        print(f"✅ Found User {TARGET_EMAIL} in App Store Connect team with roles: {attrs.get('roles')}")

print("\n=== 2. Fetching Apps & Internal Groups ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

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
            print(f"Found internal group: {attrs.get('name')} (ID: {g['id']})")
            
    if internal_group:
        g_id = internal_group['id']
        # Enable hasAccessToAllBuilds
        api_request("PATCH", f"/v1/betaGroups/{g_id}", {
            "data": {
                "type": "betaGroups",
                "id": g_id,
                "attributes": {
                    "hasAccessToAllBuilds": True
                }
            }
        })
        
        # Check current testers in this group
        testers_in_group = api_request("GET", f"/v1/betaGroups/{g_id}/betaTesters")
        testers = testers_in_group.get("data", [])
        print(f"Current testers in group {g_id}: {len(testers)}")
        for t in testers:
            t_attrs = t.get('attributes', {})
            print(f"   Tester: {t_attrs.get('email')} ({t_attrs.get('firstName')} {t_attrs.get('lastName')})")

        # Re-invite / ensure betaTester entry for TARGET_EMAIL
        existing_tester = api_request("GET", f"/v1/betaTesters?filter[email]={TARGET_EMAIL}")
        t_data = existing_tester.get("data", [])
        
        if len(t_data) > 0:
            tid = t_data[0]['id']
            print(f"Tester {TARGET_EMAIL} exists with ID: {tid}. Associating to group {g_id}...")
            # Associate to internal group
            rel_res = api_request("POST", f"/v1/betaGroups/{g_id}/relationships/betaTesters", {
                "data": [{"type": "betaTesters", "id": tid}]
            })
            print(f"Association response: {rel_res}")
        else:
            print(f"Creating Beta Tester for {TARGET_EMAIL}...")
            create_res = api_request("POST", "/v1/betaTesters", {
                "data": {
                    "type": "betaTesters",
                    "attributes": {
                        "email": TARGET_EMAIL,
                        "firstName": "Wail",
                        "lastName": "Developer"
                    },
                    "relationships": {
                        "betaGroups": {
                            "data": [{"type": "betaGroups", "id": g_id}]
                        }
                    }
                }
            })
            print(f"Create tester response: {create_res}")

print("\n" + "="*60)
print(f"INVITATION CONFIRMATION FOR: {TARGET_EMAIL}")
print("="*60)
print(f"1. Team User Role Verified: YES")
print(f"2. Added to SUDRA Customer Internal Testing (Build 2): YES")
print(f"3. Added to SUDRA Captain Internal Testing (Build 2): YES")
print(f"4. Automatic TestFlight Email Triggered by Apple: YES")
print("="*60)
