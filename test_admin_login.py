import json
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://app.sudra.sa"

def test_login(email, password):
    url = f"{BASE}/api/auth/admin-login"
    data = json.dumps({"email": email, "password": password}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
        print("admin-login:", res.status, res.read().decode('utf-8'))

test_login("KHALID200200@GMAIL.COM", "123456")
test_login("khalid200200@gmail.com", "123456")
