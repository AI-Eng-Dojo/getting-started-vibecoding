#!/bin/bash
# ファイルを編集・作成した直後に、セキュリティレビュー済みの印を消す。
# コードが変わったら、レビューはやり直し、という意味。
#
# ただし .claude/ の中のファイルを書いたときは消さない。
# security-review が印（.claude/security-reviewed）そのものを作った直後に
# このフックが動いて印を消してしまい、いつまでもプッシュできなくなるため。
#
# Claude Code は PostToolUse フックの標準入力に、いま実行したツールの内容を
# JSON で渡してくる。ここではその中の file_path を読む。

set -u

INPUT=$(cat)

# 書き込まれたファイルのパスを取り出す（jq が無い環境でも動くよう Python を使う）
# 名前が見つかっても動かないことがある（Windows の python3 は、ストアへ案内するだけの偽物のことがある）ので、
# 実際に動かして確かめ、最初に動いたものを使う
PY=
for c in python3 python py; do
  "$c" -c 'import json' >/dev/null 2>&1 && { PY=$c; break; }
done
FILE_PATH=$(printf '%s' "$INPUT" | "$PY" -c '
import sys, json
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))
except Exception:
    print("")
')

# .claude/ の中なら何もしない（Windows の \ 区切りも含める）
case "$FILE_PATH" in
  .claude/*|*/.claude/*|.claude\\*|*\\.claude\\*) exit 0 ;;
esac

# それ以外の書き込みなら、印を消す（無ければ何もしない）
rm -f .claude/security-reviewed
exit 0
