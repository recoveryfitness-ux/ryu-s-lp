"""LP画像の一括リサイズ＋圧縮スクリプト。
- max 1600px に縮小
- アルファなしPNGはJPEG化（元PNGは削除し、HTML参照も更新）
- JPEGは quality 82・progressive 再エンコード
"""
import os, shutil, sys
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(__file__), "images")
BACKUP = os.path.join(IMG_DIR, "_originals")
HTML = os.path.join(os.path.dirname(__file__), "index.html")
MAX_DIM = 1600
JPEG_Q = 82

os.makedirs(BACKUP, exist_ok=True)

renames = {}  # old -> new (for .png -> .jpg conversion)
report = []

for fname in sorted(os.listdir(IMG_DIR)):
    src = os.path.join(IMG_DIR, fname)
    if os.path.isdir(src):
        continue
    ext = fname.lower().rsplit(".", 1)[-1] if "." in fname else ""
    if ext not in ("png", "jpg", "jpeg"):
        continue

    bak = os.path.join(BACKUP, fname)
    if not os.path.exists(bak):
        shutil.copy2(src, bak)
    orig_size = os.path.getsize(bak)

    img = Image.open(src)
    img.load()

    # Resize
    if max(img.size) > MAX_DIM:
        img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)

    has_alpha = (
        img.mode in ("RGBA", "LA")
        or (img.mode == "P" and "transparency" in img.info)
    )

    if ext == "png" and not has_alpha:
        # PNG photo without alpha -> JPEG
        new_name = fname.rsplit(".", 1)[0] + ".jpg"
        new_path = os.path.join(IMG_DIR, new_name)
        img = img.convert("RGB")
        img.save(new_path, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
        if os.path.abspath(new_path) != os.path.abspath(src):
            os.remove(src)
            renames[fname] = new_name
        new_size = os.path.getsize(new_path)
        report.append((fname, new_name, orig_size, new_size))
    elif ext == "png" and has_alpha:
        # PNG with alpha -> keep but recompress
        img.save(src, "PNG", optimize=True)
        report.append((fname, fname, orig_size, os.path.getsize(src)))
    else:
        # JPEG -> recompress
        img = img.convert("RGB")
        img.save(src, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
        report.append((fname, fname, orig_size, os.path.getsize(src)))

# Update HTML references for renamed files
if renames and os.path.exists(HTML):
    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()
    for old, new in renames.items():
        html = html.replace(old, new)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)

# Print report
total_old = sum(r[2] for r in report)
total_new = sum(r[3] for r in report)
print(f"{'OLD':<40}{'NEW':<40}{'BEFORE':>10}{'AFTER':>10}{'SAVED':>8}")
print("-" * 108)
for old, new, o, n in report:
    saved = 100 * (1 - n / o) if o else 0
    print(f"{old:<40}{new:<40}{o//1024:>8}KB{n//1024:>8}KB{saved:>6.0f}%")
print("-" * 108)
print(
    f"{'TOTAL':<80}{total_old//1024:>8}KB{total_new//1024:>8}KB"
    f"{100*(1-total_new/total_old):>6.0f}%"
)
