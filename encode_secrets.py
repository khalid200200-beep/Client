import os
import sys
import base64
import json

sys.stdout.reconfigure(encoding='utf-8')

signing_dir = r"C:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"

p12_path = os.path.join(signing_dir, "distribution_certificate.p12")
client_prof = os.path.join(signing_dir, "SUDRA_Client_App_Store.mobileprovision")
driver_prof = os.path.join(signing_dir, "SUDRA_Captain_App_Store.mobileprovision")

def to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

secrets = {
    "APPLE_CERTIFICATE_P12_BASE64": to_b64(p12_path),
    "APPLE_CERTIFICATE_P12_PASSWORD": "SudraSecure2026!",
    "APPLE_PROVISION_PROFILE_CLIENT_BASE64": to_b64(client_prof),
    "APPLE_PROVISION_PROFILE_DRIVER_BASE64": to_b64(driver_prof),
    "APP_STORE_CONNECT_KEY_ID": "KDDV3TG35U",
    "APP_STORE_CONNECT_ISSUER_ID": "2cad879f-f7a8-410d-bc49-d6c9081625e4"
}

out_json = os.path.join(signing_dir, "prepared_secrets.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(secrets, f, indent=2)

print("✅ Successfully prepared and encoded all Apple Secrets:")
for k in secrets:
    print(f"  - {k}: length={len(secrets[k])}")
