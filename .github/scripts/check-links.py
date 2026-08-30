#!/usr/bin/env python3
"""教材のMarkdownが参照しているリポジトリ内ファイルの実在を確認する。

当日まで誰も踏まない参照（救済版・テンプレート・スキルの完成例）が
静かに壊れているのを検出するのが目的。
"""
import os
import re
import sys

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "#")

# 教材が参加者に配る raw URL。指すファイルが main から消えると、
# 当日「URLの中身を保存して」が404で失敗する。ローカルの実ファイルと突き合わせる。
RAW_SELF = re.compile(
    r"https://raw\.githubusercontent\.com/AI-Eng-Dojo/getting-started-vibecoding/main/([^\s)`\"']+)"
)


def targets(root="."):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", ".github"}]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


FENCE = re.compile(r"^\s*(```|~~~)")


def main():
    broken = []
    checked = 0
    for src in sorted(targets()):
        in_fence = False
        with open(src, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                # コードブロックの中は「書き方の例」であって参照ではない
                if FENCE.match(line):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for raw in LINK.findall(line):
                    if raw.startswith(SKIP_PREFIX):
                        continue
                    path = raw.split("#", 1)[0]
                    if not path:
                        continue
                    resolved = os.path.normpath(os.path.join(os.path.dirname(src), path))
                    checked += 1
                    if not os.path.exists(resolved):
                        broken.append((src, lineno, raw, resolved))

    # 教材が配る raw URL の指す先が、リポジトリに実在するか
    raw_checked = 0
    for src in sorted(targets()):
        with open(src, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for path in RAW_SELF.findall(line):
                    # ⟨ ⟩ は参加者が置き換えるプレースホルダ。実在しなくて当然
                    if "⟨" in path or "⟩" in path:
                        continue
                    raw_checked += 1
                    if not os.path.exists(path):
                        broken.append((src, lineno, "raw URL: " + path, path))

    for src, lineno, raw, resolved in broken:
        print(f"::error file={src},line={lineno}::参照先が存在しません: {raw} -> {resolved}")

    print(f"確認したリポジトリ内リンク: {checked} 件 / 配布用 raw URL: {raw_checked} 件 "
          f"/ 壊れているもの: {len(broken)} 件")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
