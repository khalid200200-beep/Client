import os
import sys
from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding='utf-8')

ICON_SRC = r"C:\Users\khalid\.gemini\antigravity-ide\brain\c00ea2bc-656f-47f0-9735-bc82bac3b2b7\.user_uploaded\media_1787997435387.jpg"

img = Image.open(ICON_SRC).convert('RGBA')
print(f"Original size: {img.size}")

# Let's inspect pixel colors at corners and find the bounding box of non-white content
# White is (255, 255, 255)
# In the image, the outer background is pure white #FFFFFF or very close (e.g. > 250)

# Let's find the bounding box of the actual squircle icon
bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
diff = ImageChops.difference(img, bg)
bbox = diff.getbbox()
print(f"Non-pure-white bounding box: {bbox}")

# If we crop with a small margin or crop exactly to the outer colored border:
# Let's check with threshold:
import numpy as np
arr = np.array(img)
# pixels that differ significantly from white (e.g. any channel < 245)
mask = (arr[:, :, 0] < 248) | (arr[:, :, 1] < 248) | (arr[:, :, 2] < 248)
y_indices, x_indices = np.where(mask)
if len(y_indices) > 0 and len(x_indices) > 0:
    crop_box = (x_indices.min(), y_indices.min(), x_indices.max() + 1, y_indices.max() + 1)
    print(f"Tightly cropped bounding box: {crop_box}, size: {crop_box[2]-crop_box[0]}x{crop_box[3]-crop_box[1]}")
    
    cropped = img.crop(crop_box)
    
    # Let's make it a square by resizing to 1024x1024 so it fills the icon completely without any white outer border!
    square_icon = cropped.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    out_path = r"c:\Users\khalid\Downloads\تطبيق فلاتر\clean_icon.png"
    square_icon.save(out_path, "PNG")
    print(f"Saved cropped full-bleed icon to: {out_path}")
