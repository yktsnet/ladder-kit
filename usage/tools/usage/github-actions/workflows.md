# ワークフロー別の週ごとの分数

<!-- render.py が作り直す。手で直さない -->

[README.md](README.md) の分数が増えたときに、何が増えたかをここで見る。直近4週の分数の多い順に、上位 10 件のワークフローを並べる。週は月曜に始まる。

分数が増えたワークフローについて、回数が増えたのか、1回あたりの分数が増えたのかを下の2つの表で見分ける。

最終更新：2026-11-06 分まで

## 分数

| リポジトリ | ワークフロー | 起動のきっかけ | 10/12〜 | 10/19〜 | 10/26〜 | 11/2〜（途中） |
|---|---|---|--:|--:|--:|--:|
| data-pipeline | nightly | `schedule` | 125 | 132 | 128 | 93 |
| web-app | e2e | `pull_request` | 132 | 83 | 197 | 60 |
| web-app | CI | `pull_request` | 95 | 109 | 116 | 150 |
| api-server | CI | `pull_request` | 60 | 69 | 47 | 82 |
| mobile-app | Build | `pull_request` | 59 | 54 | 31 | 49 |
| web-app | CI | `push` | 67 | 21 | 42 | 63 |
| api-server | Deploy | `push` | 70 | 7 | 47 | 13 |
| infra | terraform-plan | `pull_request` | 20 | 21 | 11 | 14 |
| admin-console | CI | `pull_request` | 23 | 8 | 9 | 19 |
| docs-site | Deploy | `push` | 18 | 10 | 9 | 15 |

## 回数

| リポジトリ | ワークフロー | 起動のきっかけ | 10/12〜 | 10/19〜 | 10/26〜 | 11/2〜（途中） |
|---|---|---|--:|--:|--:|--:|
| data-pipeline | nightly | `schedule` | 7 | 7 | 7 | 5 |
| web-app | e2e | `pull_request` | 14 | 9 | 21 | 7 |
| web-app | CI | `pull_request` | 22 | 25 | 29 | 37 |
| api-server | CI | `pull_request` | 19 | 22 | 14 | 27 |
| mobile-app | Build | `pull_request` | 8 | 7 | 4 | 7 |
| web-app | CI | `push` | 16 | 5 | 10 | 15 |
| api-server | Deploy | `push` | 11 | 1 | 7 | 2 |
| infra | terraform-plan | `pull_request` | 6 | 6 | 3 | 4 |
| admin-console | CI | `pull_request` | 11 | 4 | 4 | 9 |
| docs-site | Deploy | `push` | 9 | 5 | 4 | 7 |

## 1回あたりの分数

| リポジトリ | ワークフロー | 起動のきっかけ | 10/12〜 | 10/19〜 | 10/26〜 | 11/2〜（途中） |
|---|---|---|--:|--:|--:|--:|
| data-pipeline | nightly | `schedule` | 17.9 | 18.9 | 18.3 | 18.6 |
| web-app | e2e | `pull_request` | 9.4 | 9.2 | 9.4 | 8.6 |
| web-app | CI | `pull_request` | 4.3 | 4.4 | 4.0 | 4.1 |
| api-server | CI | `pull_request` | 3.2 | 3.1 | 3.4 | 3.0 |
| mobile-app | Build | `pull_request` | 7.4 | 7.7 | 7.8 | 7.0 |
| web-app | CI | `push` | 4.2 | 4.2 | 4.2 | 4.2 |
| api-server | Deploy | `push` | 6.4 | 7.0 | 6.7 | 6.5 |
| infra | terraform-plan | `pull_request` | 3.3 | 3.5 | 3.7 | 3.5 |
| admin-console | CI | `pull_request` | 2.1 | 2.0 | 2.2 | 2.1 |
| docs-site | Deploy | `push` | 2.0 | 2.0 | 2.2 | 2.1 |
