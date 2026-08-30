# starters/ — 前半ハンズオン①の代替お題テンプレート

前半ハンズオン①（[docs/01-part1.md](../docs/01-part1.md)）で、自分のアイデアがすぐに思いつかないとき・もう少し手順のある題材で試したいときに使う、お題3種の開始状態フォルダです。必須ではありません。

## 使い方

1. 3つから1つ選ぶ（迷ったらA）
2. 選んだフォルダの中身を、`vibecoding-0908` にコピーしてClaude Codeで開く
3. フォルダ内READMEの指示文をそのまま貼り付けて実行

| お題 | フォルダ | こんな人に |
|---|---|---|
| A: ポモドーロタイマー | [a-pomodoro-timer/](a-pomodoro-timer/) | 迷ったらこれ |
| B: 診断チャート | [b-shindan-chart/](b-shindan-chart/) | コンテンツを作るのが好き |
| C: 習慣トラッカー | [c-habit-tracker/](c-habit-tracker/) | データが残るアプリを作りたい |

## 救済版（完成状態）

お題A・B・Cそれぞれについて、**完成まで作り込んだ状態**を1ファイルずつ置いてあります。自分で触っていて収拾がつかなくなったときの、最後の逃げ場です。

- `starters/a-pomodoro-timer/rescue/index.html`
- `starters/b-shindan-chart/rescue/index.html`
- `starters/c-habit-tracker/rescue/index.html`

> **これは教材リポジトリ側のファイルです。** 実際の作業は `vibecoding-0908` 側で行っているはずなので、「このリポジトリを戻す」のではなく「**救済版の `index.html` を、`vibecoding-0908` の `index.html` に上書きコピーしてくる**」という操作になります。

### 使うタイミング

- [リカバリー3手](../docs/01-part1.md)（貼る・戻す・小さくする）を2回試しても直らない
- 挙手してメンターに見てもらっても、今日の残り時間では厳しそう
- 「動く状態」が欲しいだけで、直すこと自体にこだわる必要はない場面

**「戻って進む」は今日教えている正規の技術です。** 恥ずかしいことでも失敗でもありません。

### いちばん簡単な方法: ブラウザで完成版を保存する

**Gitの知識もClaude Codeの操作も要りません。ZIPでダウンロードした人もこの方法が使えます。** 自分のお題に対応するリンクを開き、出てきたコードをすべて選択してコピーし、自分の作業フォルダの `index.html` の中身を丸ごと置き換えてください。

- お題A: `https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/main/starters/a-pomodoro-timer/rescue/index.html`
- お題B: `https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/main/starters/b-shindan-chart/rescue/index.html`
- お題C: `https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/main/starters/c-habit-tracker/rescue/index.html`

> 置き換えるのが不安なら、いまの `index.html` の名前を先に `index-broken.html` などに変えてから、新しく保存したファイルを `index.html` にリネームしてください。**分からなければここもClaude Codeに「やっておいて」と頼んで構いません。**

### Claude Codeに頼む方法

**教材リポジトリを開いている必要はありません。** `vibecoding-0908` を開いているClaude Codeに、そのまま次のように頼めます。⟨ ⟩は自分のお題に置き換えます。

```text
次のURLの中身を、このフォルダの index.html に上書きしてください。
https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/main/starters/⟨a-pomodoro-timer⟩/rescue/index.html

いま index.html にあるファイルは、念のため同じ場所に index-broken.html という名前で
コピーしてから進めてください。
```

コピーが終わったら、そのまま続きを再開してください。**今の壊れた状態は `index-broken.html` として残っているので、あとで見比べることもできます。**

### 自分のPCでコマンドを直接使う場合（任意・上級者向け）

```bash
# 念のため、いまのファイルを退避してから上書きする
cd "⟨vibecoding-0908の絶対パス⟩"
cp index.html index-broken.html
curl -o index.html https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/main/starters/a-pomodoro-timer/rescue/index.html
```

教材リポジトリを `git clone` している場合は、そちらの `starters/⟨お題⟩/rescue/index.html` をコピーしても同じです。**`git checkout` でタグやブランチを切り替える必要はありません。**

### これは「starters/を選んだ人」だけの仕組みです

自由なアイデアでハンズオン①を進めた人（starters/を使わなかった人）や、宿題・後半で自分のアプリを作っている人には、対応する救済版は**ありません**。そちらの「戻る」手段は、今日ずっと使う**リカバリー3手**（貼る・戻す・小さくする）です。加えて、こまめに「いまの状態をgitでコミットして保存してください」とClaude Codeに頼んで保存しておけば、そのコミットに「さっき保存した状態に戻して」と頼んで戻ることもできます（保存していない場合は戻れないので、こまめな保存が前提です）。

> 運営メモ:
> - 各救済版は、対応する `starters/⟨題⟩/` を実際に完成まで作り込んだ結果を、開催回の前に `main` 上の `starters/⟨題⟩/rescue/index.html` として更新します。**Gitタグは使いません。** タグ名と文書中のURLを人手で同期する必要があり、実際に一度壊れた（案内していた3本のURLが全て404だった）ためです
> - 参照は常に `main` を指すので、**リポジトリを見ればファイルの実在が確認できます。** あわせて `.github/workflows/link-check.yml` が、救済版3本と教材内の外部リンクを週次とPR時に叩いて404を検出します
> - 旧タグ `rescue/handson3-a`・`-b`・`-c` は `main` から辿れない別コミットを指しています。**どこからも参照していないので放置して構いません**が、整理する場合は `git push origin --delete rescue/handson3-a` などで消せます
> - raw.githubusercontent.com のリンクは**リポジトリがpublicであること**が前提です。非公開にする場合はこの方式が使えなくなるため、この節ごと見直してください
