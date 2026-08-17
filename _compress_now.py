"""
LP画像の一括最適化スクリプト。
- ヒーロー画像 (PNG): max幅1920px、JPEG q82 で変換
- その他大きい画像 (>180KB): max幅1600px、JPEG q82 で再エンコード
- _originals に元画像をバックアップ
"""
import os
import shutil
from pathlib import Path
from PIL import Image, ImageOps

IMG_DIR = Path(__file__).parent / "images"
BACKUP_DIR = IMG_DIR / "_originals_compress"
BACKUP_DIR.mkdir(exist_ok=True)

MAX_HERO_WIDTH = 1920
MAX_GENERAL_WIDTH = 1600
JPEG_QUALITY = 82
TARGET_THRESHOLD_BYTES = 180 * 1024  # 180KB以上のみ最適化

# 削除対象 (現在使用していないヒーロー画像)
UNUSED = ["lp-hero-recovery.png", "lp-hero-kaatsu.png", "lp-hero.jpg"]


def backup(src: Path):
    dst = BACKUP_DIR / src.name
    if not dst.exists():
        shutil.copy2(src, dst)


def is_hero(name: str) -> bool:
    return "lp-hero" in name.lower()


def optimize(path: Path):
    size_before = path.stat().st_size
    if size_before < TARGET_THRESHOLD_BYTES and not is_hero(path.name):
        return None

    backup(path)
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)  # EXIF回転を維持

        max_w = MAX_HERO_WIDTH if is_hero(path.name) else MAX_GENERAL_WIDTH
        if img.width > max_w:
            ratio = max_w / img.width
            new_size = (max_w, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # JPEGに変換 (RGBAなら白背景合成)
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 出力は .jpg に統一 (PNGも変換)
        out_path = path.with_suffix(".jpg")
        img.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        # 元のPNG/JPEGと拡張子が違ったら削除
        if out_path != path:
            path.unlink()
        size_after = out_path.stat().st_size
        return path.name, out_path.name, size_before, size_after
    except Exception as e:
        print(f"FAIL: {path.name} → {e}")
        return None


def main():
    print(f"Source dir: {IMG_DIR}")
    # 不要画像を削除
    for name in UNUSED:
        p = IMG_DIR / name
        if p.exists():
            backup(p)
            p.unlink()
            print(f"Deleted unused: {name}")

    results = []
    for p in sorted(IMG_DIR.iterdir()):
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png"):
            res = optimize(p)
            if res:
                results.append(res)

    print("\n=== Compression Results ===")
    total_before = 0
    total_after = 0
    for old, new, b, a in results:
        total_before += b
        total_after += a
        rename_note = f" → {new}" if old != new else ""
        print(f"{old}{rename_note}: {b/1024:7.1f}KB → {a/1024:7.1f}KB ({a/b*100:.1f}%)")
    if total_before:
        print(f"\nTOTAL: {total_before/1024/1024:.2f}MB → {total_after/1024/1024:.2f}MB ({total_after/total_before*100:.1f}%)")


if __name__ == "__main__":
    main()
