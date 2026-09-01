import sys
import json
import urllib.request
import ssl

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test_api(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    headers = {}
    body = None
    if data:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            raw = res.read().decode('utf-8')
            print(f"[{method}] {path} -> HTTP {res.status} | Length: {len(raw)}")
            try:
                parsed = json.loads(raw)
                print(f"   Response JSON: {json.dumps(parsed, ensure_ascii=False)[:120]}...")
            except:
                print(f"   RAW: {raw[:150]}...")
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8')
        print(f"[{method}] {path} -> HTTP {e.code} | Error: {raw[:150]}")
    except Exception as e:
        print(f"[{method}] {path} -> Failed: {e}")

print("=== 1. Test REST Login with Existing Phone 0551234567 ===")
test_api("/api/auth/login", method="POST", data={"phone": "0551234567", "password": "123456"})

print("\n=== 2. Test REST Login with New / Any Phone (Auto Registration / Flexible) ===")
test_api("/api/auth/login", method="POST", data={"phone": "0912345678", "password": "password123"})

print("\n=== 3. Test REST GET /api/orders ===")
test_api("/api/orders", method="GET")

print("\n=== 4. Test REST GET /api/banners ===")
test_api("/api/banners", method="GET")

print("\n=== 5. Test REST GET /api/drivers ===")
test_api("/api/drivers", method="GET")

print("\n=== 6. Test REST GET /api/clients ===")
test_api("/api/clients", method="GET")
