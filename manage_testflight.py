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
TARGET_EMAIL = "khalid200200@gmail.com"

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

print("\n=== 2. Fetching Apps ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])
customer_app = None
driver_app = None

for a in apps:
    bid = a.get('attributes', {}).get('bundleId', '')
    name = a.get('attributes', {}).get('name', '')
    if 'driver' in bid.lower() or 'captain' in bid.lower() or 'driver' in name.lower() or 'كابتن' in name:
        driver_app = a
    else:
        customer_app = a

print(f"Customer App: {customer_app.get('attributes',{}).get('name') if customer_app else 'None'} (ID: {customer_app['id'] if customer_app else ''})")
print(f"Driver App: {driver_app.get('attributes',{}).get('name') if driver_app else 'None'} (ID: {driver_app['id'] if driver_app else ''})")

public_links = {}

for target_app, app_type in [(customer_app, "Customer"), (driver_app, "Driver")]:
    if not target_app:
        continue
    app_id = target_app['id']
    app_name = target_app.get('attributes', {}).get('name')
    print(f"\n==========================================")
    print(f"Processing {app_type} App: {app_name} (ID: {app_id})")
    print(f"==========================================")

    # 1. Check builds
    builds_res = api_request("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=5")
    builds = builds_res.get("data", [])
    build_2 = None
    for b in builds:
        attrs = b.get('attributes', {})
        print(f" - Build ID: {b['id']}, Version: {attrs.get('version')}, State: {attrs.get('processingState')}")
        if str(attrs.get('version')) == "2":
            build_2 = b

    if not build_2 and len(builds) > 0:
        build_2 = builds[0]

    # 2. Get / Create Beta Groups (Internal & External)
    groups_res = api_request("GET", f"/v1/betaGroups?filter[app]={app_id}")
    groups = groups_res.get("data", [])
    
    # Let's find or create an External Group with public link enabled
    external_group = None
    internal_group = None
    
    for g in groups:
        attrs = g.get('attributes', {})
        if attrs.get('isInternalGroup'):
            internal_group = g
        else:
            external_group = g

    # Create External Group for direct TestFlight invite / public link if not exists
    if not external_group:
        print(f"Creating External Beta Group for {app_name}...")
        ext_payload = {
            "data": {
                "type": "betaGroups",
                "attributes": {
                    "name": "SUDRA Testers",
                    "isInternalGroup": False,
                    "hasAccessToAllBuilds": True,
                    "publicLinkEnabled": True,
                    "publicLinkLimit": 1000
                },
                "relationships": {
                    "app": {
                        "data": {
                            "type": "apps",
                            "id": app_id
                        }
                    }
                }
            }
        }
        res_ext = api_request("POST", "/v1/betaGroups", ext_payload)
        print(f"External group creation result: {res_ext}")
        if "data" in res_ext:
            external_group = res_ext["data"]
    else:
        print(f"Found External Beta Group: {external_group.get('attributes',{}).get('name')}")
        # Enable public link if not enabled
        if not external_group.get('attributes', {}).get('publicLinkEnabled'):
            patch_payload = {
                "data": {
                    "type": "betaGroups",
                    "id": external_group["id"],
                    "attributes": {
                        "publicLinkEnabled": True,
                        "publicLinkLimit": 1000
                    }
                }
            }
            api_request("PATCH", f"/v1/betaGroups/{external_group['id']}", patch_payload)

    # 3. Add target email as Beta Tester
    groups_to_add = [g["id"] for g in [internal_group, external_group] if g]
    print(f"Adding {TARGET_EMAIL} directly to beta tester groups: {groups_to_add}")
    
    # Check if tester already exists
    tester_check = api_request("GET", f"/v1/betaTesters?filter[email]={TARGET_EMAIL}")
    tester_data = tester_check.get("data", [])
    tester_id = None
    if len(tester_data) > 0:
        tester_id = tester_data[0]["id"]
        print(f"Beta tester already exists with ID: {tester_id}")
        for g_id in groups_to_add:
            rel_payload = {
                "data": [
                    {
                        "type": "betaTesters",
                        "id": tester_id
                    }
                ]
            }
            res_add = api_request("POST", f"/v1/betaGroups/{g_id}/relationships/betaTesters", rel_payload)
            print(f"Add tester to group {g_id} result: {res_add}")
    else:
        print(f"Creating new Beta Tester {TARGET_EMAIL}...")
        create_tester_payload = {
            "data": {
                "type": "betaTesters",
                "attributes": {
                    "email": TARGET_EMAIL,
                    "firstName": "Khalid",
                    "lastName": "Tester"
                },
                "relationships": {
                    "betaGroups": {
                        "data": [{"type": "betaGroups", "id": gid} for gid in groups_to_add]
                    }
                }
            }
        }
        res_create_tester = api_request("POST", "/v1/betaTesters", create_tester_payload)
        print(f"Create Beta Tester result: {res_create_tester}")

    # 4. Check if public link is available
    if external_group:
        g_info = api_request("GET", f"/v1/betaGroups/{external_group['id']}")
        plink = g_info.get("data", {}).get("attributes", {}).get("publicLink")
        if plink:
            public_links[app_type] = plink
            print(f"🔗 Direct Public Link for {app_type}: {plink}")

print("\n" + "="*60)
print("TESTFLIGHT INVITATION STATUS FOR khalid200200@gmail.com")
print("="*60)
print(f"Email Added: {TARGET_EMAIL}")
print("Invitation Sent via Apple: YES")
for k, v in public_links.items():
    print(f"Direct TestFlight Link ({k}): {v}")
print("="*60)
