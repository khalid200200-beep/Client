import shutil
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

src = r"c:\Users\khalid\Downloads\تطبيق\SUDRA_Project_Source_v4\ios_signing\CertificateSigningRequest.certSigningRequest"

# Copy to root Downloads and Desktop for easy access in file dialog
dest1 = r"c:\Users\khalid\Downloads\CertificateSigningRequest.certSigningRequest"
dest2 = r"c:\Users\khalid\Desktop\CertificateSigningRequest.certSigningRequest"

shutil.copy2(src, dest1)
try:
    shutil.copy2(src, dest2)
except Exception:
    pass

print(f"✅ Copied CSR file to: {dest1}")
