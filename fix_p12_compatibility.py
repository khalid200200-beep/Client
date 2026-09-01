import os
import sys
import subprocess
import base64

sys.stdout.reconfigure(encoding='utf-8')

openssl = r"C:\Program Files\Git\mingw64\bin\openssl.exe"
provider_path = r"C:\Program Files\Git\mingw64\lib\ossl-modules"
signing_dir = r"C:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"

cer_path = os.path.join(signing_dir, "distribution.cer")
key_path = os.path.join(signing_dir, "distribution_private_key.key")
pem_cert_path = os.path.join(signing_dir, "distribution.pem")
p12_path = os.path.join(signing_dir, "distribution_certificate.p12")

# 1. Convert DER .cer to PEM locally
cmd1 = [openssl, "x509", "-inform", "DER", "-in", cer_path, "-out", pem_cert_path]
res1 = subprocess.run(cmd1, capture_output=True, text=True)
if res1.returncode != 0:
    print(f"❌ Failed to convert DER to PEM: {res1.stderr}")
    sys.exit(1)
print("✅ Converted Apple distribution certificate to PEM format locally.")

# 2. Convert PEM cert + Key to legacy PKCS12 with explicit provider path
password = "SudraSecure2026!"
cmd2 = [
    openssl, "pkcs12", "-export",
    "-provider-path", provider_path,
    "-provider", "default",
    "-provider", "legacy",
    "-inkey", key_path,
    "-in", pem_cert_path,
    "-out", p12_path,
    "-name", "Apple Distribution: Khalid Alomtiry",
    "-passout", f"pass:{password}"
]
res2 = subprocess.run(cmd2, capture_output=True, text=True)
if res2.returncode != 0:
    print(f"❌ Failed to export PKCS12: {res2.stderr}")
    sys.exit(1)
print("✅ Exported PKCS12 certificate bundle with macOS-compatible legacy encryption.")

# 3. Verify the generated P12 locally
cmd3 = [
    openssl, "pkcs12", "-info",
    "-provider-path", provider_path,
    "-provider", "default",
    "-provider", "legacy",
    "-in", p12_path,
    "-noout",
    "-passin", f"pass:{password}"
]
res3 = subprocess.run(cmd3, capture_output=True, text=True)
if res3.returncode != 0:
    print(f"❌ P12 Verification Failed: {res3.stderr}")
    sys.exit(1)
print("✅ Verified PKCS12 certificate bundle integrity successfully.")

# 4. Read new p12 and encode base64
with open(p12_path, "rb") as f:
    p12_b64 = base64.b64encode(f.read()).decode('utf-8')

# 5. Update GitHub secret APPLE_CERTIFICATE_P12_BASE64
gh_exe = r"C:\Program Files\GitHub CLI\gh.exe"
repo = "khalid200200-beep/Client"

proc = subprocess.run(
    [gh_exe, "secret", "set", "APPLE_CERTIFICATE_P12_BASE64", "-R", repo],
    input=p12_b64.encode('utf-8'),
    capture_output=True
)
if proc.returncode == 0:
    print("✅ Successfully updated GitHub secret APPLE_CERTIFICATE_P12_BASE64.")
else:
    print(f"❌ Error updating GitHub Secret: {proc.stderr.decode('utf-8', errors='ignore')}")
    sys.exit(1)

# Clean up temp PEM
if os.path.exists(pem_cert_path):
    os.remove(pem_cert_path)
