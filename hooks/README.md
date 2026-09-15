# hooks/ — 後半10④でコピーして使うHookスクリプト

後半10④（`docs/02-part2.md`）で設定する **Hook A**（編集した直後に印を消す）と **Hook B**（外に出す直前に止める）の中身です。自分で書かず、コピーして使ってください。`skills/` の後半4枚と同じ扱いです。

## なぜコピーで済ませるのか

Hooksは権限プロンプトを経由せず自動実行されます（前半5）。だから原則は「中身を理解できるものだけを登録する」です。

一方この講座の参加者は半数がノンテク層で、シェルスクリプトを読める前提がありません。**その場でAIに書かせたスクリプトを、書いた本人（同じAI）の説明だけを頼りに登録するのは、この原則を満たしていません。**

学んでほしいのはシェルスクリプトの書き方ではなく、エージェントスキルとHooksの違いです。だから中身は検証済みのものを配り、参加者は「仕組みが止める瞬間」を見ることに集中します。

## 中身

| ファイル | 何をするか |
|---|---|
| [clear-security-reviewed.sh](clear-security-reviewed.sh) | **Hook A。** ファイルが編集・作成された直後に、`.claude/security-reviewed` を消す。ただし書き込まれたのが `.claude/` の中のファイルなら何もしない |
| [require-security-review.sh](require-security-review.sh) | **Hook B。** これから実行されるコマンドに `git push` か `wrangler deploy` が含まれていて、かつ `.claude/security-reviewed` が無ければ、そのコマンドを止めて理由を返す |

どちらも40行前後です。日本語のコメント付きなので、読める人は読んでください。読めなくても、動きは後半10④で自分の目で確認します。

どちらも、Claude Codeから渡される内容を読むのにPython（`python3`・`python`・`py` のうち動くもの）を使います。**Pythonが入っていないPCでは、Hook Aは書き込みのたびに完了チェックを消し、Hook Bは何も止めません。**

> **Hook Aが `.claude/` の中を除外している理由。** `security-review` はレビューの最後に印（`.claude/security-reviewed`）を作ります。除外しないと、印を作ったこと自体にHook Aが反応して、作った直後の印を消してしまいます。2026-09-14の後半で実際に起きた不具合です。

## 動きの確認

Hookとして登録する前に、手元で直接動かして確かめられます。

```bash
# 印が無い状態で push しようとする → 終了コード 2（止まる）
echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' | ./hooks/require-security-review.sh
echo "終了コード: $?"

# 関係ないコマンドは素通りする → 終了コード 0
echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | ./hooks/require-security-review.sh
echo "終了コード: $?"
```

`.claude/security-reviewed` があれば、`git push` でも終了コード 0 になります。

Hook Aは、印が消えるかどうかで確かめます。このリポジトリに印を残さないよう、使い捨てのフォルダの中で試します。

```bash
HOOK_A="$PWD/hooks/clear-security-reviewed.sh"
cd "$(mktemp -d)"

# 印を置いてから、アプリのファイルを書いたことにする → 印が消える
mkdir -p .claude && touch .claude/security-reviewed
echo '{"tool_name":"Write","tool_input":{"file_path":"index.html"}}' | "$HOOK_A"
ls .claude/security-reviewed   # 「No such file」と出れば消えている

# 印を置いてから、印そのものを書いたことにする → 印は残る
touch .claude/security-reviewed
echo '{"tool_name":"Write","tool_input":{"file_path":".claude/security-reviewed"}}' | "$HOOK_A"
ls .claude/security-reviewed   # ファイル名が表示されれば残っている
```

> **終了コード 2 は「このツール実行をブロックし、標準エラーの内容をClaudeに返す」**という意味です。Claude Codeがそう決めています。
