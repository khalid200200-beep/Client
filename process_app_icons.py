import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ICON_SRC = r"C:\Users\khalid\.gemini\antigravity-ide\brain\c00ea2bc-656f-47f0-9735-bc82bac3b2b7\.user_uploaded\media_1787997435387.jpg"

if not os.path.exists(ICON_SRC):
    print(f"Error: {ICON_SRC} not found!")
    sys.exit(1)

img = Image.open(ICON_SRC)
print(f"Source Image loaded: {img.size}, mode: {img.mode}")

# Ensure RGB
if img.mode != 'RGB':
    img = img.convert('RGB')

# Sizes for Android mipmaps
MIPMAP_SIZES = {
    'mipmap-mdpi': (48, 48),
    'mipmap-hdpi': (72, 72),
    'mipmap-xhdpi': (96, 96),
    'mipmap-xxhdpi': (144, 144),
    'mipmap-xxxhdpi': (192, 192),
}

def generate_icons_for_app(app_path, app_name):
    print(f"\n--- Generating icons for {app_name} at {app_path} ---")
    res_dir = os.path.join(app_path, "android", "app", "src", "main", "res")
    
    for folder, size in MIPMAP_SIZES.items():
        target_dir = os.path.join(res_dir, folder)
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, "ic_launcher.png")
        
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(target_file, "PNG")
        print(f"Saved: {target_file} ({size[0]}x{size[1]})")

    # Also save high-res assets in flutter
    assets_dir = os.path.join(app_path, "assets", "images")
    os.makedirs(assets_dir, exist_ok=True)
    
    logo_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    logo_512.save(os.path.join(assets_dir, "logo.png"), "PNG")
    logo_512.save(os.path.join(assets_dir, "app_icon.png"), "PNG")
    print(f"Saved Flutter assets in {assets_dir}")

# 1. Client App
client_dir = r"c:\Users\khalid\Downloads\تطبيق فلاتر\client_app"
generate_icons_for_app(client_dir, "Client App")

# 2. Driver App
driver_dir = r"c:\Users\khalid\Downloads\تطبيق فلاتر\driver_app"
generate_icons_for_app(driver_dir, "Driver App")

print("\n✅ All icon resolutions successfully generated and placed!")
