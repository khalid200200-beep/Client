import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    "https://sudra.sa/support",
    "https://sudra.sa/privacy",
    "https://app.sudra.sa/support",
    "https://app.sudra.sa/privacy.html"
]

print("=== VERIFYING SUPPORT & PRIVACY LIVE URLS ===")
for u in urls:
    try:
        res = requests.get(u, timeout=15)
        print(f"URL: {u}")
        print(f"  Status Code: {res.status_code}")
        print(f"  Content Length: {len(res.text)} bytes")
        print(f"  Contains WhatsApp/Support: {'واتساب' in res.text or 'whatsapp' in res.text.lower() or 'support' in res.text.lower()}")
        print(f"  Contains Apple Privacy Data: {'الصور' in res.text or 'الموقع' in res.text or 'OTP' in res.text}")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"URL: {u} -> Error: {e}")
