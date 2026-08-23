---
name: tsumete
description: Interrogate a plan or design until both sides genuinely agree, and record what gets settled as repository documentation. Use when the user says "詰めて", asks to stress-test a plan before implementation, or wants the result captured as durable docs, ADRs, and implementation tickets.
---

# 詰めて

`tsumetsume` スキルのセッションを、`ddd` スキルを併用しながら実行してください。

つまり、計画について一問ずつ問い詰めて共通理解に到達させると同時に、その過程で確定した用語を `CONTEXT.md` に、記録に値する決定を `docs/adr/` に、その場で書き残していきます。

- 詰め詰めの進め方: [tsumetsume/SKILL.md](../tsumetsume/SKILL.md)
- ドメインモデリングの進め方: [ddd/SKILL.md](../ddd/SKILL.md)

両方を読んでから始めてください。

## 始める前に: リポジトリのドキュメント構造を確かめる

質問を始める前に、このリポジトリが「決まったことをどこに書くか」を持っているかを調べます。ここを曖昧にしたまま詰めると、合意した内容が会話の中に消えます。

### 1. 既存の構造を調べる

次を実際に確認してください。ユーザーに聞くのではなく、自分で見ます。

- `README.md` にドキュメントの案内があるか
- `docs/` があるか。あるなら何が入っているか
- 用語集（`CONTEXT.md` / `CONTEXT-MAP.md` / 用語集にあたるもの）があるか
- 決定記録（`docs/adr/` / `docs/decisions/` など）があるか
- 実装チケットや作業一覧をリポジトリ内で管理しているか（`docs/tickets/`、`TODO.md`、`backlog/` など）

### 2. あるものは尊重する

**既存の構造が見つかったら、それに従ってください。** 名前が一般的でなくても、置き場所が独特でも、勝手に作り直さないこと。既存の書式・命名規則・採番規則を読み取り、それに合わせます。

足りないものだけを足します。たとえば用語集はあるが決定記録の置き場がないなら、決定記録だけを既存の流儀に合わせて追加します。

### 3. なければ構造そのものを先に定義する

何もなければ、**最初に構造を決めて、その定義自体をリポジトリに書いてください。** 既定はこれです。

```
/
├── CONTEXT.md              用語集（このプロジェクトの言葉）
└── docs/
    ├── README.md           ドキュメント一覧。どこに何があるかの索引
    ├── adr/                決定記録
    │   └── 0001-{slug}.md
    └── tickets/
        ├── README.md       チケット一覧（ID・タイトル・状態・依存）
        └── T-001-{slug}.md 個別タスク
```

`docs/README.md` には、少なくとも次を書きます。

- このリポジトリのドキュメントの一覧と、それぞれの役割
- 新しい決定・新しい用語・新しいタスクが出たとき、どこに書けばよいか

構造を提案したら、実装に入る前にユーザーの同意を取ってください。決めるのはユーザーです。

### 4. 実装チケットもリポジトリ内で管理する

詰めた結果として出てくる「やること」は、会話の中やユーザーの頭の中ではなく、**リポジトリ内のファイルとして残します。** 外部のツールを前提にしないでください。

- `docs/tickets/README.md` に一覧を持ち、各チケットの ID・タイトル・状態・依存関係が一覧で読めるようにする
- 個別タスクは 1 チケット 1 ファイル。何を作るか、完了条件は何か、どの決定（ADR）と用語（CONTEXT.md）に依存するかを書く
- チケットは詰めながらその場で起票する。セッションの最後にまとめて作らない

## セッション中の書き残し方

`tsumetsume` の質問を一問ずつ進めながら、確定した瞬間に該当ファイルへ書きます。

| 確定したもの | 書く場所 |
|---|---|
| 用語の定義 | `CONTEXT.md`（書式は [ddd/CONTEXT-FORMAT.md](../ddd/CONTEXT-FORMAT.md)） |
| 元に戻しにくい決定 | `docs/adr/`（書式と判断基準は [ddd/ADR-FORMAT.md](../ddd/ADR-FORMAT.md)） |
| やること | `docs/tickets/` と、その一覧 |

まとめて後回しにしないこと。合意したその場で書くのが、このスキルの本体です。
