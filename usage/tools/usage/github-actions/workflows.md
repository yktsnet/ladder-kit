# ワークフロー別の週ごとの分数

<!-- render.py が作り直す。手で直さない -->

[README.md](README.md) の分数が増えたときに、何が増えたかをここで見る。直近4週の分数の多い順に、上位 10 件のワークフローを並べる。週は月曜に始まる。

分数が増えたワークフローについて、回数が増えたのか、1回あたりの分数が増えたのかを下の2つの表で見分ける。

最終更新：2026-04-24 分まで

## 分数

| リポジトリ | ワークフロー | 起動のきっかけ | 3/30〜 | 4/6〜 | 4/13〜 | 4/20〜（途中） |
|---|---|---|--:|--:|--:|--:|
| web-app | CI | `pull_request` | 116 | 150 | 157 | 136 |
| data-pipeline | nightly | `schedule` | 150 | 138 | 135 | 89 |
| web-app | e2e | `pull_request` | 104 | 191 | 117 | 96 |
| api-server | CI | `pull_request` | 54 | 63 | 88 | 73 |
| mobile-app | Build | `pull_request` | 47 | 46 | 83 | 45 |
| web-app | CI | `push` | 59 | 55 | 50 | 25 |
| api-server | Deploy | `push` | 51 | 39 | 24 | 29 |
| admin-console | CI | `pull_request` | 19 | 22 | 40 | 4 |
| infra | terraform-plan | `pull_request` | 24 | 11 | 15 | 27 |
| design-system | Delete merged branch | `pull_request` | 16 | 14 | 20 | 16 |

## 回数

| リポジトリ | ワークフロー | 起動のきっかけ | 3/30〜 | 4/6〜 | 4/13〜 | 4/20〜（途中） |
|---|---|---|--:|--:|--:|--:|
| web-app | CI | `pull_request` | 28 | 36 | 37 | 32 |
| data-pipeline | nightly | `schedule` | 7 | 7 | 7 | 5 |
| web-app | e2e | `pull_request` | 11 | 20 | 12 | 10 |
| api-server | CI | `pull_request` | 17 | 21 | 28 | 23 |
| mobile-app | Build | `pull_request` | 6 | 6 | 11 | 6 |
| web-app | CI | `push` | 14 | 14 | 12 | 6 |
| api-server | Deploy | `push` | 7 | 6 | 4 | 4 |
| admin-console | CI | `pull_request` | 9 | 10 | 19 | 2 |
| infra | terraform-plan | `pull_request` | 7 | 4 | 5 | 8 |
| design-system | Delete merged branch | `pull_request` | 16 | 14 | 20 | 16 |

## 1回あたりの分数

| リポジトリ | ワークフロー | 起動のきっかけ | 3/30〜 | 4/6〜 | 4/13〜 | 4/20〜（途中） |
|---|---|---|--:|--:|--:|--:|
| web-app | CI | `pull_request` | 4.1 | 4.2 | 4.2 | 4.2 |
| data-pipeline | nightly | `schedule` | 21.4 | 19.7 | 19.3 | 17.8 |
| web-app | e2e | `pull_request` | 9.5 | 9.6 | 9.8 | 9.6 |
| api-server | CI | `pull_request` | 3.2 | 3.0 | 3.1 | 3.2 |
| mobile-app | Build | `pull_request` | 7.8 | 7.7 | 7.5 | 7.5 |
| web-app | CI | `push` | 4.2 | 3.9 | 4.2 | 4.2 |
| api-server | Deploy | `push` | 7.3 | 6.5 | 6.0 | 7.2 |
| admin-console | CI | `pull_request` | 2.1 | 2.2 | 2.1 | 2.0 |
| infra | terraform-plan | `pull_request` | 3.4 | 2.8 | 3.0 | 3.4 |
| design-system | Delete merged branch | `pull_request` | 1.0 | 1.0 | 1.0 | 1.0 |
