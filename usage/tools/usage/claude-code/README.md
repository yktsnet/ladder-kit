# Claude Code の利用状況

組織のメンバーの Claude Code の利用状況を、メンバー別に毎日集めて並べる。使い方の支援と
seat の配分に使う。

このページは全員を並べて比べる。1人ずつの毎日の推移は、表の名前から開く `members/<名前>.md` にある。
どちらも GitHub Actions が定時に作り直す。時刻は [tools/usage/README.md](../README.md#仕組み) の「仕組み」にある。

<!-- report:start -->
最終更新：2026-11-06 分まで

図と表はどれも 2026-10-12 〜 2026-11-06 の平日の分で、期間のトークン量の多い順に並べる。

### 日ごとのトークン量

![メンバー別の日ごとのトークン量](charts/team-daily.svg)

### 日ごとの commit

上のトークン量と同じ日付で並べる。トークン量が増えた時期に commit も増えているかを見比べる。

![メンバー別の日ごとの commit](charts/team-commits.svg)

### 量と成果

どれも期間の合計である。

| メンバー | 利用時間 | トークン量 | commit | PR | 追加した行 | 削除した行 | 立てた Issue | 閉じた Issue |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| [alice-walker](members/alice-walker.md) | 1472分 | 8147.5M | 268 | 52 | 26137 | 2833 | 99 | 56 |
| [ben-carter](members/ben-carter.md) | 1400分 | 7270.3M | 276 | 49 | 22078 | 2242 | 0 | 0 |
| [henry-ward](members/henry-ward.md) | 725分 | 3924.8M | 107 | 15 | 6048 | 1039 | - | - |
| [chloe-evans](members/chloe-evans.md) | 646分 | 3383.8M | 117 | 23 | 10727 | 1306 | 12 | 17 |
| [emma-hughes](members/emma-hughes.md) | 502分 | 2654.7M | 94 | 18 | 6798 | 1030 | 36 | 32 |
| [daniel-brooks](members/daniel-brooks.md) | 431分 | 2427.4M | 71 | 5 | 5505 | 767 | 0 | 0 |
| [felix-grant](members/felix-grant.md) | 417分 | 2399.3M | 77 | 9 | 6035 | 702 | 0 | 0 |
| [grace-turner](members/grace-turner.md) | 165分 | 911.4M | 28 | 4 | 2734 | 331 | 10 | 22 |
| [isla-morgan](members/isla-morgan.md) | 84分 | 436.7M | 18 | 2 | 2105 | 259 | 19 | 28 |
| [jack-foster](members/jack-foster.md) | 26分 | 133.4M | 9 | 2 | 1006 | 83 | 0 | 0 |

### 使い方

| メンバー | スキル | サブエージェントに任せた割合 | Effort | モデル | 1会話あたりのトークン量 |
|---|--:|--:|---|---|--:|
| alice-walker | 191回 | 35% | 4（low, medium, high, xhigh） | 2（opus 5.5, sonnet 5.5） | 9.6M |
| ben-carter | 317回 | 50% | 3（low, medium, high） | 2（opus 5.5, sonnet 5.5） | 10.9M |
| henry-ward | 88回 | 30% | 2（medium, high） | 2（opus 5.5, sonnet 5.5） | 12.6M |
| chloe-evans | 6回 | 15% | 1（high） | 1（opus 5.5） | 46.4M |
| emma-hughes | 123回 | 41% | 1（medium） | 1（opus 5.5） | 8M |
| daniel-brooks | 37回 | 35% | 1（medium） | 1（opus 5.5） | 9.3M |
| felix-grant | 5回 | 8% | 1（medium） | 1（opus 5.5） | 28.6M |
| grace-turner | 15回 | 20% | 2（medium, high） | 1（opus 5.5） | 4.6M |
| isla-morgan | 0回 | 15% | 2（low, medium） | 1（sonnet 5.5） | 3M |
| jack-foster | 0回 | 29% | 1（medium） | 1（opus 5.5） | 5.8M |

### seat

直近2週（2026-10-24 〜 2026-11-06、土日を含む）を7日ずつに分け、割合の高い方の週で決める。

| メンバー | いまの seat | Premium の上限に対する割合 | Standard の上限に対する割合 | 要る seat |
|---|---|--:|--:|---|
| alice-walker | Premium | 94% | 471% | Premium |
| ben-carter | Premium | 85% | 427% | Premium |
| henry-ward | Premium | 48% | 241% | Premium |
| chloe-evans | Premium | 37% | 185% | Review |
| emma-hughes | Premium | 28% | 142% | Review |
| daniel-brooks | Premium | 28% | 139% | Review |
| felix-grant | Premium | 24% | 118% | Review |
| grace-turner | Standard | 11% | 54% | Standard |
| isla-morgan | Standard | 8% | 39% | Standard |
| jack-foster | Standard | 2% | 9% | 要らない |
| kate-hill | Premium | - | - | 記録が届いているかを確かめる |

要る seat の数：Premium 3・Standard 2・Review 4・決められない 1（いまの名簿は Premium 8・Standard 3）

Premium の上限は Standard の 5 倍である。Standard の上限の2倍以内（100% を超え 200% 以下）の人は Review としている。
<!-- report:end -->

## 良い使い方

| 良い使い方 | 見るところ | できている状態 |
|---|---|---|
| 毎日の仕事で使う | 個人のページの「毎日の推移」 | 平日はほぼ毎日使っている |
| 成果まで Claude Code で仕上げる | 量と成果の「commit」「PR」「行数」 | 利用時間に見合った commit・PR が出ている |
| 作業に合わせて Effort を変える | 使い方の「Effort」 | 2段階以上。軽い作業は low・medium、設計や難しい調査は high 以上 |
| 作業に合わせてモデルを変える | 使い方の「モデル」 | 2系統以上。新しいバージョンが出たら切り替えている |
| 作業を Issue にして、閉じる | 量と成果の「立てた Issue」「閉じた Issue」 | 立てた Issue があり、閉じられている |
| 繰り返す作業をスキルにして使う | 使い方の「スキル」 | 使った回数が多い |
| 調べ物やテストの実行はサブエージェントに任せる | 使い方の「サブエージェントに任せた割合」 | 0% ではない |
| 1つの会話を長く続けない | 使い方の「1会話あたりのトークン量」 | 突出していない。作業が変わるときは `/clear`（それまでの会話を消す）し、長い作業の途中は `/compact`（会話を要約して縮める）している |

## 文書

| 文書 | 中身 |
|---|---|
| [docs/metrics.md](docs/metrics.md) | 各項目が何を数え、何を数えないか |
| [docs/seats.md](docs/seats.md) | seat の判定の規則、上限の置き方、名簿の書き方 |
| [docs/setup.md](docs/setup.md) | 何が集まるか、データの流れ、送信設定、まだ取っていないもの |
