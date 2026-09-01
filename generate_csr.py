import os
import sys
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

sys.stdout.reconfigure(encoding='utf-8')

out_dir = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing"
os.makedirs(out_dir, exist_ok=True)

key_path = os.path.join(out_dir, "distribution_private_key.key")
csr_path = os.path.join(out_dir, "CertificateSigningRequest.certSigningRequest")

# Generate RSA 2048 private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Write private key
with open(key_path, "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Generate CSR
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.EMAIL_ADDRESS, "waildaoudi01@gmail.com"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Khalid Alomtiry"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "SA"),
])).sign(private_key, hashes.SHA256())

with open(csr_path, "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))

print(f"✅ Generated Private Key: {key_path}")
print(f"✅ Generated CSR: {csr_path}")
