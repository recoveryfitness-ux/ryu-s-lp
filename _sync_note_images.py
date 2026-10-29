"""
note サムネイル自動同期スクリプト
使い方: python _sync_note_images.py
  1. note用サムネイルフォルダの画像をRSS記事と照合
  2. 新しい画像を images/note/ にコピー
  3. index.html の thumbMap を自動更新
  4. git commit & push
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

THUMB_DIR = Path(r"C:\Users\PC\OneDrive\Desktop\AIクラウドコード\営業\参考資料\note用サムネイル")
LP_DIR    = Path(__file__).parent
NOTE_IMG_DIR = LP_DIR / "images" / "note"
INDEX_HTML   = LP_DIR / "index.html"
RSS_URL      = "https://note.com/kori_ryuji_ryus/rss"


# ── RSS取得 ──────────────────────────────
def fetch_articles():
    with urllib.request.urlopen(RSS_URL, timeout=15) as r:
        tree = ET.parse(r)
    items = []
    for item in tree.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link")  or "").strip()
        items.append({"title": title, "link": link})
    return items


# ── タイトル類似度（共通文字数 / 短い方の長さ）────────────────
def similarity(a: str, b: str) -> float:
    a, b = a.lower(), b.lower()
    common = sum(1 for c in set(a) if c in b)
    return common / max(len(set(a)), 1)


def best_match(filename: str, articles: list) -> dict | None:
    stem = Path(filename).stem
    # 日付・時刻部分を除去
    stem_clean = re.sub(r"(\d{4}年\d{1,2}月\d{1,2}日.*|ChatGPT Image.*)", "", stem).strip()
    if not stem_clean:
        return None
    best, best_score = None, 0.3  # 最低閾値
    for art in articles:
        score = similarity(stem_clean, art["title"])
        if score > best_score:
            best, best_score = art, score
    return best


# ── 現在の thumbMap を index.html から読み込む ──────────────
def load_thumb_map(html: str) -> list[dict]:
    pattern = r"\{\s*key:\s*'([^']+)'\s*,\s*file:\s*'([^']+)'\s*\}"
    return [{"key": m[0], "file": m[1]} for m in re.findall(pattern, html)]


# ── 最小識別キーワードを生成 ─────────────────────────────────
def make_key(title: str, existing_keys: list[str]) -> str:
    words = [w for w in re.split(r"[｜——\-\s・「」『』【】（）\[\]]", title) if len(w) >= 4]
    for w in sorted(words, key=len, reverse=True):
        if not any(w in k or k in w for k in existing_keys):
            return w[:20]
    return title[:15]


# ── メイン ────────────────────────────────────────────────
def main():
    articles = fetch_articles()
    print(f"RSS: {len(articles)} 記事取得")

    html = INDEX_HTML.read_text(encoding="utf-8")
    thumb_map = load_thumb_map(html)
    existing_files = {e["file"] for e in thumb_map}
    existing_keys  = [e["key"]  for e in thumb_map]

    # 次の連番
    nums = [int(re.search(r"\d+", e["file"]).group()) for e in thumb_map if re.search(r"\d+", e["file"])]
    next_num = max(nums, default=0) + 1

    new_entries = []
    for img_path in sorted(THUMB_DIR.glob("*.png")):
        article = best_match(img_path.name, articles)
        if not article:
            print(f"  スキップ（記事未照合）: {img_path.name[:40]}")
            continue

        # 既存エントリにマッチするか確認
        matched_key = next((e["key"] for e in thumb_map if e["key"] in article["title"]), None)
        if matched_key:
            # 既存エントリ — 画像ファイルだけ最新に上書き
            matched_file = next(e["file"] for e in thumb_map if e["key"] == matched_key)
            dest = NOTE_IMG_DIR / matched_file
            shutil.copy2(img_path, dest)
            print(f"  更新: {matched_file} ← {img_path.name[:50]}")
            continue

        # 新規エントリ
        new_file = f"note-{next_num:02d}.png"
        while new_file in existing_files:
            next_num += 1
            new_file = f"note-{next_num:02d}.png"

        dest = NOTE_IMG_DIR / new_file
        shutil.copy2(img_path, dest)

        key = make_key(article["title"], existing_keys)
        new_entries.append({"key": key, "file": new_file, "title": article["title"]})
        existing_files.add(new_file)
        existing_keys.append(key)
        print(f"  追加: {new_file} key='{key}' ← {img_path.name[:40]}")
        next_num += 1

    if not new_entries:
        print("新しい画像はありません。")
    else:
        # thumbMap に追記（最後のエントリにカンマがなければ補完）
        import re as _re
        html = _re.sub(r'(\}\s*)\n(\s*\];)', r'\1,\n\2', html, count=1)
        insert_js = "\n".join(
            f"      {{ key: '{e['key']}', file: '{e['file']}' }},"
            for e in new_entries
        )
        old_map_end = "    ];"  # thumbMap 末尾
        html = html.replace(
            old_map_end,
            insert_js + "\n" + old_map_end,
            1
        )
        INDEX_HTML.write_text(html, encoding="utf-8")
        print(f"\nindex.html を更新しました（{len(new_entries)} 件追加）")

    # git commit & push
    repo = str(LP_DIR)
    subprocess.run(["git", "-C", repo, "add", "images/note/", "index.html"], check=True)
    result = subprocess.run(["git", "-C", repo, "status", "--short"], capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run(["git", "-C", repo, "commit", "-m", "note: update thumbnails and thumbMap"], check=True)
        subprocess.run(["git", "-C", repo, "push"], check=True)
        print("\nGitHubにpush完了 → Netlifyが自動デプロイ開始")
    else:
        print("\n変更なし — pushをスキップ")


if __name__ == "__main__":
    main()
