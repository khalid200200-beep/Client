import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

CLEAN_ICON = r"c:\Users\khalid\Downloads\تطبيق فلاتر\clean_icon.png"

img = Image.open(CLEAN_ICON).convert('RGBA')
print(f"Clean icon loaded: {img.size}")

MIPMAP_SIZES = {
    'mipmap-mdpi': (48, 48),
    'mipmap-hdpi': (72, 72),
    'mipmap-xhdpi': (96, 96),
    'mipmap-xxhdpi': (144, 144),
    'mipmap-xxxhdpi': (192, 192),
}

def update_app_icons(app_path, app_name):
    print(f"\n--- Updating icons for {app_name} at {app_path} ---")
    res_dir = os.path.join(app_path, "android", "app", "src", "main", "res")
    
    for folder, size in MIPMAP_SIZES.items():
        target_dir = os.path.join(res_dir, folder)
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, "ic_launcher.png")
        
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(target_file, "PNG")
        print(f"Saved: {target_file} ({size[0]}x{size[1]})")

    assets_dir = os.path.join(app_path, "assets", "images")
    os.makedirs(assets_dir, exist_ok=True)
    
    logo_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    logo_512.save(os.path.join(assets_dir, "logo.png"), "PNG")
    logo_512.save(os.path.join(assets_dir, "app_icon.png"), "PNG")
    print(f"Saved assets in {assets_dir}")

# 1. Client App
update_app_icons(r"c:\Users\khalid\Downloads\تطبيق فلاتر\client_app", "Client App")

# 2. Driver App
update_app_icons(r"c:\Users\khalid\Downloads\تطبيق فلاتر\driver_app", "Driver App")

print("\n✅ All icons updated cleanly without white border!")
