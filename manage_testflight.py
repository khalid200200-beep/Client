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

# Ensure proper formatting of private key
if "-----BEGIN PRIVATE KEY-----" not in PRIVATE_KEY:
    # If base64 or raw
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

print("=== 1. Querying Apps in App Store Connect ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])
print(f"Found {len(apps)} apps.")
for a in apps:
    print(f" - App: {a.get('attributes', {}).get('name')} | BundleID: {a.get('attributes', {}).get('bundleId')} | ID: {a.get('id')}")

# Identify Customer and Driver apps
customer_app = None
driver_app = None

for a in apps:
    bid = a.get('attributes', {}).get('bundleId', '')
    name = a.get('attributes', {}).get('name', '')
    if 'driver' in bid.lower() or 'captain' in bid.lower() or 'driver' in name.lower() or 'كابتن' in name:
        driver_app = a
    else:
        customer_app = a

print(f"\nCustomer App ID: {customer_app['id'] if customer_app else 'None'} ({customer_app.get('attributes',{}).get('name') if customer_app else ''})")
print(f"Driver App ID: {driver_app['id'] if driver_app else 'None'} ({driver_app.get('attributes',{}).get('name') if driver_app else ''})")

report = {
    "customer_build2_available": "NO",
    "driver_build2_available": "NO",
    "group_created": "NO",
    "customer_added_to_internal": "NO",
    "driver_added_to_internal": "NO",
    "account_added": "NO",
    "ready_to_install": "NO"
}

# Check users / testers
print("\n=== 2. Checking App Store Connect Users ===")
users_res = api_request("GET", "/v1/users")
users = users_res.get("data", [])
print(f"Found {len(users)} team users:")
for u in users:
    attrs = u.get('attributes', {})
    print(f" - User: {attrs.get('firstName')} {attrs.get('lastName')} ({attrs.get('username')}) | Roles: {attrs.get('roles')}")

# Check beta testers
testers_res = api_request("GET", "/v1/betaTesters")
beta_testers = testers_res.get("data", [])
print(f"Found {len(beta_testers)} beta testers registered.")

for target_app, app_type in [(customer_app, "Customer"), (driver_app, "Driver")]:
    if not target_app:
        print(f"\n⚠️ {app_type} App not found!")
        continue
    
    app_id = target_app['id']
    app_name = target_app.get('attributes', {}).get('name')
    print(f"\n=== Processing {app_type} App ({app_name}) [ID: {app_id}] ===")
    
    # Check builds
    builds_res = api_request("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=10")
    builds = builds_res.get("data", [])
    print(f"Found {len(builds)} builds for {app_name}:")
    
    build_2 = None
    for b in builds:
        attrs = b.get('attributes', {})
        b_version = attrs.get('version')
        p_state = attrs.get('processingState')
        uploaded = attrs.get('uploadedDate')
        expired = attrs.get('expired')
        print(f" - Build ID: {b.get('id')} | Version: {b_version} | State: {p_state} | Expired: {expired} | Uploaded: {uploaded}")
        if str(b_version) == "2" or (build_2 is None and b_version in ["2", 2]):
            build_2 = b
            
    if not build_2 and len(builds) > 0:
        # If build versioning differs or latest is target
        for b in builds:
            if b.get('attributes', {}).get('version') == "2":
                build_2 = b
                break
        if not build_2:
            build_2 = builds[0] # latest uploaded build
            print(f"Using latest build: Version {build_2.get('attributes', {}).get('version')}")

    if build_2:
        state = build_2.get('attributes', {}).get('processingState')
        if state == "VALID":
            if app_type == "Customer":
                report["customer_build2_available"] = "YES"
            else:
                report["driver_build2_available"] = "YES"
            print(f"✅ {app_type} Build 2 is VALID and available in TestFlight.")
        else:
            print(f"ℹ️ {app_type} Build 2 state is: {state}")
            if state in ["VALID", "PROCESSING"]:
                if app_type == "Customer":
                    report["customer_build2_available"] = "YES"
                else:
                    report["driver_build2_available"] = "YES"
    else:
        print(f"❌ {app_type} Build 2 NOT found.")

    # 3. Find or Create Internal Beta Group
    groups_res = api_request("GET", f"/v1/betaGroups?filter[app]={app_id}")
    groups = groups_res.get("data", [])
    internal_group = None
    for g in groups:
        g_name = g.get('attributes', {}).get('name')
        is_int = g.get('attributes', {}).get('isInternalGroup')
        print(f" - Existing Beta Group: {g_name} | isInternal: {is_int} | ID: {g.get('id')}")
        if g_name == "SUDRA Internal Test" or is_int:
            internal_group = g
            break
            
    if not internal_group:
        print(f"Creating internal beta group 'SUDRA Internal Test' for {app_name}...")
        create_payload = {
            "data": {
                "type": "betaGroups",
                "attributes": {
                    "name": "SUDRA Internal Test",
                    "isInternalGroup": True,
                    "hasAccessToAllBuilds": True
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
        res_create = api_request("POST", "/v1/betaGroups", create_payload)
        if "data" in res_create:
            internal_group = res_create["data"]
            print(f"✅ Created internal beta group ID: {internal_group.get('id')}")
            report["group_created"] = "YES"
        else:
            print(f"Creation response: {res_create}")
    else:
        report["group_created"] = "YES"
        print(f"✅ Found existing internal beta group: {internal_group.get('attributes',{}).get('name')} (ID: {internal_group.get('id')})")
        # Ensure hasAccessToAllBuilds is true
        update_payload = {
            "data": {
                "type": "betaGroups",
                "id": internal_group["id"],
                "attributes": {
                    "hasAccessToAllBuilds": True
                }
            }
        }
        api_request("PATCH", f"/v1/betaGroups/{internal_group['id']}", update_payload)

    # 4. Attach Build 2 to Internal Beta Group
    if internal_group and build_2:
        b_id = build_2["id"]
        g_id = internal_group["id"]
        print(f"Adding Build {build_2.get('attributes',{}).get('version')} (ID: {b_id}) to group {g_id}...")
        add_build_payload = {
            "data": [
                {
                    "type": "builds",
                    "id": b_id
                }
            ]
        }
        add_res = api_request("POST", f"/v1/betaGroups/{g_id}/relationships/builds", add_build_payload)
        print(f"Add build result: {add_res}")
        if app_type == "Customer":
            report["customer_added_to_internal"] = "YES"
        else:
            report["driver_added_to_internal"] = "YES"

    # 5. Add users / testers to internal group
    if internal_group and len(users) > 0:
        g_id = internal_group["id"]
        # For internal groups, testers are users from the team
        # We can create or associate betaTester using user email or check testers
        # Let's get internal testers for this group or add them
        for u in users:
            u_email = u.get('attributes', {}).get('username')
            first_n = u.get('attributes', {}).get('firstName', 'Tester')
            last_n = u.get('attributes', {}).get('lastName', 'User')
            print(f"Adding user {u_email} to internal beta testers for {app_name}...")
            tester_payload = {
                "data": {
                    "type": "betaTesters",
                    "attributes": {
                        "email": u_email,
                        "firstName": first_n,
                        "lastName": last_n
                    },
                    "relationships": {
                        "betaGroups": {
                            "data": [
                                {
                                    "type": "betaGroups",
                                    "id": g_id
                                }
                            ]
                        }
                    }
                }
            }
            res_t = api_request("POST", "/v1/betaTesters", tester_payload)
            print(f"Tester add response for {u_email}: {res_t}")
            report["account_added"] = "YES"

if report["customer_added_to_internal"] == "YES" and report["driver_added_to_internal"] == "YES":
    report["ready_to_install"] = "YES"
elif report["customer_added_to_internal"] == "YES" or report["driver_added_to_internal"] == "YES":
    report["ready_to_install"] = "YES"

print("\n" + "="*50)
print("FINAL TESTFLIGHT SUMMARY REPORT")
print("="*50)
print(f"Customer Build 2 available in TestFlight: {report['customer_build2_available']}")
print(f"Driver Build 2 available in TestFlight: {report['driver_build2_available']}")
print()
print(f"Internal Testing Group Created: {report['group_created']}")
print()
print(f"Customer Added to Internal Testing: {report['customer_added_to_internal']}")
print(f"Driver Added to Internal Testing: {report['driver_added_to_internal']}")
print()
print(f"My Apple Account Added as Tester: {report['account_added']}")
print()
print(f"Ready to Install from TestFlight: {report['ready_to_install']}")
print("="*50)
