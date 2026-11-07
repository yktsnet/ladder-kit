#!/usr/bin/env python3
"""New Relic から Claude Code の利用状況を日本時間の1日単位で取り出し、data/<日付>.json に置く。"""

import argparse
import datetime as dt
import json
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
# New Relic の無料枠の保存期間（8日）に収め、取りこぼした日を次の実行で埋める
BACKFILL_DAYS = 7

METRICS = {
    "tokens": "sum(claude_code.token.usage)",
    # 人が操作していた時間（type = 'user'）はターミナルしか記録せず、VS Code 拡張と並べられないので数えない
    "active_seconds": "filter(sum(claude_code.active_time.total), WHERE type = 'cli')",
    "sessions": "sum(claude_code.session.count)",
    "cost_usd": "sum(claude_code.cost.usage)",
    "commits": "sum(claude_code.commit.count)",
    "pull_requests": "sum(claude_code.pull_request.count)",
    "lines_added": "filter(sum(claude_code.lines_of_code.count), WHERE type = 'added')",
    "lines_removed": "filter(sum(claude_code.lines_of_code.count), WHERE type = 'removed')",
}


def nerdgraph(key: str, query: str) -> dict:
    req = urllib.request.Request(
        "https://api.newrelic.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"API-Key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        body = json.load(res)
    if body.get("errors"):
        sys.exit(f"error: NerdGraph returned errors: {body['errors']}")
    return body["data"]


def query_day(
    key: str, account: int, day: dt.date, domain: str, select: str, facet: str, source: str = "Metric", where: str = ""
) -> list[dict]:
    # Team 以外のアカウント（試験に使った個人のアカウントなど）を混ぜない
    nrql = (
        f"FROM {source} SELECT {select} WHERE user.email LIKE '%@{domain}' {where} FACET {facet} "
        f"SINCE '{day} 00:00:00' UNTIL '{day + dt.timedelta(days=1)} 00:00:00' "
        f"WITH TIMEZONE 'Asia/Tokyo' LIMIT MAX"
    )
    query = f"{{ actor {{ account(id: {account}) {{ nrql(query: {json.dumps(nrql)}) {{ results }} }} }} }}"
    return nerdgraph(key, query)["actor"]["account"]["nrql"]["results"]


def github_search(token: str, q: str) -> list[dict]:
    items: list[dict] = []
    for page in range(1, 11):
        url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({"q": q, "per_page": 100, "page": page})
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                body = json.load(res)
        except urllib.error.HTTPError as e:
            # 422 は、トークンから組織のリポが見えないときにも返る。理由は本文にしか無い
            raise RuntimeError(f"GitHub search failed with HTTP {e.code}: {e.read().decode(errors='replace')}") from e
        # 検索の API は1分に30回までなので、続けて呼ぶときに間を空ける
        time.sleep(2.5)
        if body.get("incomplete_results"):
            sys.exit(f"error: GitHub search timed out and returned partial results: {q}")
        items += body["items"]
        if len(items) >= body["total_count"] or not body["items"]:
            break
    return items


def collect_issues(token: str, org: str, day: dt.date) -> dict:
    """その日に立てた Issue と、閉じられた Issue を、立てた人の GitHub アカウント別に数える。"""
    window = f"{day}T00:00:00+09:00..{day}T23:59:59+09:00"
    counts: dict[str, dict[str, int]] = {}
    for field, qualifier in (("opened", "created"), ("closed", "closed")):
        for item in github_search(token, f"org:{org} is:issue {qualifier}:{window}"):
            c = counts.setdefault(item["user"]["login"], {"opened": 0, "closed": 0})
            c[field] += 1
    return dict(sorted(counts.items()))


# 内訳ごとに (メトリクス, 値の名前, FACET する属性, 絞り込み) を持つ。FACET の先頭は常に user.email
BREAKDOWNS = {
    "entrypoints": ("claude_code.active_time.total", "active_seconds", ["app.entrypoint"], "AND type = 'cli'"),
    "active_by_type": ("claude_code.active_time.total", "active_seconds", ["type"], ""),
    "tokens_by_type": ("claude_code.token.usage", "tokens", ["type"], ""),
    "cost_by_model": ("claude_code.cost.usage", "cost_usd", ["model", "effort", "query_source"], ""),
}


def attr(v: object) -> str:
    # 属性の無い記録は、NRQL が null か "(null)" で返す。effort はモデルが対応しないと付かない
    return "none" if v in (None, "(null)", "") else str(v)


def collect_day(key: str, account: int, day: dt.date, domain: str) -> dict:
    select = ", ".join(f"{expr} AS {name}" for name, expr in METRICS.items())
    members = {}
    for row in query_day(key, account, day, domain, select, "user.email"):
        values = {name: row.get(name) or 0 for name in METRICS}
        members[row["user.email"]] = {
            name: round(v, 4) if name == "cost_usd" else round(v) for name, v in values.items()
        }
    for field, (metric, alias, facets, where) in BREAKDOWNS.items():
        for m in members.values():
            m[field] = [] if len(facets) > 1 else {}
        select = f"sum({metric}) AS {alias}"
        for row in query_day(key, account, day, domain, select, ", ".join(["user.email", *facets]), where=where):
            email, *keys = row["facet"]
            v = row.get(alias) or 0
            v = round(v, 4) if alias == "cost_usd" else round(v)
            if email not in members or not v:
                continue
            if len(facets) > 1:
                members[email][field].append({**{f: attr(k) for f, k in zip(facets, keys)}, alias: v})
            else:
                bucket = members[email][field]
                bucket[attr(keys[0])] = bucket.get(attr(keys[0]), 0) + v
    # スキルの回数はメトリクスに無く、ログの skill_activated イベントにしか残らない。
    # ログが1件も届いていない人は、使わなかったのではなく送信設定がログを送っていないので None にする
    logged = {
        row["user.email"]
        for row in query_day(key, account, day, domain, "count(*) AS count", "user.email", source="Log")
        if row.get("count")
    }
    for email, m in members.items():
        m["skills"] = {} if email in logged else None
    rows = query_day(
        key, account, day, domain, "count(*) AS count", "user.email, skill.name",
        source="Log", where="AND event.name = 'skill_activated'",
    )
    for row in rows:
        email, skill = row["facet"]
        if email in members and members[email]["skills"] is not None and row.get("count"):
            members[email]["skills"][attr(skill)] = row["count"]
    return {"date": day.isoformat(), "members": dict(sorted(members.items()))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily Claude Code usage from New Relic.")
    parser.add_argument("--date", type=dt.date.fromisoformat, help="fetch only this JST date (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="overwrite files that already exist")
    args = parser.parse_args()

    key = os.environ.get("NEW_RELIC_USER_KEY") or sys.exit("error: NEW_RELIC_USER_KEY is not set")
    # New Relic は自動で保存用のアカウントも作るので、ID は推測せずに指定させる
    account = int(os.environ.get("NEW_RELIC_ACCOUNT_ID") or sys.exit("error: NEW_RELIC_ACCOUNT_ID is not set"))
    # Team のアカウントのメールアドレスのドメイン。試験に使った個人のアカウントなどを混ぜない
    domain = os.environ.get("EMAIL_DOMAIN") or sys.exit("error: EMAIL_DOMAIN is not set")

    yesterday = dt.datetime.now(JST).date() - dt.timedelta(days=1)
    backfill = [yesterday - dt.timedelta(days=i) for i in range(BACKFILL_DAYS)]
    # 土日分は表にも図にも出さないので取らない
    days = [args.date] if args.date else [d for d in backfill if d.weekday() < 5]

    DATA_DIR.mkdir(exist_ok=True)
    for day in sorted(days):
        path = DATA_DIR / f"{day}.json"
        if path.exists() and not args.force:
            continue
        data = collect_day(key, account, day, domain)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {path.name} ({len(data['members'])} members)")

    token = os.environ.get("ORG_READ_TOKEN")
    if not token:
        print("ORG_READ_TOKEN is not set. Skipping issue counts.")
        return
    org = os.environ.get("GITHUB_ORG") or sys.exit("error: GITHUB_ORG is not set")
    # GitHub の記録は消えないので、Issue の数が無い日は New Relic の保存期間に関係なく遡って埋める
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        day = dt.date.fromisoformat(data["date"])
        if day.weekday() >= 5 or ("issues" in data and not (args.force and day == args.date)):
            continue
        try:
            data["issues"] = collect_issues(token, org, day)
        except RuntimeError as e:
            # New Relic の分は書き終えているので、表の作り直しとコミットは続けさせる（usage.yml）
            print(f"::error::{e}")
            sys.exit(1)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote issue counts to {path.name} ({len(data['issues'])} accounts)")


if __name__ == "__main__":
    main()
