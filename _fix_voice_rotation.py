"""voice-1〜3のEXIF回転情報を反映して保存し直す"""
import os
from PIL import Image, ImageOps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SCRIPT_DIR, "images", "_originals")
DST = os.path.join(SCRIPT_DIR, "images")

for fname in ["voice-1.jpeg", "voice-2.jpeg", "voice-3.jpeg"]:
    img = Image.open(os.path.join(SRC, fname))
    img = ImageOps.exif_transpose(img)
    if max(img.size) > 1600:
        img.thumbnail((1600, 1600), Image.LANCZOS)
    if img.mode != "RGB":
        img = img.convert("RGB")
    out = os.path.join(DST, fname)
    img.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"{fname}: -> {img.size} ({os.path.getsize(out)//1024}KB)")
