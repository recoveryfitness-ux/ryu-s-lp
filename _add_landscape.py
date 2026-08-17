"""新しい横画像を加工してLP imagesに配置・HTMLを更新"""
import os, shutil
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "参考資料", "素材写真"))
IMG_DIR = os.path.join(SCRIPT_DIR, "images")
HTML = os.path.join(SCRIPT_DIR, "index.html")
BACKUP = os.path.join(IMG_DIR, "_originals")
os.makedirs(BACKUP, exist_ok=True)

MAX_DIM = 1600
JPEG_Q = 82

# 入力ファイル: 元ファイル名 -> 出力ファイル名
files = {
    "代表・郡　横.png": "trainer-kori-wide.jpg",
    "カウンセリング　横.png": "counseling-wide.jpg",
}

for src_name, dst_name in files.items():
    src = os.path.join(SRC_DIR, src_name)
    if not os.path.exists(src):
        print(f"SKIP: {src_name} not found")
        continue
    bak = os.path.join(BACKUP, src_name)
    if not os.path.exists(bak):
        shutil.copy2(src, bak)
    img = Image.open(src)
    img.load()
    if max(img.size) > MAX_DIM:
        img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    dst = os.path.join(IMG_DIR, dst_name)
    img.save(dst, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    print(f"{src_name} -> {dst_name}: {os.path.getsize(dst)//1024}KB ({img.size[0]}x{img.size[1]})")
