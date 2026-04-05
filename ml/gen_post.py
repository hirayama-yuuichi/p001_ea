#!/usr/bin/env python3
"""
X投稿文生成スクリプト
docs/results/ の当日作業記録をもとに投稿候補を生成し、選択してクリップボードへコピーする
"""

import os
import sys
import glob
import re
import subprocess
from datetime import date

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../docs/results")
HASHTAGS = "#FX自動売買開発 #Claude #p001ea"
TODAY = date.today().strftime("%Y-%m-%d")


def load_today_results() -> tuple[str, list[str], str, str]:
    """当日の作業記録を読み込み、タイトル・やったこと・結果・次のアクションを抽出"""
    pattern = os.path.join(RESULTS_DIR, f"{TODAY}_*.md")
    files = glob.glob(pattern)
    if not files:
        all_files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.md")))
        if not all_files:
            print("作業記録が見つかりません。docs/results/ を確認してください。")
            sys.exit(1)
        files = [all_files[-1]]
        print(f"当日の記録なし。最新ファイルを使用: {os.path.basename(files[0])}")

    titles, todos, results, nexts = [], [], [], []

    for f in files:
        with open(f, encoding="utf-8") as fp:
            content = fp.read()

        # タイトル（# の行）
        m = re.search(r"^# (.+)", content, re.MULTILINE)
        if m:
            titles.append(m.group(1).strip())

        # やったこと
        m = re.search(r"## やったこと\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if m:
            items = [l.lstrip("- ").strip() for l in m.group(1).strip().splitlines() if l.strip()]
            todos.extend(items[:3])  # 最大3件

        # 結果
        m = re.search(r"## 結果\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if m:
            items = [l.lstrip("- ").strip() for l in m.group(1).strip().splitlines() if l.strip()]
            results.extend(items[:2])

        # 次のアクション
        m = re.search(r"## 次のアクション\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if m:
            items = [l.lstrip("- ").strip() for l in m.group(1).strip().splitlines() if l.strip()]
            nexts.extend(items[:2])

    return titles, todos, results, nexts


def generate_posts(titles, todos, results, nexts) -> list[str]:
    """3パターンの投稿文を生成"""
    title_str = " / ".join(titles) if titles else "開発作業"
    todo_str = "\n".join(f"・{t}" for t in todos) if todos else "・環境整備"
    result_str = results[0] if results else ""
    next_str = nexts[0] if nexts else ""

    posts = []

    # パターン1: 技術寄り
    p1 = f"【開発日記 {TODAY}】\n{todo_str}"
    if result_str:
        p1 += f"\n\n{result_str}"
    p1 += f"\n\n{HASHTAGS}"
    posts.append(p1)

    # パターン2: 感想寄り
    p2 = f"【開発日記 {TODAY}】\n今日は{title_str}をやった。"
    if result_str:
        p2 += f"\n{result_str}"
    if next_str:
        p2 += f"\n次は{next_str}"
    p2 += f"\n\n{HASHTAGS}"
    posts.append(p2)

    # パターン3: 短くさっぱり
    p3 = f"【開発日記 {TODAY}】\n{todos[0] if todos else title_str}"
    if next_str:
        p3 += f"→ 次: {next_str}"
    p3 += f"\n{HASHTAGS}"
    posts.append(p3)

    return posts


def copy_to_clipboard(text: str) -> bool:
    for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["wl-copy"]]:
        try:
            subprocess.run(cmd, input=text.encode(), check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return False


def main():
    print(f"=== X投稿文生成 {TODAY} ===\n")

    titles, todos, results, nexts = load_today_results()
    posts = generate_posts(titles, todos, results, nexts)

    for i, post in enumerate(posts, 1):
        print(f"【{i}】({len(post)}文字)")
        print(post)
        print()

    while True:
        choice = input(f"番号を選択 (1-{len(posts)}) / q=終了: ").strip()
        if choice.lower() == "q":
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(posts):
            selected = posts[int(choice) - 1]
            break
        print("正しい番号を入力してください。")

    print()
    if copy_to_clipboard(selected):
        print("クリップボードにコピーしました。Xに貼り付けて投稿してください。")
    else:
        print("以下をコピーしてください:\n")
        print(selected)


if __name__ == "__main__":
    main()
