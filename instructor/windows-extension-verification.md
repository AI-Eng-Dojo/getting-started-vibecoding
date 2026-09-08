# Windows版Claude Code拡張の起動検証（2026-09-08）

[Issue #30](https://github.com/AI-Eng-Dojo/getting-started-vibecoding/issues/30) の確認として、GitHub ActionsのWindows環境で外部Node.jsをPATHから除外し、Claude Code拡張を起動した。
[検証run 34193270746](https://github.com/AI-Eng-Dojo/getting-started-vibecoding/actions/runs/34193270746) は成功し、未ログイン画面の描画まで確認できた。

| 項目 | 検証結果 |
|---|---|
| 実行日 | 2026-09-08 |
| OS | Windows Server 2025（10.0.26100） |
| VS Code | 1.136.1 |
| Claude Code拡張 | 2.1.263（win32-x64） |
| 外部Node.jsの探索 | `where.exe node`、`where.exe npm`、`where.exe npx` はすべて終了コード1（PATHで見つからない） |
| 外部Node.jsの起動 | Windowsのプロセス生成記録で、VS Code自身を含むプロセスツリー107件中 `node.exe` は0件 |
| 拡張の有効化 | `activate()` 成功 |
| パネルの生成 | `claudeVSCodePanel` を生成し、スクリーンショットで認証方式を選ぶ未ログイン画面を確認 |
| 同梱CLIの起動 | `resources/native-binary/claude.exe --version` が終了コード0で `2.1.263 (Claude Code)` を出力 |
| パネルからのCLI起動 | 拡張ログでも、既定の設定で同梱 `claude.exe` を起動したことを確認 |

ランナーにはNode.jsのインストール自体は残っており、今回の検証では拡張を起動する環境のPATHから除外した。
VS Codeに埋め込まれたNode.jsランタイム（24.18.1）は使用している。
そのため、確認できたのは「外部のNode.jsをコマンドとして探索できず、外部 `node.exe` も起動しない状態で、検証した拡張が起動すること」である。

検証範囲は未ログイン画面までで、ログイン後のモデル応答は未検証である。
認証情報の入力や有料APIへのリクエストは行っていない。
物理PC上のWindows 10／11や、異なるVS Code／拡張バージョンの動作も未検証である。

[Claude Code公式のVS Code版要件](https://code.claude.com/docs/en/vs-code#prerequisites) は、VS Code 1.94.0以上と利用可能なアカウントを挙げ、拡張がチャットパネル用のCLIを同梱すると明記している（2026-09-08確認）。
この公式記述と今回の実行結果から、検証したWindows版拡張の起動に外部Node.jsが必須とは言えない。
講座では、後半の `npx wrangler` とBacklog連携に使うため、全OSでNode.jsを導入する案内を続ける。

実行証跡はrunの成果物 `windows-extension-startup-34193270746` に保存した。
`summary.json`、`extension-result.json`、`process-starts.json`、`sources.json`、`claude-code-panel.png` と拡張ログを含む。
同じ検証は[Windows拡張起動検証ワークフロー](../.github/workflows/windows-extension-check.yml) から再実行できる。
