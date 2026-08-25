# skills/ — 前半4〜5で作るスキルの完成形

前半のハンズオン③・④（[docs/01-part1.md](../docs/01-part1.md)）で作るエージェントスキルの**完成形**です。作るのは2つ、「詰めて」（Grill Me系・3枚構成）と「セキュリティレビュー」です。

自分で書いてみるのが本線なので、**まずは見ないで作ってみてください。** 詰まったとき、または答え合わせのときに開きます。

## 1つ目: 「詰めて」（前半4・3枚構成）

```
tsumete      ← 入口。「詰めて」と言ったら起動する
  ├─ tsumetsume  一問ずつ問い詰める進め方
  └─ ddd         決まったことを CONTEXT.md と ADR に書き残す進め方
```

| スキル | 役割 |
|---|---|
| [tsumete](tsumete/SKILL.md) | 入口。詰めながら書き残す。ドキュメント構造とチケット管理もここで面倒を見る |
| [tsumetsume](tsumetsume/SKILL.md) | 実装前に計画を揺さぶる。質問は一度に一つ |
| [ddd](ddd/SKILL.md) | 用語集（[CONTEXT-FORMAT.md](ddd/CONTEXT-FORMAT.md)）と決定記録（[ADR-FORMAT.md](ddd/ADR-FORMAT.md)）の書き方 |

前半4のハンズオンでは、この3つの**最小版**を自分で作ります。ここに置いてあるのは、その先まで育て込んだ完成形です。

## 2つ目: 「セキュリティレビュー」（前半5・1枚）

| スキル | 役割 |
|---|---|
| [security-review](security-review/SKILL.md) | コードを読んで危ないところを重大度つきで報告する。**勝手には直さない** |

**「開発の一工程を、Skillとして切り出せる」**という感覚をつかむのが前半5の目的の一つです。このスキルは後半のハンズオン⑧（レビュー・改善）でそのまま実戦投入します。前半5ではもう一つ、Hooksで「条件が合えば確実に処理を実行する」体験もします（詳細は[docs/01-part1.md](../docs/01-part1.md)）。

## 使い方（自分のプロジェクトに入れる）

スキルは `.claude/skills/` に置くとClaude Codeが自動で読み込みます。**自分の作法はユーザーレベル（`~/.claude/skills/`）、チームの決まりごとはプロジェクトレベル（`<プロジェクト>/.claude/skills/`）**が原則です。宿題・後半でも使い続けるので、今日はユーザーレベルに置くのがおすすめです。

```bash
mkdir -p .claude/skills
cp -r ⟨このリポジトリ⟩/skills/tsumete .claude/skills/
cp -r ⟨このリポジトリ⟩/skills/tsumetsume .claude/skills/
cp -r ⟨このリポジトリ⟩/skills/ddd .claude/skills/
cp -r ⟨このリポジトリ⟩/skills/security-review .claude/skills/
```

置いたら、Claude Codeに「詰めて」「セキュリティレビューして」と言うだけです。スキル名を指定する必要はありません。**フロントマターの `description` を読んで、Claudeが自分で「今これを使う場面だ」と判断します。**

> だから `description` は「何をするスキルか」だけでなく「**いつ使うか**」まで書きます。ここがスキル作りでいちばん効く一行です。

## フォルダの形

```
skills/⟨スキル名⟩/
└── SKILL.md        必須。フロントマター（name・description）＋本文
```

長い書式や参考資料は同じフォルダに別ファイルとして置き、`SKILL.md` からリンクします（`ddd/` がその例）。SKILL.md本体は短く保ち、詳細は必要になったときだけ読ませるのがコツです。
