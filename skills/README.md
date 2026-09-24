# この教材で使うエージェントスキルの完成例

前半で自作する2件と、任意課題で使う2件の完成例です。
前半の2件は、まず自分で作り、詰まったときや答え合わせに開いてください。

<a id="前半で自作する3件"></a>

## 前半で自作する2件

```text
tsumete    人が /tsumete と呼び、質問から実装資料の作成まで進める
  └─ ddd   確定した用語と決定を書き残す
```

| エージェントスキル | 役割 |
|---|---|
| [tsumete](tsumete/SKILL.md) | READMEを読み、一問ずつ問い詰める。用語や決定を `ddd` に記録させ、最後にREADMEとTASKSを書き出す |
| [ddd](ddd/SKILL.md) | 確定した用語をCONTEXTに、変更しにくい決定をADRに残す |

`tsumete` には `disable-model-invocation: true` を付け、開始を人間が決めます。
`ddd` は `tsumete` から使うほか、「用語集を整理して」のように直接頼むこともできます。
用語集と決定記録の書式は [CONTEXT-FORMAT.md](ddd/CONTEXT-FORMAT.md) と [ADR-FORMAT.md](ddd/ADR-FORMAT.md) にあります。

## 任意課題でコピーする2件

| エージェントスキル | 使う場面 |
|---|---|
| [tdd](tdd/SKILL.md) | 自動テストから実装する進め方を試す。テストが落ちることを確認し、最小の実装で通してから、自分で画面を確かめる |
| [prototype](prototype/SKILL.md) | 設計を決められないとき、捨てる前提の試作で判断する |

どちらも本線の必須条件ではありません。
前半3の中心操作デモは、`prototype` を導入せず、本文のプロンプトだけで試せます。

## レビューにはClaude Codeに同梱されたものを使う

後半9は同梱の `/code-review`、後半10の初回プッシュ前は組み込みの `/security-review` を使います。
**`code-review` と `security-review` という名前の独自エージェントスキルをコピーしないでください。**
同名のものがあると、同梱のものと競合します。
以前の教材で保存した人は、プロジェクトと `~/.claude/skills/` の両方を確認し、該当する独自エージェントスキルだけを読み込み対象の外へ退避してから、Claude Codeを開き直します。

仕様への適合は、READMEの完成判定に沿って自分で動作確認します。
コミット前のセキュリティレビューは、[フックの配布物](../hooks/README.md) にある確認観点をサブエージェントに渡します。
コマンドが使えない場合の指示は [レビューのプロンプト](../templates/verify-prompt.md) にあります。

[同梱コードレビューの公式説明](https://code.claude.com/docs/en/code-review)と[同名のエージェントスキルの優先順位](https://code.claude.com/docs/en/skills)も参照してください。

## 自分のプロジェクトに入れる

この教材では `myapp/.claude/skills/⟨名前⟩/SKILL.md` に保存します。
教材リポジトリのcloneは不要で、必要な完成例のページをClaude Codeに渡してコピーさせます。
`ddd` は参照する書式ファイルも同じフォルダに置きます。

`.claude/skills/` 自体を初めて作ったときは、Claude Codeを再起動します。
既存の置き場所への追加や変更は自動で反映されます。
候補に出なければ `/reload-skills`、それでも出なければ再起動して保存先を確認します。
一度呼び出した本文を変更した場合は、`/clear` で旧版の指示を会話から除いて試します。
詳しくは [公式の更新手順](https://code.claude.com/docs/en/skills#edit-a-skill-during-a-session) を参照してください。

ユーザーレベルの `~/.claude/skills/` は別のプロジェクトにも作用するので、講座では使いません。
同名のものがある場合はユーザーレベルが優先されるため、編集した内容が反映されないときは両方の置き場所を確かめます。

## 参考にした設計

配布する4件は、[mattpocock/skills](https://github.com/mattpocock/skills) の設計を教材に合わせたものです。
`tsumete` と `ddd` の役割の違いは [後読みコラム](../docs/columns.md) にまとめています。
