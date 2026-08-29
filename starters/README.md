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

## 救済タグ

お題A・B・Cそれぞれについて、**完成まで作り込んだ状態**をGitタグとして1つずつ用意しています。自分で触っていて収拾がつかなくなったときの、最後の逃げ場です。

- `rescue/a-pomodoro-timer` — 中身は `starters/a-pomodoro-timer/README.md` と `index.html`
- `rescue/b-shindan-chart` — 中身は `starters/b-shindan-chart/README.md` と `index.html`
- `rescue/c-habit-tracker` — 中身は `starters/c-habit-tracker/README.md` と `index.html`

> **これは starters/（教材リポジトリ側）のタグです。** 実際の作業は `vibecoding-0908` 側で行っているはずなので、「タグの状態に戻す」のではなく「**タグの中の `index.html` を、`vibecoding-0908` の `index.html` に上書きコピーしてくる**」という操作になります。

### 使うタイミング

- [リカバリー3手](../docs/01-part1.md)（貼る・戻す・小さくする）を2回試しても直らない
- 挙手してメンターに見てもらっても、今日の残り時間では厳しそう
- 「動く状態」が欲しいだけで、直すこと自体にこだわる必要はない場面

**「戻って進む」は今日教えている正規の技術です。** 恥ずかしいことでも失敗でもありません。

### いちばん簡単な方法: ブラウザで完成版を保存する

**Gitの知識もClaude Codeの操作も要りません。ZIPでダウンロードした人もこの方法が使えます。** 自分のお題に対応するリンクを開き、出てきたコードをすべて選択してコピーし、自分の作業フォルダの `index.html` の中身を丸ごと置き換えてください。

- お題A: `https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/rescue/a-pomodoro-timer/starters/a-pomodoro-timer/index.html`
- お題B: `https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/rescue/b-shindan-chart/starters/b-shindan-chart/index.html`
- お題C: `https://raw.githubusercontent.com/AI-Eng-Dojo/getting-started-vibecoding/rescue/c-habit-tracker/starters/c-habit-tracker/index.html`

> 置き換えるのが不安なら、いまの `index.html` の名前を先に `index-broken.html` などに変えてから、新しく保存したファイルを `index.html` にリネームしてください。**分からなければここもClaude Codeに「やっておいて」と頼んで構いません。**

### Claude Codeに頼む方法（教材リポジトリをGit cloneした人向け）

教材リポジトリをZIPではなく `git clone` で取得した人は、**教材リポジトリを開いているClaude Code**（このリポジトリを開いたセッション。無ければ新しく開いてください）に、そのまま次のように頼めます。⟨ ⟩は自分の状況に置き換えます。

```text
このリポジトリのGitタグ「rescue/a-pomodoro-timer」における
starters/a-pomodoro-timer/index.html の中身を、
⟨vibecoding-0908の絶対パス⟩/index.html に上書きしてください。
いま index.html にあるファイルは、念のため同じ場所に index-broken.html という名前で
コピーしてから進めてください。
```

> **`vibecoding-0908` の絶対パスが分からない場合**は、`vibecoding-0908` 側のClaude Codeで「今のフォルダの絶対パスを教えて」と聞けば分かります。また、教材リポジトリを開いているClaude Codeに `vibecoding-0908` のパスを初めて触らせるときは、「このフォルダの外を操作してよいか」の確認が出ることがあります。自分が今伝えたフォルダであれば許可して構いません。

コピーが終わったら、`vibecoding-0908` 側のClaude Codeに戻って続きを再開してください。**今の壊れた状態は `index-broken.html` として残っているので、あとで見比べることもできます。**

### 自分のPCでGitコマンドを直接使う場合（任意・上級者向け）

```bash
# 教材リポジトリのフォルダで実行する。事前に git clone している必要があります（ZIPでは使えません）
# タグの一覧を見る
git tag -l 'rescue/*'

# 念のため、いまの作業フォルダを丸ごとバックアップしておく
cp -r "⟨vibecoding-0908の絶対パス⟩" "⟨vibecoding-0908の絶対パス⟩-broken"

# お題Aの完成版ファイルだけを取り出して、vibecoding-0908 に上書きコピーする
# （starters/a-pomodoro-timer/ 配下だけを対象にし、2階層分のパスを取り除いて展開しています）
git archive rescue/a-pomodoro-timer -- starters/a-pomodoro-timer \
  | tar -x -C "⟨vibecoding-0908の絶対パス⟩" --strip-components=2
```

`git checkout rescue/...` で教材リポジトリ自体をタグの状態に切り替えることもできますが、そのままだと教材リポジトリが「ブランチのない状態（detached HEAD）」になります。作業が終わったら `git checkout main` で元に戻しておいてください。

### これは「starters/を選んだ人」だけの仕組みです

自由なアイデアでハンズオン①を進めた人（starters/を使わなかった人）や、宿題・後半で自分のアプリを作っている人には、対応する救済タグは**ありません**。そちらの「戻る」手段は、今日ずっと使う**リカバリー3手**（貼る・戻す・小さくする）です。加えて、こまめに「いまの状態をgitでコミットして保存してください」とClaude Codeに頼んで保存しておけば、そのコミットに「さっき保存した状態に戻して」と頼んで戻ることもできます（保存していない場合は戻れないので、こまめな保存が前提です）。

> 運営メモ:
> - 各救済タグは、対応する `starters/⟨題⟩/` を実際に完成まで作り込んだ結果を、開催回の前にタグ付けして作成します。タグ名はフォルダ名と揃えて `rescue/⟨フォルダ名⟩`（例: `rescue/a-pomodoro-timer`）。中身は `README.md` と `index.html` のみ（余計なファイルを含めない）。複数ハンズオン段階にまたがる救済は今回のカリキュラムでは扱いません（starters/はハンズオン①の一発勝負のため）。
> - **現在リポジトリには `rescue/handson3-a`・`-b`・`-c` という古い命名のタグが残っていますが、これは3パート構成へ再編する前の別ブランチ上のコミットで、`main` からは辿れません。** 中身（各starterの完成版 `index.html`）自体は流用できるので、開催前に `main` 上へ `rescue/a-pomodoro-timer` などの新しい名前で作り直し、古いタグは整理してください。
> - raw.githubusercontent.com のリンクは**リポジトリがpublicであること**が前提です。非公開にする場合はこの方式が使えなくなるため、この節ごと見直してください。
