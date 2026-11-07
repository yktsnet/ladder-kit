# ワークフロー別の週ごとの分数

<!-- render.py が作り直す。手で直さない -->

[README.md](README.md) の分数が増えたときに、何が増えたかをここで見る。直近4週の分数の多い順に、上位 10 件のワークフローを並べる。週は月曜に始まる。

分数が増えたワークフローについて、回数が増えたのか、1回あたりの分数が増えたのかを下の2つの表で見分ける。

最終更新：2026-11-06 分まで

## 分数

| リポジトリ | ワークフロー | 起動のきっかけ | 10/12〜 | 10/19〜 | 10/26〜 | 11/2〜（途中） |
|---|---|---|--:|--:|--:|--:|
| web-app | e2e | `pull_request` | 163 | 136 | 197 | 167 |
| web-app | CI | `pull_request` | 151 | 155 | 145 | 180 |
| data-pipeline | nightly | `schedule` | 151 | 130 | 136 | 97 |
| api-server | CI | `pull_request` | 97 | 86 | 113 | 68 |
| mobile-app | Build | `pull_request` | 21 | 73 | 76 | 44 |
| api-server | Deploy | `push` | 52 | 30 | 43 | 32 |
| web-app | CI | `push` | 32 | 40 | 20 | 44 |
| admin-console | CI | `pull_request` | 37 | 35 | 24 | 24 |
| infra | terraform-plan | `pull_request` | 28 | 11 | 18 | 10 |
| design-system | Delete merged branch | `pull_request` | 13 | 19 | 12 | 6 |

## 回数

| リポジトリ | ワークフロー | 起動のきっかけ | 10/12〜 | 10/19〜 | 10/26〜 | 11/2〜（途中） |
|---|---|---|--:|--:|--:|--:|
| web-app | e2e | `pull_request` | 17 | 14 | 21 | 18 |
| web-app | CI | `pull_request` | 39 | 38 | 34 | 44 |
| data-pipeline | nightly | `schedule` | 7 | 7 | 7 | 5 |
| api-server | CI | `pull_request` | 32 | 28 | 35 | 22 |
| mobile-app | Build | `pull_request` | 3 | 10 | 10 | 6 |
| api-server | Deploy | `push` | 8 | 5 | 6 | 5 |
| web-app | CI | `push` | 8 | 9 | 5 | 11 |
| admin-console | CI | `pull_request` | 18 | 17 | 12 | 12 |
| infra | terraform-plan | `pull_request` | 9 | 4 | 5 | 3 |
| design-system | Delete merged branch | `pull_request` | 13 | 19 | 12 | 6 |

## 1回あたりの分数

| リポジトリ | ワークフロー | 起動のきっかけ | 10/12〜 | 10/19〜 | 10/26〜 | 11/2〜（途中） |
|---|---|---|--:|--:|--:|--:|
| web-app | e2e | `pull_request` | 9.6 | 9.7 | 9.4 | 9.3 |
| web-app | CI | `pull_request` | 3.9 | 4.1 | 4.3 | 4.1 |
| data-pipeline | nightly | `schedule` | 21.6 | 18.6 | 19.4 | 19.4 |
| api-server | CI | `pull_request` | 3.0 | 3.1 | 3.2 | 3.1 |
| mobile-app | Build | `pull_request` | 7.0 | 7.3 | 7.6 | 7.3 |
| api-server | Deploy | `push` | 6.5 | 6.0 | 7.2 | 6.4 |
| web-app | CI | `push` | 4.0 | 4.4 | 4.0 | 4.0 |
| admin-console | CI | `pull_request` | 2.1 | 2.1 | 2.0 | 2.0 |
| infra | terraform-plan | `pull_request` | 3.1 | 2.8 | 3.6 | 3.3 |
| design-system | Delete merged branch | `pull_request` | 1.0 | 1.0 | 1.0 | 1.0 |
