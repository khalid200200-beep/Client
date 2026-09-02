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
        print(f"HTTP {e.code} for {method} {path}: {err_msg}")
        try:
            return json.loads(err_msg)
        except:
            return {"error": err_msg, "status": e.code}

print("=== FINAL APP STORE REVIEW SUBMISSION ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

final_report = {
    "customer": {},
    "driver": {},
    "raw_errors": {}
}

for app in apps:
    app_id = app['id']
    app_name = app.get('attributes', {}).get('name')
    bundle_id = app.get('attributes', {}).get('bundleId')
    
    is_driver = ('driver' in bundle_id.lower() or 'captain' in bundle_id.lower() or 'driver' in app_name.lower() or 'كابتن' in app_name)
    app_key = "driver" if is_driver else "customer"
    app_label = "DRIVER" if is_driver else "CUSTOMER"
    
    print(f"\n========================================================")
    print(f"SUBMITTING {app_label} APP: {app_name} ({bundle_id}) [ID: {app_id}]")
    print(f"========================================================")
    
    # 1. Fetch Version
    versions_res = api_request("GET", f"/v1/apps/{app_id}/appStoreVersions?include=build")
    versions = versions_res.get("data", [])
    target_ver = versions[0] if versions else None
    ver_id = target_ver['id'] if target_ver else None
    ver_str = target_ver.get('attributes', {}).get('versionString', '1.0.0') if target_ver else '1.0.0'
    
    # 2. Check Build Attached
    build_res = api_request("GET", f"/v1/appStoreVersions/{ver_id}/build") if ver_id else {}
    attached_build = build_res.get("data")
    b_version = attached_build.get('attributes', {}).get('version', '2') if attached_build else '2'
    
    rep = {
        "version": ver_str,
        "build": f"{b_version}",
        "submit_pass": "FAIL",
        "current_status": "PREPARE_FOR_SUBMISSION",
        "submission_id": "None"
    }

    # 3. Check / Get Review Submission
    rev_subs = api_request("GET", f"/v1/apps/{app_id}/reviewSubmissions?filter[state]=READY_FOR_REVIEW,UNRESOLVED_ISSUES,IN_REVIEW,WAITING_FOR_REVIEW")
    subs_list = rev_subs.get("data", [])
    
    current_sub = subs_list[0] if subs_list else None
    if not current_sub:
        create_sub = api_request("POST", "/v1/reviewSubmissions", {
            "data": {
                "type": "reviewSubmissions",
                "attributes": {
                    "platform": "IOS"
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
        })
        if "data" in create_sub:
            current_sub = create_sub["data"]

    sub_id = current_sub['id'] if current_sub else None
    rep["submission_id"] = str(sub_id) if sub_id else "None"
    
    # Ensure item added to review submission
    if current_sub:
        items_res = api_request("GET", f"/v1/reviewSubmissions/{sub_id}/items")
        items = items_res.get("data", [])
        has_item = any(i.get('relationships',{}).get('appStoreVersion',{}).get('data',{}).get('id') == ver_id for i in items)
        if not has_item:
            api_request("POST", "/v1/reviewSubmissionItems", {
                "data": {
                    "type": "reviewSubmissionItems",
                    "relationships": {
                        "reviewSubmission": {
                            "data": {
                                "type": "reviewSubmissions",
                                "id": sub_id
                            }
                        },
                        "appStoreVersion": {
                            "data": {
                                "type": "appStoreVersions",
                                "id": ver_id
                            }
                        }
                    }
                }
            })

    # 4. EXECUTE SUBMIT FOR REVIEW
    print(f"Executing Submit for Review on Submission ID: {sub_id}...")
    submit_res = api_request("PATCH", f"/v1/reviewSubmissions/{sub_id}", {
        "data": {
            "type": "reviewSubmissions",
            "id": sub_id,
            "attributes": {
                "submitted": True
            }
        }
    })
    print(f"Submit result: {submit_res}")
    
    if "data" in submit_res:
        rep["submit_pass"] = "PASS"
        sub_state = submit_res.get("data", {}).get("attributes", {}).get("state")
        rep["current_status"] = "Waiting for Review" if sub_state in ["WAITING_FOR_REVIEW", "READY_FOR_REVIEW"] else sub_state
    elif "errors" in submit_res:
        # Fallback to legacy appStoreVersionSubmissions API
        print("Attempting legacy appStoreVersionSubmissions API...")
        legacy_res = api_request("POST", "/v1/appStoreVersionSubmissions", {
            "data": {
                "type": "appStoreVersionSubmissions",
                "relationships": {
                    "appStoreVersion": {
                        "data": {
                            "type": "appStoreVersions",
                            "id": ver_id
                        }
                    }
                }
            }
        })
        print(f"Legacy submit result: {legacy_res}")
        if "data" in legacy_res:
            rep["submit_pass"] = "PASS"
            rep["current_status"] = "Waiting for Review"
        else:
            final_report["raw_errors"][app_key] = submit_res.get("errors", legacy_res.get("errors"))
            
    # Check final version state
    ver_check = api_request("GET", f"/v1/appStoreVersions/{ver_id}")
    final_ver_state = ver_check.get("data", {}).get("attributes", {}).get("appStoreState")
    if final_ver_state:
        if final_ver_state == "WAITING_FOR_REVIEW":
            rep["current_status"] = "Waiting for Review"
            rep["submit_pass"] = "PASS"
        elif final_ver_state in ["IN_REVIEW", "PROCESSING_FOR_APP_STORE"]:
            rep["current_status"] = final_ver_state
            rep["submit_pass"] = "PASS"
        else:
            if rep["submit_pass"] != "PASS":
                rep["current_status"] = final_ver_state

    final_report[app_key] = rep

print("\n" + "="*70)
print("FINAL SUBMISSION EXECUTION SUMMARY:")
print("="*70)
print(json.dumps(final_report, indent=2, ensure_ascii=False))
print("="*70)
