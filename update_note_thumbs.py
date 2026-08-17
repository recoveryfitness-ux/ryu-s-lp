"""
note サムネイル自動反映スクリプト
参考資料\note用サムネイル に画像を入れてこのスクリプトを実行するだけで
LP の images/note/ へのコピー・thumbMap の更新・git push まで自動で行う
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

# ---- パス設定 ----
SCRIPT_DIR   = Path(__file__).parent
SOURCE_DIR   = Path(r"C:\Users\PC\OneDrive\Desktop\AIクラウドコード\営業\参考資料\note用サムネイル")
DEST_DIR     = SCRIPT_DIR / "images" / "note"
INDEX_HTML   = SCRIPT_DIR / "index.html"

# 日付パターン（例: 2026年8月17日 16_57_06）
DATE_PATTERN = re.compile(r"\d{4}年\d+月\d+日[\s\d_]+$")
# タイトル区切り文字
SPLIT_CHARS  = ["｜", "——", "——", "—", "？｜", "！｜"]


def extract_keyword(filename: str) -> str:
    title = Path(filename).stem
    title = DATE_PATTERN.sub("", title).strip()
    for sep in SPLIT_CHARS:
        if sep in title:
            title = title.split(sep)[0].strip()
            break
    # 最初の 15 文字を keyword に（十分ユニーク）
    return title[:15].strip("「」『』【】　 ")


def get_existing_thumbmap(html: str) -> dict:
    """thumbMap から {keyword: file} の辞書を返す"""
    pattern = re.compile(r"\{\s*key:\s*'([^']+)'\s*,\s*file:\s*'(note-\d+\.png)'\s*\}")
    return {m.group(1): m.group(2) for m in pattern.finditer(html)}


def next_note_number(existing: dict) -> int:
    nums = [int(re.search(r"\d+", v).group()) for v in existing.values()]
    return max(nums) + 1 if nums else 1


def get_processed_sources(existing: dict, html: str) -> set:
    """すでに処理済みのファイル名を推定（keywordで逆引き）"""
    return set(existing.keys())


def update_thumbmap(html: str, new_entries: list) -> str:
    """thumbMap の末尾エントリの後ろに新エントリを挿入"""
    last = re.search(r"(\{ key: '[^']+',\s*file: 'note-\d+\.png' \})\s*\];", html)
    if not last:
        print("thumbMap の末尾が見つかりません")
        return html

    insert_text = ""
    for kw, fname in new_entries:
        insert_text += f"\n      {{ key: '{kw}', file: '{fname}' }},"

    new_html = html[:last.end(1)] + "," + insert_text + "\n    ];" + html[last.end():]
    return new_html


def git_push(message: str):
    cmds = [
        ["git", "add", "images/note/", "index.html"],
        ["git", "commit", "-m", message],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True)
        print(result.stdout.strip() or result.stderr.strip())


def main():
    print("=== note サムネイル自動反映 ===\n")

    html = INDEX_HTML.read_text(encoding="utf-8")
    existing = get_existing_thumbmap(html)
    existing_keywords = set(existing.keys())

    source_files = sorted(SOURCE_DIR.glob("*.png")) + sorted(SOURCE_DIR.glob("*.jpg"))
    if not source_files:
        print(f"対象画像が見つかりません: {SOURCE_DIR}")
        return

    new_entries = []
    num = next_note_number(existing)

    for src in source_files:
        keyword = extract_keyword(src.name)
        # すでに登録済みのキーワードと部分一致するものはスキップ
        if any(keyword[:8] in k or k[:8] in keyword for k in existing_keywords):
            print(f"スキップ（登録済み）: {src.name[:40]}...")
            continue

        ext = src.suffix.lower()
        dest_name = f"note-{num:02d}.png"
        dest_path = DEST_DIR / dest_name

        shutil.copy2(src, dest_path)
        print(f"コピー: {src.name[:40]}...")
        print(f"  → {dest_name}  keyword: 「{keyword}」")

        new_entries.append((keyword, dest_name))
        existing_keywords.add(keyword)
        num += 1

    if not new_entries:
        print("\n新しいサムネイルはありません。")
        return

    html = update_thumbmap(html, new_entries)
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"\nthumbMap に {len(new_entries)} 件追加しました")

    labels = "・".join(kw for kw, _ in new_entries)
    git_push(f"note: サムネイル自動追加（{labels}）")
    print("\n✅ 完了 — Netlify が自動デプロイします（1〜2分）")


if __name__ == "__main__":
    main()
