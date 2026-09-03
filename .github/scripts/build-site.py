#!/usr/bin/env python3
"""教材リポジトリを GitHub Pages 用のHTMLサイトにビルドする。

やっていることは2つだけ。

1. 参加者に見せるMarkdown（README.md と docs/ skills/ starters/ templates/
   hooks/ demos/）を、**ディレクトリ構造をそのまま保って** .site-src/ にコピーする。
   構造を保つのは、教材内の相対リンク（`../starters/README.md` など）を
   1行も書き換えずに、GitHub上でもPages上でも同じように動かすため。
2. `mkdocs build` を呼ぶ。

instructor/ は「参加者には配布しない」と書かれているのでサイトには載せない
（リポジトリ上には残る。載せたくなったら INCLUDE に足すだけ）。

使い方:
    python3 .github/scripts/build-site.py           # site/ にビルド
    python3 .github/scripts/build-site.py --serve   # ローカルプレビュー
    python3 .github/scripts/build-site.py --stage-only
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = os.path.join(ROOT, ".site-src")

# サイトに載せるもの。ファイルでもディレクトリでもよい
INCLUDE = [
    "README.md",
    "docs",
    "skills",
    "starters",
    "templates",
    "hooks",
    "demos",
]

# コピーしないもの（どのディレクトリでも）
EXCLUDE_NAMES = {".DS_Store", "__pycache__", ".git"}

FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

# [starters/](../starters/) のような「ディレクトリ宛」のリンク
DIR_LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)\s]*/)\)")


def fix_directory_links(text, src):
    """ディレクトリ宛リンクを、そのディレクトリの README.md 宛に書き換える。

    GitHub上では `../starters/` はディレクトリ一覧に着地して機能するが、
    サイト側はページが `/docs/01-part1/` という1段深いURLになるため、
    同じ相対パスだと `/docs/starters/` にずれて404になる。
    ステージング側だけで README.md を明示しておけば、mkdocs が
    正しいURLに解決してくれる（元のMarkdownは触らない）。
    """
    def repl(m):
        target = m.group(1)
        d = os.path.normpath(os.path.join(os.path.dirname(src), target))
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "README.md")):
            return "](" + target + "README.md)"
        return m.group(0)

    return DIR_LINK.sub(repl, text)


def surface_front_matter(text):
    """SKILL.md のフロントマターを本文にも見える形で残す。

    mkdocs はフロントマターをメタデータとして食べてしまうため、そのままだと
    サイト上から `name` と `description` が消える。この教材は
    「description がスキルの起動条件になる」ことを教えるものなので、
    完成例からそこが消えるのは教材として成立しない。
    フロントマター自体は残したまま、最初のH1の直後に表示用のブロックを挿す。
    """
    m = FRONT_MATTER.match(text)
    if not m:
        return text
    block = (
        "\n"
        "!!! note \"このスキルのフロントマター（`SKILL.md` の冒頭）\"\n"
        "\n"
        "    Claudeは `description` を読んで、このスキルを自分で呼ぶかどうかを判断します。\n"
        "\n"
        "    ```yaml\n"
        + "".join("    " + line + "\n" for line in m.group(1).splitlines())
        + "    ```\n"
    )
    body = text[m.end():]
    # 最初のH1の直後に差し込む。H1が無ければ本文の先頭に置く
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, block)
            break
    else:
        lines.insert(0, block)
    return text[: m.end()] + "\n".join(lines)


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if src.endswith(".md"):
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(fix_directory_links(surface_front_matter(text), src))
    else:
        shutil.copy2(src, dst)


def stage():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)

    count = 0
    for item in INCLUDE:
        src = os.path.join(ROOT, item)
        if not os.path.exists(src):
            sys.exit(f"ビルド対象が見つかりません: {item}")
        if os.path.isfile(src):
            copy_file(src, os.path.join(STAGE, item))
            count += 1
            continue
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_NAMES]
            for name in filenames:
                if name in EXCLUDE_NAMES:
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT)
                copy_file(full, os.path.join(STAGE, rel))
                count += 1
    print(f".site-src/ に {count} ファイルを配置しました")


def main():
    args = sys.argv[1:]
    stage()
    if "--stage-only" in args:
        return 0
    cmd = ["mkdocs", "serve"] if "--serve" in args else ["mkdocs", "build", "--strict"]
    print("$ " + " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
