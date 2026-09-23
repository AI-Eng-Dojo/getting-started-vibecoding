# hooks/ の配布ファイル

後半9で実装前に設定するコミット前のレビューと、後半11で追加するデプロイ前の確認に使います。
スクリプトはNode.jsで動きます。
事前準備で `node -v` と `git --version` が通ることを確かめてください。

## 配布するもの

| ファイル | 役割 |
|---|---|
| [pre-commit-code-review.mjs](pre-commit-code-review.mjs) | Markdown以外のファイルが制御ファイルより新しければ、コミットを一度止めて `/code-review` を呼ぶよう伝える |
| [mark-code-reviewed.mjs](mark-code-reviewed.mjs) | 自分で `/code-review` または `/review` と打ったときに、制御ファイルの日時を更新する |
| [security-review-prompt.md](security-review-prompt.md) | コミット前のセキュリティレビューで見る範囲、観点、重大度を指定する |
| [settings.review.json](settings.review.json) | 後半9で追加するフックの設定 |
| [pre-deploy-check.mjs](pre-deploy-check.mjs) | Gitにコミットしていない変更があれば、デプロイを止める |
| [settings.deploy.json](settings.deploy.json) | 後半11で追加するデプロイ用フックの設定だけを収録する |

Hooksは、登録したイベントをきっかけに処理を実行します。
この例では、コードレビューを促すスクリプトと、セキュリティレビューを実行するエージェントフックを、コミット前に並行して動かします。
Hooksは自分のアカウントの権限で動くため、登録する内容と用途を確かめてから使ってください。

## 後半9で実装前に設定する

コピー先は、参加者が作る `myapp` の `.claude/hooks/` です。
この教材リポジトリの `.claude/` に登録するものではありません。

1. `pre-commit-code-review.mjs`、`mark-code-reviewed.mjs`、`security-review-prompt.md` を `myapp/.claude/hooks/` にコピーする。
2. `settings.review.json` の `hooks` の項目を、`myapp/.claude/settings.json` に追加する。
   既存の設定と、前半で作ったログ用Hookを残す。
   同じイベントの配列があれば、その配列に項目を追加し、同じ設定を二重に登録しない。
3. `myapp/.gitignore` に `.claude/code-reviewed` を追加する。
4. Claude Codeで `/hooks` を開き、この教材分として `PreToolUse` に4件、`UserPromptExpansion` に1件追加されたことを確かめる。
   反映されていなければ、Claude Codeを開き直して確認する。

`settings.review.json` は、既存の `.claude/settings.json` 全体に上書きするファイルではありません。
Claude Codeに設定を頼むときも、既存の内容を読ませてから追加させます。

```text
配布された hooks/ の pre-commit-code-review.mjs、mark-code-reviewed.mjs、
security-review-prompt.md を、この myapp の .claude/hooks/ にコピーしてください。
hooks/settings.review.json の設定を、既存の .claude/settings.json に追加してください。
既存の設定とログ用Hookを残し、同じ設定を二重に登録しないでください。
.gitignore に .claude/code-reviewed を追加してください。
追加した内容を説明してください。まだコミットしないでください。
```

Claude Codeに同梱されたエージェントスキル `/code-review` を使います。
`myapp/.claude/skills/` や `~/.claude/skills/` に同名のエージェントスキルがあると、同梱のものに代わって使われます。
以前の教材からコピーした `code-review` がある場合は、内容と保存先を確認して、同梱のものを使えるように整理してください。

## 以前の教材から移行する場合

旧教材の `clear-security-reviewed.sh` と `require-security-review.sh` を呼ぶフックが残っていると、新しい手順でレビューしても、旧制御ファイルを要求してプッシュが止まります。
新しいフックを登録して動作確認したあと、`.claude/settings.json` を読み、**この二つのスクリプトを呼ぶ旧フックの項目だけ**を取り除いてください。
前半の編集ログや、自分で設定したほかのフックは残します。
`/hooks` で旧項目が消え、新しい項目が残っていることを確認します。
古いエージェントスキル `code-review` と `security-review` の退避は、[配布物の使い方](../skills/README.md)を参照してください。

編集ログ `.claude/edit-log.txt` もGitの除外対象にします。
すでに追跡している場合は、手元のログを残したまま `git rm --cached .claude/edit-log.txt` で追跡を外し、その変更もコミットします。
レビュー開始時点の制御ファイルと編集ログが、デプロイ前の変更確認に混ざるのを防ぐためです。

## コードレビューを促す仕組みの範囲

`.claude/code-reviewed` は、**レビューを始める時点の制御ファイル**です。
コミットを一度止めたときと、自分で `/code-review` または `/review` と打ったときに更新します。
レビュー結果が届いたことや、指摘を直したことは記録していません。
結果が届く前でも、変更せずに同じコミットを再試行すれば、コードレビューの確認は通ります。
レビュー開始と結果の報告を自分で確認してください。

