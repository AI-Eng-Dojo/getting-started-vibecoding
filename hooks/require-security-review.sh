#!/bin/bash
# 外に出す直前に、セキュリティレビュー済みの印があるかを確認する。
# 無ければ、そのコマンドの実行を止めて理由を返す。
#
# Claude Code は PreToolUse フックの標準入力に、これから実行しようとしている
# ツールの内容を JSON で渡してくる。ここではその中の command を読む。

set -u

INPUT=$(cat)

# 実行されようとしているコマンド文字列を取り出す（jq が無い環境でも動くよう python3 を使う）
COMMAND=$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception:
    print("")
')

# 外に出すコマンドかどうか
case "$COMMAND" in
  *"git push"*|*"wrangler deploy"*) ;;
  *) exit 0 ;;   # それ以外は何もしない
esac

# 印があれば通す
if [ -f ".claude/security-reviewed" ]; then
  exit 0
fi

# 印が無ければ止める。
# 終了コード 2 は「このツール実行をブロックし、標準エラーの内容をClaudeに返す」の意味。
cat >&2 <<'MSG'
外に出す前のセキュリティレビューが済んでいません。

直前にコードを変更したため、レビュー済みの印（.claude/security-reviewed）が消えています。
先に「セキュリティレビューして」を実行してください。レビューが通れば印が作り直され、
このコマンドは通るようになります。
MSG
exit 2
