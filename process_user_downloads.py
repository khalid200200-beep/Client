import os
import sys
import shutil
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

sys.stdout.reconfigure(encoding='utf-8')

downloads = r"C:\Users\khalid\Downloads"
signing_dir = r"C:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"
os.makedirs(signing_dir, exist_ok=True)

# 1. Copy files
files_to_copy = [
    "distribution.cer",
    "SUDRA_Client_App_Store.mobileprovision",
    "SUDRA_Captain_App_Store.mobileprovision"
]

for fname in files_to_copy:
    # also check without extension or with .cer
    src = os.path.join(downloads, fname)
    if not os.path.exists(src) and fname == "distribution.cer":
        alt = os.path.join(downloads, "distribution")
        if os.path.exists(alt):
            src = alt
    if os.path.exists(src):
        dest = os.path.join(signing_dir, fname)
        shutil.copy2(src, dest)
        print(f"✅ Copied: {src} -> {dest}")
    else:
        print(f"⚠️ Not found: {src}")

# 2. Build .p12 certificate bundle
cert_path = os.path.join(signing_dir, "distribution.cer")
key_path = os.path.join(signing_dir, "distribution_private_key.key")

if os.path.exists(cert_path) and os.path.exists(key_path):
    with open(key_path, "rb") as kf:
        private_key = serialization.load_pem_private_key(kf.read(), password=None)

    with open(cert_path, "rb") as cf:
        cert_bytes = cf.read()
        try:
            cert = x509.load_der_x509_certificate(cert_bytes)
        except Exception:
            cert = x509.load_pem_x509_certificate(cert_bytes)

    p12_password = b"SudraSecure2026!"
    p12_data = pkcs12.serialize_key_and_certificates(
        name=b"Apple Distribution: Khalid Alomtiry",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(p12_password)
    )

    p12_path = os.path.join(signing_dir, "distribution_certificate.p12")
    with open(p12_path, "wb") as pf:
        pf.write(p12_data)

    print(f"✅ SUCCESS: Created .p12 Certificate: {p12_path}")
    print(f"🔑 P12 Password: SudraSecure2026!")
else:
    print(f"⚠️ Cannot build p12: cert={os.path.exists(cert_path)}, key={os.path.exists(key_path)}")
