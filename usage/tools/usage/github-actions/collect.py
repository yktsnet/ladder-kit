#!/usr/bin/env python3
"""組織の private リポの GitHub Actions の実行記録から、日ごとの分数を data/<日付>.json に置く。"""

import argparse
import concurrent.futures
import datetime as dt
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
DATA_DIR = Path(__file__).parent / "data"
# 1:00 JST に前日分を取ると、日付の変わり目に走っていた run がまだ終わっていない。
# 日曜と月曜は実行しないので、火曜の実行が金曜の分まで取り直せる日数にする
REFRESH_DAYS = 4
# 無料枠の分数は OS ごとの倍率を掛けて減る
OS_MULTIPLIER = {"windows": 2, "macos": 10}


class Unreadable(Exception):
    """token の権限か見える範囲が足りず、リポの記録を読めない。"""


def get(token: str, path: str, params: dict | None = None) -> dict:
    url = f"https://api.github.com/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    # 千回単位で呼ぶので、途中で切れた接続や 5xx はやり直す
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                return json.load(res)
        except urllib.error.HTTPError as e:
            # 回数の上限も 403 で返るので、権限の不足と分けて止める
            if e.code in (403, 404) and e.headers.get("x-ratelimit-remaining") != "0":
                raise Unreadable(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e
            if e.code < 500 or attempt == 3:
                sys.exit(f"error: GET {path} failed with HTTP {e.code}: {e.read().decode(errors='replace')}")
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def paged(token: str, path: str, key: str | None, params: dict | None = None) -> list[dict]:
    items: list[dict] = []
    for page in range(1, 100):
        body = get(token, path, {**(params or {}), "per_page": 100, "page": page})
        batch = body[key] if key else body
        items += batch
        if len(batch) < 100:
            break
    return items


def private_repos(token: str, org: str) -> list[str]:
    # public リポの Actions は課金されないので数えない
    repos = paged(token, f"orgs/{org}/repos", None, {"type": "all"})
    return sorted(r["name"] for r in repos if r["visibility"] != "public")


def job_minutes(job: dict) -> int:
    # self-hosted runner の分は課金されない
    if job.get("runner_group_name") not in (None, "GitHub Actions") or "self-hosted" in job.get("labels", []):
        return 0
    if not job.get("started_at") or not job.get("completed_at"):
        return 0
    seconds = (dt.datetime.fromisoformat(job["completed_at"]) - dt.datetime.fromisoformat(job["started_at"])).total_seconds()
    if seconds <= 0:
        return 0
    labels = " ".join(job.get("labels", [])).lower()
    multiplier = next((m for os_name, m in OS_MULTIPLIER.items() if os_name in labels), 1)
    # Billing と同じく、ジョブ1つごとに1分単位で切り上げる
    return math.ceil(seconds / 60) * multiplier


def collect_day(token: str, org: str, repos: list[str], day: dt.date, previous: dict | None) -> dict:
    rows: dict[str, dict[tuple[str, str], dict[str, int]]] = {}
    runs = []
    unreadable = []
    for repo in repos:
        # 条件付きの一覧は 1,000 件までしか返らないので、1日ずつ取る
        window = f"{day}T00:00:00+09:00..{day}T23:59:59+09:00"
        try:
            runs += [(repo, run) for run in paged(token, f"repos/{org}/{repo}/actions/runs", "workflow_runs", {"created": window})]
        except Unreadable as e:
            print(f"warning: cannot read runs of {repo} for {day}: {e}", file=sys.stderr)
            unreadable.append(repo)

    def jobs_of(item):
        repo, run = item
        # filter=all で再実行した回のジョブも数える
        return item, paged(token, f"repos/{org}/{repo}/actions/runs/{run['id']}/jobs", "jobs", {"filter": "all"})

    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        for (repo, run), jobs in pool.map(jobs_of, runs):
            key = (run["name"], run["event"])
            row = rows.setdefault(repo, {}).setdefault(key, {"runs": 0, "minutes": 0})
            row["runs"] += 1
            row["minutes"] += sum(job_minutes(j) for j in jobs)
    result = {
        repo: sorted(
            ({"workflow": w, "event": e, **v} for (w, e), v in by_key.items()),
            key=lambda r: (-r["minutes"], r["workflow"], r["event"]),
        )
        for repo, by_key in rows.items()
    }
    # 読めなかったリポは、前に取れていた分を残す。0 分で上書きすると、読めた日の記録まで消える
    for repo in unreadable:
        if previous and repo in previous.get("repos", {}):
            result[repo] = previous["repos"][repo]
    return {"date": day.isoformat(), "unreadable": unreadable, "repos": dict(sorted(result.items()))}


def needs_fetch(path: Path) -> bool:
    if not path.exists():
        return True
    # unreadable が無いのは、全リポを読めたか確かめていない記録なので取り直す
    unreadable = json.loads(path.read_text()).get("unreadable")
    return unreadable is None or bool(unreadable)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily GitHub Actions minutes of the organization's private repositories.")
    parser.add_argument("--date", type=dt.date.fromisoformat, help="fetch only this JST date (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="overwrite files that already exist")
    args = parser.parse_args()

    token = os.environ.get("ORG_READ_TOKEN") or sys.exit("error: ORG_READ_TOKEN is not set")
    org = os.environ.get("GITHUB_ORG") or sys.exit("error: GITHUB_ORG is not set")
    yesterday = dt.datetime.now(JST).date() - dt.timedelta(days=1)
    # 実行の記録は消えないので、data/ に無い日はここまで遡って埋める。月の見込みと4週の表に足りる先月の1日を既定にする
    first_day = (dt.date.fromisoformat(os.environ["ACTIONS_FIRST_DAY"]) if os.environ.get("ACTIONS_FIRST_DAY")
                 else (yesterday.replace(day=1) - dt.timedelta(days=1)).replace(day=1))
    days = [args.date] if args.date else [
        first_day + dt.timedelta(days=i) for i in range((yesterday - first_day).days + 1)
    ]
    days = [d for d in days if args.force or (yesterday - d).days < REFRESH_DAYS or needs_fetch(DATA_DIR / f"{d}.json")]
    if not days:
        print("All days are already collected.")
        return

    repos = private_repos(token, org)
    DATA_DIR.mkdir(exist_ok=True)
    unreadable: set[str] = set()
    for day in days:
        path = DATA_DIR / f"{day}.json"
        previous = json.loads(path.read_text()) if path.exists() else None
        data = collect_day(token, org, repos, day, previous)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        unreadable.update(data["unreadable"])
        total = sum(r["minutes"] for rows in data["repos"].values() for r in rows)
        print(f"Wrote {day}.json ({total} minutes)")
    # 書けた分は反映させたいが、欠けていることはジョブの失敗で気づけるようにする
    if unreadable:
        sys.exit(f"error: could not read Actions runs of: {', '.join(sorted(unreadable))}. Grant Actions read access to the token.")


if __name__ == "__main__":
    main()
