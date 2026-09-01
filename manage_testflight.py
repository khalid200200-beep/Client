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

print("=== 1. Checking User Invitations ===")
inv_res = api_request("GET", "/v1/userInvitations")
invs = inv_res.get("data", [])
print(f"Found {len(invs)} pending user invitations:")
for inv in invs:
    attrs = inv.get('attributes', {})
    print(f" - Invitation ID: {inv.get('id')} | Email: {attrs.get('email')} | Roles: {attrs.get('roles')} | Expiration: {attrs.get('expirationDate')}")

print("\n=== 2. Checking Team Users ===")
users_res = api_request("GET", "/v1/users")
users = users_res.get("data", [])
for u in users:
    attrs = u.get('attributes', {})
    print(f" - User: {attrs.get('firstName')} {attrs.get('lastName')} | Email: {attrs.get('username')} | Roles: {attrs.get('roles')}")

print("\n=== 3. Checking Beta Testers ===")
testers_res = api_request("GET", "/v1/betaTesters")
testers = testers_res.get("data", [])
print(f"Found {len(testers)} total beta testers:")
for t in testers:
    attrs = t.get('attributes', {})
    print(f" - Tester ID: {t.get('id')} | Email: {attrs.get('email')} | Name: {attrs.get('firstName')} {attrs.get('lastName')} | State: {attrs.get('inviteType')}")

# Delete old pending invitations for TARGET_EMAIL and recreate fresh invitation
for inv in invs:
    if inv.get('attributes', {}).get('email', '').lower() == TARGET_EMAIL.lower():
        inv_id = inv.get('id')
        print(f"Deleting stale invitation {inv_id} for {TARGET_EMAIL}...")
        api_request("DELETE", f"/v1/userInvitations/{inv_id}")

print(f"\nCreating FRESH user invitation for {TARGET_EMAIL}...")
fresh_inv_payload = {
    "data": {
        "type": "userInvitations",
        "attributes": {
            "email": TARGET_EMAIL,
            "firstName": "Khalid",
            "lastName": "User",
            "roles": ["ADMIN"],
            "allAppsVisible": True
        }
    }
}
fresh_res = api_request("POST", "/v1/userInvitations", fresh_inv_payload)
print(f"Fresh invitation created: {fresh_res}")

print("\n=== 4. Checking Primary Developer Email ===")
print("Note: The main Apple Developer account holder is waildaoudi01@gmail.com.")
