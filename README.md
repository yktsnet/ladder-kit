# mgmt-kit

エージェント（Claude Code 等）で開発するチームを、マネジメントの側から見るための道具を置く。
型を配る側は [sdlc-kit](https://github.com/yktsnet/sdlc-kit) が受け持ち、このリポは配った型が
どう回り、人がどこにいて、いくら掛かっているかを読む側を受け持つ。

| 道具 | 答える問い | 置き場 |
|---|---|---|
| ladder | 1人がどの段階にいて、次にどの軸を上げるか | `ladder/` |
| usage | メンバーが Claude Code をどう使い、どれだけ成果を出しているか。seat が使い方に見合っているか | `usage/` |

**usage の数字は ladder の採点に足さない。** トークン量の9割以上はキャッシュの読み込みで、
会話の長さと呼び出しの回数でほぼ決まる。多く使ったことは、多く仕事を進めたことにならない。
ladder は成果物だけを読んで点を付け、usage は使い方を教える相手と、seat と予算の判断に使う。

## ladder：評価の物差し

評価・標準化・採用を、1本の物差しの上で繋ぐ。

- **軸を決める。**何を測るかが決まると、標準化が何を揃えるべきかも決まる
- **型を配る。**標準化された手順をチームで回すと、成果物の形が揃う
- **成果物が見える。**揃った成果物は、書式の差ではなく中身の差として読める
- **評価ができる。**読めるものがあって初めて、人の現在地を置ける
- **既存人材と候補者を同じ尺度で測れる。**軸は共通で、替えるのは証拠源だけになる

**価値はこの5つが繋がっていることにある。** 評価軸だけを作ると、測る材料が出てこない。
標準化だけをやると、回っているかどうかを誰も判定できない。採用だけを別の基準で回すと、
入れた人を育てる段になって尺度が合わない。3つを別々の制度として持つと、
繋ぎ目を人が埋め続けることになる。

| | 中身 |
|---|---|
| [ladder/docs/ladder.md](ladder/docs/ladder.md) | 正本。5軸5段階と各セルの判定文、判定に読むもの |
| [ladder/docs/personas.md](ladder/docs/personas.md) | 各段階の参照ペルソナ。軸の凸凹を持たせた5人 |
| [ladder/docs/scoring.md](ladder/docs/scoring.md) | 在籍者を採点し、次に上げる軸を決めるまでの手順 |
| [ladder/docs/hiring.md](ladder/docs/hiring.md) | 同じ軸を候補者に当てる手順。証拠源の替え方 |
| [ladder/docs/adapt.md](ladder/docs/adapt.md) | 自社へ持ち込むときの差し替え方 |
| [ladder/docs/ref/sources.md](ladder/docs/ref/sources.md) | 下敷きにした公開ラダーとライセンス |

### 軸が先に来る

標準化を先にやると、揃えるものが「書式」で止まる。何を測るかを決めてから型を配ると、
型は測りたいものが成果物に出る形になる。

`ladder/docs/ladder.md` の判定文が `PLAN.md` や `docs/guarantees.md` を名指ししているのはそのためで、
**判定文と型の置き場が1対1で対応している。** 型に無い置き場を判定文が指していたら、
どちらかが間違っている。

### 採点を回す

`ladder/.claude/skills/ladder-score/` に、採点する skill が入っている。採点する相手の成果物が
あるリポジトリへ、`docs/` ごとコピーして使う。

```bash
git clone https://github.com/yktsnet/mgmt-kit.git
cp mgmt-kit/ladder/docs/{ladder,scoring,hiring,adapt}.md ~/repos/target/docs/
cp -r mgmt-kit/ladder/.claude/skills/ladder-score ~/repos/target/.claude/skills/
```

skill は判定文を暗記や印象で当てず、各セルの「読むもの」を実際に開いて根拠を引く。出るのは
5軸の点と次に上げる1軸で、総合点は出さない。**採点結果は既定でファイルに書かない。**
置き場と実名の扱いは、残すと決めた側が先に決める。

### 測る対象について

エージェントを走らせる開発では、実装の速さは人の差になりにくい。差は、配られた型に
乗れるか、乗ったうえで型を直せるかへ移る。B 軸を独立して置いてあるのはそのためで、
この軸だけは**型を配っていない組織では測れない**。

型を配る前にこの物差しを当てると、判定文の大半が空欄になる。順序は入れ替えられない。

## usage：Claude Code の利用状況

Claude Code の OpenTelemetry の記録を New Relic で受け、メンバー別に毎日並べる。GitHub Actions の定時実行が
集め、表とグラフを作り直してコミットする。

- **量と成果**：利用時間・トークン量と、Claude Code が作った commit・PR・行数。立てた Issue と閉じた Issue は GitHub から数える
- **使い方**：スキルを使った回数、サブエージェントに任せた割合、Effort とモデルの切り替え、1会話あたりのトークン量。表の横に、それぞれの良い使い方と、できている状態を置く
- **seat**：直近2週の費用を上限に対する割合で見て、1人ずつ要る seat（Premium・Standard）を出す

同じ定時実行で、組織の private リポジトリが使った GitHub Actions の分数も数え、月末に無料枠と予算のどこまで届くかを見込む。
エージェントで PR が増えると CI の分数も増えるので、並べて置いている。

サンプルは [Claude Code の利用状況](usage/tools/usage/claude-code/README.md) と [Actions の分数](usage/tools/usage/github-actions/README.md) にある。
どちらも架空の10人と8リポのダミーデータから作った。
`scripts/sample-usage.py` がダミーデータを作り、続けて各集計の `render.py` で表とグラフを作り直す。

### 取り込む

`usage/` は取り込み先の配置を写した形になっている。集計を置く管理用のリポジトリへコピーし、サンプルのデータと名簿を消す。

```bash
cp -R mgmt-kit/usage/. <管理用のリポジトリ>/
cd <管理用のリポジトリ>/tools/usage
rm -rf claude-code/{data,members,charts} github-actions/{data,charts} claude-code/{seats,github}.json
```

そのあとは、コピーした `tools/usage/README.md` の「導入の手順」に従う。上限の値や受け先など、組織に合わせて替えるものも同じ文書にある。

## License

MIT
