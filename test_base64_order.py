import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test creating an order with a Base64 sample image
fake_base64 = "data:image/jpeg;base64," + ("A" * 5000)

data = {
    "clientName": "عميل الاختبار",
    "clientPhone": "0559998877",
    "city": "الرياض",
    "packageCount": 1,
    "notes": "تجربة مع صورة base64",
    "imagePath": fake_base64,
    "image": fake_base64
}

req = urllib.request.Request("https://app.sudra.sa/api/orders", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
    print("Response status:", res.status)
    print("Response body:", res.read().decode('utf-8'))
