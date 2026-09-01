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

print("=== 1. Querying Apps & Beta Testers ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

testers_res = api_request("GET", "/v1/betaTesters")
testers = testers_res.get("data", [])

print(f"Total Beta Testers found: {len(testers)}")
for t in testers:
    t_attrs = t.get('attributes', {})
    print(f" - Tester: {t_attrs.get('email')} | ID: {t.get('id')}")

for app in apps:
    app_id = app['id']
    app_name = app.get('attributes', {}).get('name')
    print(f"\nTriggering direct TestFlight invitations for App: {app_name} (ID: {app_id})...")
    
    for t in testers:
        t_id = t['id']
        t_email = t.get('attributes', {}).get('email')
        
        inv_payload = {
            "data": {
                "type": "betaTesterInvitations",
                "relationships": {
                    "betaTester": {
                        "data": {
                            "type": "betaTesters",
                            "id": t_id
                        }
                    },
                    "app": {
                        "data": {
                            "type": "apps",
                            "id": app_id
                        }
                    }
                }
            }
        }
        res = api_request("POST", "/v1/betaTesterInvitations", inv_payload)
        print(f" -> Sent direct invite for {t_email} on {app_name}: {res}")

print("\n" + "="*60)
print("TESTFLIGHT INVITATION EMAILS DISPATCHED DIRECTLY FROM APPLE")
print("="*60)
