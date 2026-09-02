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

print("=== 1. Fetching Apps ===")
apps_res = api_request("GET", "/v1/apps")
apps = apps_res.get("data", [])

results = {}

for app in apps:
    app_id = app['id']
    app_name = app.get('attributes', {}).get('name')
    bundle_id = app.get('attributes', {}).get('bundleId')
    
    is_driver = ('driver' in bundle_id.lower() or 'captain' in bundle_id.lower() or 'driver' in app_name.lower() or 'كابتن' in app_name)
    app_key = "Driver" if is_driver else "Customer"
    
    print(f"\n========================================================")
    print(f"Processing {app_key} App: {app_name} ({bundle_id}) [ID: {app_id}]")
    print(f"========================================================")
    
    results[app_key] = {
        "name": app_name,
        "build": "Build 2",
        "submission_status": "FAILED",
        "app_store_status": "UNKNOWN",
        "release_method": "Manual",
        "error": None
    }

    # 1. Get Build 2
    builds_res = api_request("GET", f"/v1/builds?filter[app]={app_id}&filter[version]=2")
    builds = builds_res.get("data", [])
    build_2 = None
    if builds:
        build_2 = builds[0]
    else:
        # Fallback to sorting by date
        all_builds = api_request("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate")
        for b in all_builds.get("data", []):
            if str(b.get("attributes", {}).get("version")) == "2":
                build_2 = b
                break
        if not build_2 and all_builds.get("data"):
            build_2 = all_builds.get("data")[0]

    if not build_2:
        print(f"❌ Could not find Build 2 for {app_name}")
        results[app_key]["error"] = "Build 2 not found"
        continue
    
    build_2_id = build_2['id']
    build_2_ver = build_2.get('attributes', {}).get('version')
    print(f"Found Build {build_2_ver} (ID: {build_2_id})")

    # 2. Get App Store Versions
    versions_res = api_request("GET", f"/v1/apps/{app_id}/appStoreVersions?include=build")
    versions = versions_res.get("data", [])
    
    # Target editable version (PREPARE_FOR_SUBMISSION, REJECTED, etc.)
    target_version = None
    for v in versions:
        state = v.get('attributes', {}).get('appStoreState')
        print(f" - App Store Version {v.get('attributes',{}).get('versionString')} (ID: {v['id']}) | State: {state} | ReleaseType: {v.get('attributes',{}).get('releaseType')}")
        if state in ["PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED", "WAITING_FOR_REVIEW"]:
            target_version = v
            break
            
    if not target_version and versions:
        target_version = versions[0]

    if not target_version:
        print(f"❌ No App Store Version found for {app_name}")
        results[app_key]["error"] = "No editable App Store Version found"
        continue

    version_id = target_version['id']
    version_str = target_version.get('attributes', {}).get('versionString')
    current_state = target_version.get('attributes', {}).get('appStoreState')
    
    # 3. Ensure Build 2 is attached to the App Store Version
    print(f"Attaching Build 2 to App Store Version {version_str}...")
    attach_build_payload = {
        "data": {
            "type": "builds",
            "id": build_2_id
        }
    }
    attach_res = api_request("PATCH", f"/v1/appStoreVersions/{version_id}/relationships/build", attach_build_payload)
    print(f"Attach build response: {attach_res}")

    # 4. Ensure Release Method is Manual (MANUAL)
    print(f"Setting Release Method to MANUAL...")
    patch_version_payload = {
        "data": {
            "type": "appStoreVersions",
            "id": version_id,
            "attributes": {
                "releaseType": "MANUAL"
            }
        }
    }
    patch_res = api_request("PATCH", f"/v1/appStoreVersions/{version_id}", patch_version_payload)
    print(f"Release method patch response: {patch_res}")

    # 5. Submit for Review
    # We will use modern Review Submission API (reviewSubmissions)
    print(f"Initiating App Store Review Submission...")
    
    # Check existing in-progress reviewSubmissions
    rev_check = api_request("GET", f"/v1/apps/{app_id}/reviewSubmissions?filter[state]=READY_FOR_REVIEW,IN_REVIEW,WAITING_FOR_REVIEW,UNRESOLVED_ISSUES")
    existing_subs = rev_check.get("data", [])
    
    submission_success = False
    
    if existing_subs:
        print(f"Found active review submission: {existing_subs[0]['id']}")
        sub_id = existing_subs[0]['id']
        sub_state = existing_subs[0].get('attributes', {}).get('state')
        # Submit if not already submitted
        submit_payload = {
            "data": {
                "type": "reviewSubmissions",
                "id": sub_id,
                "attributes": {
                    "submitted": True
                }
            }
        }
        submit_res = api_request("PATCH", f"/v1/reviewSubmissions/{sub_id}", submit_payload)
        print(f"Submit response: {submit_res}")
        if "data" in submit_res:
            submission_success = True
            current_state = submit_res.get("data", {}).get("attributes", {}).get("state", "WAITING_FOR_REVIEW")
        elif "errors" in submit_res:
            results[app_key]["error"] = submit_res["errors"]
    else:
        # Create new reviewSubmission
        create_sub_payload = {
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
        }
        create_sub_res = api_request("POST", "/v1/reviewSubmissions", create_sub_payload)
        print(f"Create reviewSubmission response: {create_sub_res}")
        
        if "data" in create_sub_res:
            sub_id = create_sub_res["data"]["id"]
            
            # Add App Store Version item to reviewSubmission
            item_payload = {
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
                                "id": version_id
                            }
                        }
                    }
                }
            }
            item_res = api_request("POST", "/v1/reviewSubmissionItems", item_payload)
            print(f"Add item response: {item_res}")
            
            # Now submit
            submit_payload = {
                "data": {
                    "type": "reviewSubmissions",
                    "id": sub_id,
                    "attributes": {
                        "submitted": True
                    }
                }
            }
            submit_res = api_request("PATCH", f"/v1/reviewSubmissions/{sub_id}", submit_payload)
            print(f"Submit PATCH response: {submit_res}")
            if "data" in submit_res:
                submission_success = True
                current_state = "Waiting for Review"
            elif "errors" in submit_res:
                results[app_key]["error"] = submit_res["errors"]
        else:
            # Fallback to legacy appStoreVersionSubmissions API
            print("Attempting legacy appStoreVersionSubmissions API...")
            legacy_payload = {
                "data": {
                    "type": "appStoreVersionSubmissions",
                    "relationships": {
                        "appStoreVersion": {
                            "data": {
                                "type": "appStoreVersions",
                                "id": version_id
                            }
                        }
                    }
                }
            }
            legacy_res = api_request("POST", "/v1/appStoreVersionSubmissions", legacy_payload)
            print(f"Legacy submission response: {legacy_res}")
            if "data" in legacy_res:
                submission_success = True
                current_state = "Waiting for Review"
            elif "errors" in legacy_res:
                results[app_key]["error"] = legacy_res["errors"]

    # Re-check updated App Store Version state
    final_ver_res = api_request("GET", f"/v1/appStoreVersions/{version_id}")
    final_state = final_ver_res.get("data", {}).get("attributes", {}).get("appStoreState", current_state)
    
    if final_state in ["WAITING_FOR_REVIEW", "IN_REVIEW", "PROCESSING_FOR_APP_STORE"] or submission_success:
        results[app_key]["submission_status"] = "Submitted Successfully"
        results[app_key]["app_store_status"] = "Waiting for Review" if final_state == "WAITING_FOR_REVIEW" else final_state
    else:
        results[app_key]["app_store_status"] = final_state

print("\n" + "="*60)
print("FINAL APP STORE SUBMISSION SUMMARY")
print("="*60)
print(json.dumps(results, indent=2, ensure_ascii=False))
print("="*60)