| 条件 | この例の動き |
|---|---|
| 制御ファイルより新しい、Markdown以外のファイルがある | コミットを一度止め、`/code-review` を呼ぶようClaudeに伝える |
| エディタやシェルでファイルを書き換えた | 次の対象コミットで更新日時を比べるため、判定に入る |
| Markdownだけを変更した、またはファイルを削除しただけ | コードレビューの確認では止めない。削除は更新日時を読めないため対象外 |
| 未追跡のファイルがある | Gitの除外対象でなく、Markdown以外なら判定に入る |
| セキュリティレビューにCriticalかHighの指摘がある | エージェントフックがコミットを止める。再試行でもレビューする |
| セキュリティレビューにMediumかLowの指摘だけがある | エージェントフックは通す。この結果だけでは指摘は報告されない |

コードレビューの確認はGitの差分ではなく更新日時を見ます。
タイムスタンプを維持したコピーなどは検知できない場合があり、レビュー完了の保証には使えません。
セキュリティレビューはMarkdownや削除を含む `git diff HEAD` と、除外対象ではない未追跡ファイルを見ます。

設定はClaude CodeのBashまたはPowerShellで実行する、`git commit *` に合うコマンドが対象です。
自分のターミナルでのコミット、別のツール、条件に合わないコマンドは対象になりません。
フックが必ず行うのは、登録条件に合ったときにスクリプトやエージェントを実行するところまでです。
コードレビューを始める指示を受けて `/code-review` を呼ぶのはClaudeなので、開始されなければ自分で実行します。

エージェントフックは実験的な機能です。
動かなければ `/hooks` と表示されたエラーを確認し、[公式リファレンスのAgent-based hooks](https://code.claude.com/docs/en/hooks#agent-based-hooks)で現在の対応を確かめます。
利用できない環境では、コミットをいったん保留し、別のサブエージェントに `security-review-prompt.md` を読ませて手動でレビューします。
CriticalとHighへの対応を確認してから、コミットを頼み直してください。
この場合、セキュリティレビューの自動実行は確認できていないものとして扱います。

## 後半11でデプロイ前の確認を追加する

1. `pre-deploy-check.mjs` を `myapp/.claude/hooks/` にコピーする。
2. `settings.deploy.json` の `PreToolUse` の項目を、既存の `.claude/settings.json` に追加する。
   コミット前のレビューとログ用Hookを残す。
3. `/hooks` を開き、デプロイ用が2件追加されたことを確かめる。
4. 設定を含む変更をレビューしてコミットしてから、デプロイを頼む。

```text
配布された hooks/pre-deploy-check.mjs を、この myapp の .claude/hooks/ にコピーしてください。
hooks/settings.deploy.json の設定を、既存の .claude/settings.json に追加してください。
コミット前のレビューとログ用Hookを残し、同じ設定を二重に登録しないでください。
追加した内容を説明してください。まだデプロイしないでください。
```

デプロイ前の確認は、`git status --porcelain` に変更が出れば終了コード2で止めます。
ステージ済みの変更、未ステージの変更、除外対象ではない未追跡ファイルが対象です。
Gitの状態を取得できないときも止めます。
このフックはレビューをせず、コミット済みかどうかだけを確かめます。
Gitの除外対象ファイルは判定に入らないので、公開先が `public/` になっているか、秘密情報が公開対象に入っていないかも確認してください。

対象は、Claude CodeのBashまたはPowerShellで実行する `npx wrangler deploy *` に合うコマンドです。
`npm run deploy` のような別の書き方、自分のターミナルからの実行、Cloudflareの画面からの公開では動きません。

## 配布ファイルのローカル検証

教材のルートで次を実行します。
Node.js標準のテスト機能を使うため、追加パッケージは不要です。
テストは一時ディレクトリのGitリポジトリだけを操作し、実際のコミット、プッシュ、デプロイ用コマンドを参加者のプロジェクトで実行しません。

```bash
node --test hooks/hooks.test.mjs
```

コードレビューの一時停止と再試行、更新日時の比較、Markdownと削除の除外、デプロイ時の変更検知、Gitの実行失敗を確認します。
Claude Codeでの登録、`/code-review` の起動、エージェントフックの実行はこのテストの対象外です。
参加者は[後半の教材](../docs/02-part2.md)に沿って、登録後の動きも確かめてください。

設定の `matcher`、`if`、`args`、`UserPromptExpansion` は[公式Hooksリファレンス](https://code.claude.com/docs/en/hooks)を参照しています（2026年9月24日確認）。
`command: "node"` と `args` の組み合わせはシェルを介さずに実行されるため、スクリプトのパスに空白があっても一つの引数として扱われます。
