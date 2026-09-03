# hooks/ — 後半10④でコピーして使うHookスクリプト

後半10④（`docs/02-part2.md`）で設定する **Hook B**（外に出す直前に止める）の判定部分です。自分で書かず、コピーして使ってください。`skills/` の後半4枚と同じ扱いです。

## なぜコピーで済ませるのか

Hooksは権限プロンプトを経由せず自動実行されます（前半5）。だから原則は「中身を理解できるものだけを登録する」です。

一方この講座の参加者は半数がノンテク層で、シェルスクリプトを読める前提がありません。**その場でAIに書かせたスクリプトを、書いた本人（同じAI）の説明だけを頼りに登録するのは、この原則を満たしていません。**

学んでほしいのはシェルスクリプトの書き方ではなく、SkillとHooksの違いです。だから中身は検証済みのものを配り、参加者は「仕組みが止める瞬間」を見ることに集中します。

## 中身

| ファイル | 何をするか |
|---|---|
| [require-security-review.sh](require-security-review.sh) | これから実行されるコマンドに `git push` か `wrangler deploy` が含まれていて、かつ `.claude/security-reviewed` が無ければ、そのコマンドを止めて理由を返す |

40行ほどです。日本語のコメント付きなので、読める人は読んでください。読めなくても、動きは後半10④で自分の目で確認します。

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

> **終了コード 2 は「このツール実行をブロックし、標準エラーの内容をClaudeに返す」**という意味です。Claude Codeがそう決めています。
