# ladder-kit

AI エージェントで開発を回すチームのための、エンジニア評価ラダー。

軸と段階で座標系を1つ作り、現在地と到達像を同じ物差しの上に置く。評価そのものが目的ではなく、
次に上げる軸を決めるために読む。

| | 中身 |
|---|---|
| [docs/ladder.md](docs/ladder.md) | 正本。5軸5段階と各セルの判定文、判定に読むもの |
| [docs/personas.md](docs/personas.md) | 各段階の参照ペルソナ。軸の凸凹を持たせた5人 |
| [docs/scoring.md](docs/scoring.md) | 1人を採点し、次に上げる軸を決めるまでの手順 |
| [docs/adapt.md](docs/adapt.md) | 自社へ持ち込むときの差し替え方 |
| [docs/ref/sources.md](docs/ref/sources.md) | 下敷きにした公開ラダーとライセンス |

## 既存の公開ラダーと違うところ

- **判定文を成果物への参照で書く。** 「自律的に」「複雑な」といった評価者の解釈に委ねる語を
  使わず、リポジトリの何を開けば真偽が確かめられるかまで書く
- **配られた型の運用を独立した軸として持つ。** エージェントを走らせる開発では、
  型に乗れるかどうかが個人の書き方の巧拙より先に効く
- **同じ物差しを、評価・育成・選考の3つに当てる。** 軸と段階は共通で、替えるのは証拠源だけに
  する。社内は成果物から、候補者は面接と経歴から読む。育成の処方箋も別立てにせず、
  配られた型を回すこと自体に載せる
- **報酬帯を持たない。** 段階と報酬の結び付け方は各社で違う

## 採点を回す

`.claude/skills/ladder-score/` に、採点する skill が入っている。採点する相手の成果物が
あるリポジトリへ、`docs/` ごとコピーして使う。

```bash
git clone https://github.com/yktsnet/ladder-kit.git
cp -r ladder-kit/docs/ladder.md ladder-kit/docs/scoring.md ladder-kit/docs/adapt.md ~/repos/target/docs/
cp -r ladder-kit/.claude/skills/ladder-score ~/repos/target/.claude/skills/
```

skill は判定文を暗記で当てず、各セルの「読むもの」を実際に開いて根拠を引く。出るのは
5軸の点と次に上げる1軸で、総合点は出さない。**採点結果は既定でファイルに書かない。**
置き場と実名の扱いは、残すと決めた側が先に決める。

## 型の配布は扱わない

判定文は、配られた型の置き場を名指しする形で書いてある。配る側は
[sdlc-kit](https://github.com/yktsnet/sdlc-kit) が持ち、ここはそこに乗れているかを測る。
別の型を使っている場合の読み替えは [docs/adapt.md](docs/adapt.md) にある。

型を配る前の段階でこの物差しを当てると、判定文の大半が空欄になる。

## License

MIT
