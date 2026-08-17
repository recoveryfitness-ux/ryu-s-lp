"""
ファビコン一括生成スクリプト。
ロゴ画像から以下のファイルを生成する:
  - favicon.ico (16, 32, 48 multi-size)
  - favicon-16x16.png
  - favicon-32x32.png
  - apple-touch-icon.png (180x180)
  - android-chrome-192x192.png
  - android-chrome-512x512.png
"""
from pathlib import Path
from PIL import Image, ImageOps

LP_DIR = Path(__file__).parent
SOURCE = Path(r"C:\Users\PC\OneDrive\Desktop\AIクラウドコード\営業\参考資料\ロゴ\Rのみ　小サイズ.jpg")
OUT_DIR = LP_DIR  # ルートに置く

SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "apple-touch-icon.png": 180,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
}


def crop_to_square(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def main():
    print(f"Source: {SOURCE}")
    img = Image.open(SOURCE)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = crop_to_square(img)
    print(f"Cropped to square: {img.size}")

    # 各サイズ生成
    for name, size in SIZES.items():
        resized = img.resize((size, size), Image.LANCZOS)
        out = OUT_DIR / name
        resized.save(out, "PNG", optimize=True)
        print(f"  Generated: {name} ({size}x{size}) {out.stat().st_size/1024:.1f}KB")

    # favicon.ico (multi-size)
    ico_path = OUT_DIR / "favicon.ico"
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    base = img.resize((48, 48), Image.LANCZOS)
    base.save(ico_path, format="ICO", sizes=ico_sizes)
    print(f"  Generated: favicon.ico ({ico_sizes}) {ico_path.stat().st_size/1024:.1f}KB")


if __name__ == "__main__":
    main()
