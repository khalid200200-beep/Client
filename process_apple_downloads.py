import os
import sys
import shutil
import glob
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

sys.stdout.reconfigure(encoding='utf-8')

downloads_dir = r"c:\Users\khalid\Downloads"
signing_dir = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"
os.makedirs(signing_dir, exist_ok=True)

# 1. Locate downloaded p8 file
p8_files = glob.glob(os.path.join(downloads_dir, "AuthKey_*.p8"))
if p8_files:
    latest_p8 = max(p8_files, key=os.path.getmtime)
    dest_p8 = os.path.join(signing_dir, os.path.basename(latest_p8))
    shutil.copy2(latest_p8, dest_p8)
    print(f"✅ Found and copied API Key p8: {dest_p8}")
else:
    print("⚠️ No AuthKey_*.p8 found in Downloads.")

# 2. Locate downloaded .cer file
cer_files = glob.glob(os.path.join(downloads_dir, "*.cer")) + glob.glob(os.path.join(downloads_dir, "distribution*.cer"))
if cer_files:
    latest_cer = max(cer_files, key=os.path.getmtime)
    dest_cer = os.path.join(signing_dir, os.path.basename(latest_cer))
    shutil.copy2(latest_cer, dest_cer)
    print(f"✅ Found and copied Certificate: {dest_cer}")

    # Convert .cer + private_key to .p12
    key_path = os.path.join(signing_dir, "distribution_private_key.key")
    if os.path.exists(key_path):
        with open(key_path, "rb") as kf:
            private_key = serialization.load_pem_private_key(kf.read(), password=None)
        
        with open(dest_cer, "rb") as cf:
            cer_bytes = cf.read()
            try:
                cert = x509.load_der_x509_certificate(cer_bytes)
            except Exception:
                cert = x509.load_pem_x509_certificate(cer_bytes)

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
        print(f"✅ Successfully created PKCS12 (.p12) bundle: {p12_path}")
else:
    print("⚠️ No .cer file found in Downloads.")

# 3. Locate mobileprovision files
prov_files = glob.glob(os.path.join(downloads_dir, "*.mobileprovision"))
for pf in prov_files:
    dest_pf = os.path.join(signing_dir, os.path.basename(pf))
    shutil.copy2(pf, dest_pf)
    print(f"✅ Found and copied Provisioning Profile: {dest_pf}")
