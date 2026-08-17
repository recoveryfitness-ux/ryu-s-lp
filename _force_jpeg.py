"""残った大きなPNGを強制的にJPEG化（αが全opaqueなら無損失、αありなら白合成）"""
import os
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "images")
HTML = os.path.join(SCRIPT_DIR, "index.html")

THRESHOLD = 400 * 1024  # 400KB以上のPNGを対象
JPEG_Q = 82

renames = {}
report = []

for fname in sorted(os.listdir(IMG_DIR)):
    if not fname.lower().endswith(".png"):
        continue
    src = os.path.join(IMG_DIR, fname)
    if os.path.getsize(src) < THRESHOLD:
        continue

    img = Image.open(src)
    img.load()
    orig = os.path.getsize(src)

    # αチェック
    if img.mode in ("RGBA", "LA"):
        alpha = img.split()[-1]
        bbox = alpha.getbbox()
        # 透明部分があるかどうか
        extrema = alpha.getextrema()  # (min, max)
        if extrema[0] == 255:
            # 完全opaque → 透過なし、安全にRGB変換
            img = img.convert("RGB")
        else:
            # 透過あり → 白背景で合成
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
    elif img.mode == "P":
        img = img.convert("RGB")
    else:
        img = img.convert("RGB")

    new_name = fname.rsplit(".", 1)[0] + ".jpg"
    new_path = os.path.join(IMG_DIR, new_name)
    img.save(new_path, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    os.remove(src)
    renames[fname] = new_name
    new_size = os.path.getsize(new_path)
    report.append((fname, new_name, orig, new_size))

# HTML置換
if renames and os.path.exists(HTML):
    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()
    for old, new in renames.items():
        html = html.replace(old, new)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)

for old, new, o, n in report:
    saved = 100 * (1 - n / o) if o else 0
    print(f"{old} -> {new}: {o//1024}KB -> {n//1024}KB ({saved:.0f}%)")
total_o = sum(r[2] for r in report)
total_n = sum(r[3] for r in report)
if total_o:
    print(f"\nTOTAL: {total_o//1024}KB -> {total_n//1024}KB ({100*(1-total_n/total_o):.0f}%)")
