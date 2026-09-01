import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

repo = "khalid200200-beep/Client"
gh_exe = r"C:\Program Files\GitHub CLI\gh.exe"

private_key = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgkuK9S2cIGeqBRB6d
z6c/zPaHmJQ0qcs8bZWy6KOZGZGgCgYIKoZIzj0DAQehRANCAASIMhOyk/3GObkJ
+7YIyYzWH1SNwmcDOJIeKE9YAmlm4AUC2SqcKTOQV2jTbiTreb1RnLohP6xB+iw/
iUPjgFfe
-----END PRIVATE KEY-----"""

key_id = "KDDV3TG35U"
issuer_id = "2cad879f-f7a8-410d-bc49-d6c9081625e4"

secrets_to_set = {
    "APP_STORE_CONNECT_PRIVATE_KEY": private_key,
    "APP_STORE_CONNECT_KEY_ID": key_id,
    "APP_STORE_CONNECT_ISSUER_ID": issuer_id
}

for k, v in secrets_to_set.items():
    print(f"Setting {k} ...")
    proc = subprocess.run([gh_exe, "secret", "set", k, "-R", repo], input=v.encode('utf-8'), capture_output=True)
    if proc.returncode == 0:
        print(f"  ✅ Successfully set {k}")
    else:
        print(f"  ❌ Error: {proc.stderr.decode('utf-8')}")

print("\n--- Final List of GitHub Secrets ---")
subprocess.run([gh_exe, "secret", "list", "-R", repo])
