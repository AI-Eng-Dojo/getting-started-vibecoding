# skills/ — この教材で使うスキルの完成形

このワークショップで扱うエージェントスキルの**完成形**です。スキルは2種類あります。

| | いつ | どう扱うか |
|---|---|---|
| **前半で自分で作る** | 前半4（ハンズオン③） | `tsumete`・`tsumetsume`・`ddd` の3枚。**自分で書くのが本線**。ここにあるのは答え合わせ用 |
| **後半でコピーして使う** | 後半9・10（ハンズオン⑥・⑦） | `tdd`・`code-review`・`security-review` ＋任意の `prototype`。**書かずにコピーして構いません** |

前半で「スキルとは何か」を自分の手で作って理解し、後半では**できあいのスキルを組み合わせて開発工程を回す**——という2段構えです。

**前半のぶんは、まずは見ないで作ってみてください。** 詰まったとき、または答え合わせのときに開きます。

## 前半で自分で作る: 「詰めて」3枚構成

```
tsumete      ← 入口。自分で `/tsumete` と打ったときだけ起動する
  ├─ tsumetsume  一問ずつ問い詰める進め方
  └─ ddd         決まったことを CONTEXT.md と ADR に書き残す進め方
```

| スキル | 役割 |
|---|---|
| [tsumete](tsumete/SKILL.md) | 入口。下の2つを呼び出し、最後に `README.md` と `TASKS.md` を書き出す。`disable-model-invocation: true` 付きで、**Claudeが勝手に起動することはない** |
| [tsumetsume](tsumetsume/SKILL.md) | 実装前に計画を揺さぶる。質問は一度に一つ |
| [ddd](ddd/SKILL.md) | 用語集（[CONTEXT-FORMAT.md](ddd/CONTEXT-FORMAT.md)）と決定記録（[ADR-FORMAT.md](ddd/ADR-FORMAT.md)）の書き方 |

前半4のハンズオンでは、この3つの**最小版**を自分で作ります。ここに置いてあるのは、その先まで育て込んだ完成形です。

## 後半でコピーして使う: 開発工程の4枚

宿題で書いた仕様を、実際のソフトウェアにするまでの工程を、そのままスキルに分けたものです。

| スキル | 使う場面 | 役割 |
|---|---|---|
| [tdd](tdd/SKILL.md) | 後半9（実装） | **目印を先に確定させてから**、1件ずつ最小実装する。green を宣言するのは人間 |
| [code-review](code-review/SKILL.md) | 後半10（レビュー） | **仕様どおりか**と**作法どおりか**を、混ぜずに別々に報告する |
| [security-review](security-review/SKILL.md) | 後半10（レビュー） | 危ないところを重大度つきで報告する。**勝手には直さない** |
| [prototype](prototype/SKILL.md) | 任意・詰まったとき | 決められない設計を、**捨てる前提の小さい試作**で判断する |

### 3枚が噛み合っている点

- `tdd` は**リファクタリングをしません**。読みにくさ・重複は `code-review` の Standards 軸が拾います。**整えるのは、動いたあと**という分担です
- `code-review` は**セキュリティを扱いません**。そこは `security-review` の担当です。1つのスキルに全部を入れると、報告が混ざって何も見えなくなります
- `code-review` の Spec 軸が読むのは、**宿題で自分が書いた `README.md`** です。仕様が人に読まれるだけのものではなく、**レビューの入力として実際に使われる**のがここです
- `security-review` だけが `.claude/security-reviewed` という「レビュー済みの印」を作ります。後半10で設定するHookは、この印を見て `git push` や `wrangler deploy` を止めます（詳細は [docs/02-part2.md](../docs/02-part2.md)）

## 使い方（自分のプロジェクトに入れる）

スキルは `.claude/skills/` に置くとClaude Codeが自動で読み込みます。**自分の作法はユーザーレベル（`~/.claude/skills/`）、チームの決まりごとはプロジェクトレベル（`<プロジェクト>/.claude/skills/`）**が原則です。宿題・後半でも使い続けるので、今日はユーザーレベルに置くのがおすすめです。

```bash
mkdir -p ~/.claude/skills
cp -r ⟨このリポジトリ⟩/skills/tsumete ~/.claude/skills/
cp -r ⟨このリポジトリ⟩/skills/tsumetsume ~/.claude/skills/
cp -r ⟨このリポジトリ⟩/skills/ddd ~/.claude/skills/
cp -r ⟨このリポジトリ⟩/skills/tdd ~/.claude/skills/
cp -r ⟨このリポジトリ⟩/skills/code-review ~/.claude/skills/
cp -r ⟨このリポジトリ⟩/skills/security-review ~/.claude/skills/
cp -r ⟨このリポジトリ⟩/skills/prototype ~/.claude/skills/
```

置いたら、Claude Codeに「セキュリティレビューして」と言うだけです。スキル名を指定する必要はありません。**フロントマターの `description` を読んで、Claudeが自分で「今これを使う場面だ」と判断します。**

> だから `description` は「何をするスキルか」だけでなく「**いつ使うか**」まで書きます。ここがスキル作りでいちばん効く一行です。

**ただし `tsumete` だけは例外で、`/tsumete` と打って呼びます。** `disable-model-invocation: true` が入っていて、Claudeの判断では起動しないようにしてあるためです。問い詰めは何十往復もする長い作業なので、**始めるかどうかは人間が決める**、という設計です。中身を持つ `tsumetsume`・`ddd` のほうは、通常どおりClaudeが自分で判断して呼びます。

## フォルダの形

```
skills/⟨スキル名⟩/
└── SKILL.md        必須。フロントマター（name・description）＋本文
```

長い書式や参考資料は同じフォルダに別ファイルとして置き、`SKILL.md` からリンクします（`ddd/` がその例）。SKILL.md本体は短く保ち、詳細は必要になったときだけ読ませるのがコツです。

## 元ネタ

ここに置いた7枚のうち6枚は、公開されているスキル集（[github.com/mattpocock/skills](https://github.com/mattpocock/skills)）の設計を下敷きにしています（`security-review` だけはこの教材オリジナルです）。**どれが原理で、どれが入口なのか**という地図は [docs/columns.md](../docs/columns.md) の★10にまとめました（当日は読まず、帰りに）。
