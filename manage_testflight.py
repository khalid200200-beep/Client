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

print("=== 1. Detailed Inspection of Apps and Builds ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

for app in apps:
    app_id = app['id']
    app_name = app.get('attributes', {}).get('name')
    print(f"\n========================================================")
    print(f"APP: {app_name} (ID: {app_id})")
    print(f"========================================================")

    # 1. Builds with relationships
    builds_res = api_request("GET", f"/v1/builds?filter[app]={app_id}&include=betaBuildLocalizations,buildBetaDetail,preReleaseVersion&limit=5")
    builds = builds_res.get("data", [])
    included = builds_res.get("included", [])
    
    print(f"Found {len(builds)} builds:")
    for b in builds:
        attrs = b.get('attributes', {})
        b_id = b['id']
        version = attrs.get('version')
        state = attrs.get('processingState')
        expired = attrs.get('expired')
        min_os = attrs.get('minOsVersion')
        uses_non_exempt = attrs.get('usesNonExemptEncryption')
        
        print(f"\n -> Build {version} (ID: {b_id}):")
        print(f"    - Processing State: {state}")
        print(f"    - Expired: {expired}")
        print(f"    - Uses Non Exempt Encryption: {uses_non_exempt}")
        
        # Check if missing encryption compliance
        if uses_non_exempt is None:
            print(f"    ⚠️ Encryption compliance NOT set! Setting usesNonExemptEncryption to False...")
            patch_enc = {
                "data": {
                    "type": "builds",
                    "id": b_id,
                    "attributes": {
                        "usesNonExemptEncryption": False
                    }
                }
            }
            res_enc = api_request("PATCH", f"/v1/builds/{b_id}", patch_enc)
            print(f"    Encryption patch response: {res_enc}")

        # Check betaBuildLocalizations (What to test)
        loc_res = api_request("GET", f"/v1/builds/{b_id}/betaBuildLocalizations")
        locs = loc_res.get("data", [])
        print(f"    - Beta Localizations count: {len(locs)}")
        if len(locs) == 0:
            print(f"    Creating 'What to test' localization for build {version}...")
            create_loc = {
                "data": {
                    "type": "betaBuildLocalizations",
                    "attributes": {
                        "locale": "en-US",
                        "whatsNew": "Initial internal test build for SUDRA."
                    },
                    "relationships": {
                        "build": {
                            "data": {
                                "type": "builds",
                                "id": b_id
                            }
                        }
                    }
                }
            }
            res_loc = api_request("POST", "/v1/betaBuildLocalizations", create_loc)
            print(f"    Localization result: {res_loc}")

    # 2. Beta Groups & Testers
    groups_res = api_request("GET", f"/v1/betaGroups?filter[app]={app_id}&include=betaTesters,builds")
    groups = groups_res.get("data", [])
    print(f"\nBeta Groups for {app_name}:")
    for g in groups:
        g_id = g['id']
        g_attrs = g.get('attributes', {})
        print(f" -> Group: {g_attrs.get('name')} | isInternal: {g_attrs.get('isInternalGroup')} | hasAccessToAllBuilds: {g_attrs.get('hasAccessToAllBuilds')} | ID: {g_id}")
        
        # Check testers in group
        g_testers_res = api_request("GET", f"/v1/betaGroups/{g_id}/betaTesters")
        g_testers = g_testers_res.get("data", [])
        print(f"    Testers in group ({len(g_testers)}):")
        for gt in g_testers:
            gt_attrs = gt.get('attributes', {})
            print(f"      * {gt_attrs.get('email')} ({gt_attrs.get('firstName')} {gt_attrs.get('lastName')}) | ID: {gt['id']}")

        # Check builds in group
        g_builds_res = api_request("GET", f"/v1/betaGroups/{g_id}/builds")
        g_builds = g_builds_res.get("data", [])
        print(f"    Builds in group: {[gb.get('attributes',{}).get('version') for gb in g_builds]}")

print("\n=== Inspection and Auto-Repair Completed ===")
