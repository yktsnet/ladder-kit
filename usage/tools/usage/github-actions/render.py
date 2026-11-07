#!/usr/bin/env python3
"""data/ の日ごとの分数から、README.md の表、workflows.md、charts/ のグラフを作り直す。"""

import calendar
import datetime as dt
import json
import math
import re
import sys
from collections.abc import Sequence
from html import escape
from pathlib import Path

# 集計のディレクトリから直接実行するので、共通の部品がある親を import の探索先に足す
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart import nice_max, spread, svg  # noqa: E402

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
CHART_DIR = ROOT / "charts"
README = ROOT / "README.md"
WORKFLOWS = ROOT / "workflows.md"
# 組織のプランの無料枠（GitHub Free は 2,000 分、Team は 3,000 分）
FREE_MINUTES = 2000
# 高いほうの単価で割る理由は docs/metrics.md にある
USD_PER_MINUTE = 0.008
# 超過額の段。最後の段が予算なので、組織の予算に合わせる
TIERS_USD = [0, 5, 10, 15]
PACE_DAYS = 7
DAILY_DAYS = 28
WEEKS = 4
TOP_WORKFLOWS = 10


def load() -> dict[dt.date, dict]:
    days = {}
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        days[dt.date.fromisoformat(data["date"])] = data
    return days


def total(day: dict | None, repo: str | None = None) -> int:
    if not day:
        return 0
    return sum(r["minutes"] for name, rows in day["repos"].items() if repo in (None, name) for r in rows)


class Plot:
    # GitHub は画像を本文の幅まで縮めるが、広げはしない。文字が縮まずに読める大きさで描く
    width, left, right, top, plot_h = 880, 64, 190, 24, 300

    def __init__(self, n: int, peak: float):
        self.n, self.peak = n, nice_max(peak)
        self.plot_w = self.width - self.left - self.right
        self.height = self.top + self.plot_h + 44
        self.step = self.plot_w / max(n - 1, 1)
        self.body: list[str] = []
        # 線の名前と目安線の名前を、右端に1列で並べる
        self.ends: list[tuple[str, str, float]] = []
        for frac in (0, 0.25, 0.5, 0.75, 1):
            y = self.top + self.plot_h * (1 - frac)
            self.body += [
                f'<line class="grid" x1="{self.left}" y1="{y:.1f}" x2="{self.left + self.plot_w}" y2="{y:.1f}"/>',
                f'<text class="muted" x="{self.left - 8}" y="{y + 4:.1f}" text-anchor="end">{self.peak * frac:,.0f}</text>',
            ]

    def x(self, i: float) -> float:
        return self.left + i * self.step

    def y(self, v: float) -> float:
        return self.top + self.plot_h * (1 - v / self.peak)

    def x_labels(self, labels: list[str]) -> None:
        for i, label in enumerate(labels):
            if label:
                self.body.append(f'<text class="muted" x="{self.x(i):.1f}" y="{self.top + self.plot_h + 22}" text-anchor="middle">{label}</text>')

    def line(self, values: Sequence[float], cls: str, label: str, xs: Sequence[int] | None = None,
             dots: bool = True, extra: str = "") -> None:
        pts = [(self.x(xs[i] if xs else i), self.y(v)) for i, v in enumerate(values)]
        self.body.append(f'<polyline class="line {cls} {extra}" style="fill: none" points="'
                         + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
        if dots:
            self.body += [f'<circle class="dot {cls}" cx="{x:.1f}" cy="{y:.1f}" r="3"/>' for x, y in pts]
        if label:
            self.ends.append((label, cls, pts[-1][1]))

    def limit(self, v: float, label: str) -> None:
        y = self.y(v)
        self.body.append(f'<line class="limit" x1="{self.left}" y1="{y:.1f}" x2="{self.left + self.plot_w}" y2="{y:.1f}"/>')
        self.ends.append((label, "limit", y))

    def render(self) -> str:
        for (label, cls, _), ly in zip(self.ends, spread([y for *_, y in self.ends], 16, self.top, self.top + self.plot_h)):
            x = self.left + self.plot_w + 12
            text_cls = "limit-text" if cls == "limit" else "label"
            self.body += [
                f'<line class="line {cls}" x1="{x}" y1="{ly:.1f}" x2="{x + 10}" y2="{ly:.1f}"/>',
                f'<text class="{text_cls}" x="{x + 16}" y="{ly + 4:.1f}">{escape(label)}</text>',
            ]
        return svg(self.width, self.height, self.body)


def tier_minutes(usd: int) -> int:
    return FREE_MINUTES + round(usd / USD_PER_MINUTE)


def tier_name(usd: int) -> str:
    return "無料枠" if usd == 0 else f"{usd}ドル" + ("（予算）" if usd == TIERS_USD[-1] else "")


def cumulative(by_date: dict[dt.date, dict], first: dt.date, last: dt.date) -> list[int]:
    out, acc = [], 0
    for i in range((last - first).days + 1):
        acc += total(by_date.get(first + dt.timedelta(days=i)))
        out.append(acc)
    return out


def month_chart(this: list[int], projected: float, month_days: int, month: dt.date) -> str:
    p = Plot(month_days, max(tier_minutes(TIERS_USD[-1]), projected, *this) * 1.05)
    p.x_labels([f"{month.month}/{d}" if d == 1 else (str(d) if d % 5 == 0 else "") for d in range(1, month_days + 1)])
    for usd in TIERS_USD:
        p.limit(tier_minutes(usd), f"{tier_name(usd)} {tier_minutes(usd):,}")
    if len(this) < month_days:
        p.line([this[-1], projected], "s0", "", xs=[len(this) - 1, month_days - 1], dots=False, extra="dash")
    p.line(this, "s0", "累計")
    return p.render()


def daily_chart(span: list[dt.date], by_date: dict[dt.date, dict], month_days: int) -> str:
    daily = [total(by_date.get(d)) for d in span]
    avg = [sum(daily[max(0, i - PACE_DAYS + 1):i + 1]) / len(daily[max(0, i - PACE_DAYS + 1):i + 1]) for i in range(len(span))]
    p = Plot(len(span), max([*daily, tier_minutes(TIERS_USD[-1]) / month_days]) * 1.05)
    p.x_labels([f"{d.month}/{d.day}" if i == 0 or d.day == 1 else (str(d.day) if d.weekday() == 0 else "")
                for i, d in enumerate(span)])
    # 月の分数を暦日で割る。課金は土日も含めた月の合計で決まる
    for usd in TIERS_USD:
        p.limit(tier_minutes(usd) / month_days, f"{tier_name(usd)} {tier_minutes(usd) / month_days:.0f}")
    p.line(daily, "other", "当日")
    p.line(avg, "s0", f"直近{PACE_DAYS}日の平均", dots=False)
    return p.render()


def day_reaching(done: int, pace: float, limit: int, today: dt.date, month_end: dt.date) -> str:
    if done >= limit:
        return "超えた"
    if pace <= 0:
        return "届かない"
    reach = today + dt.timedelta(days=math.ceil((limit - done) / pace))
    return f"{reach.month}/{reach.day}" if reach <= month_end else "届かない"


def workflows_page(by_date: dict[dt.date, dict], last: dt.date) -> str:
    # 週は月曜始まり。最後の週は途中までになる
    monday = last - dt.timedelta(days=last.weekday())
    weeks = [monday - dt.timedelta(weeks=WEEKS - 1 - i) for i in range(WEEKS)]
    sums: dict[tuple[str, str, str], list[dict[str, int]]] = {}
    for d, day in by_date.items():
        if d < weeks[0]:
            continue
        w = (d - weeks[0]).days // 7
        for repo, rows in day["repos"].items():
            for r in rows:
                cells = sums.setdefault((repo, r["workflow"], r["event"]), [{"runs": 0, "minutes": 0} for _ in weeks])
                cells[w]["runs"] += r["runs"]
                cells[w]["minutes"] += r["minutes"]
    top = sorted(sums.items(), key=lambda kv: -sum(c["minutes"] for c in kv[1]))[:TOP_WORKFLOWS]
    heads = [f"{w.month}/{w.day}〜" + ("（途中）" if w == monday and last.weekday() < 6 else "") for w in weeks]

    def table(cell) -> str:
        lines = ["| リポジトリ | ワークフロー | 起動のきっかけ | " + " | ".join(heads) + " |",
                 "|---|---|---|" + "--:|" * len(weeks)]
        for (repo, wf, event), cells in top:
            lines.append(f"| {repo} | {wf} | `{event}` | " + " | ".join(cell(c) for c in cells) + " |")
        return "\n".join(lines)

    return "\n".join([
        "# ワークフロー別の週ごとの分数",
        "",
        "<!-- render.py が作り直す。手で直さない -->",
        "",
        f"[README.md](README.md) の分数が増えたときに、何が増えたかをここで見る。直近{WEEKS}週の分数の多い順に、"
        f"上位 {TOP_WORKFLOWS} 件のワークフローを並べる。週は月曜に始まる。",
        "",
        "分数が増えたワークフローについて、回数が増えたのか、1回あたりの分数が増えたのかを下の2つの表で見分ける。",
        "",
        f"最終更新：{last} 分まで",
        "",
        "## 分数",
        "",
        table(lambda c: str(c["minutes"])),
        "",
        "## 回数",
        "",
        table(lambda c: str(c["runs"])),
        "",
        "## 1回あたりの分数",
        "",
        table(lambda c: f"{c['minutes'] / c['runs']:.1f}" if c["runs"] else "—"),
    ]) + "\n"


def main() -> None:
    by_date = load()
    if not by_date:
        print("No data yet. Nothing to render.")
        return
    last = max(by_date)
    month = last.replace(day=1)
    month_days = calendar.monthrange(last.year, last.month)[1]
    month_end = month.replace(day=month_days)

    this = cumulative(by_date, month, last)
    # 先月の末にまたがって平均すると、月替わりに入れた削減が見込みに出ない。月初は今月の日数だけで割る
    pace_from = max(month, last - dt.timedelta(days=PACE_DAYS - 1))
    pace_days = (last - pace_from).days + 1
    pace = sum(total(by_date.get(pace_from + dt.timedelta(days=i))) for i in range(pace_days)) / pace_days
    projected = this[-1] + pace * (month_days - last.day)
    over = max(0, projected - FREE_MINUTES)

    span = [last - dt.timedelta(days=DAILY_DAYS - 1 - i) for i in range(DAILY_DAYS)]
    span = [d for d in span if d >= min(by_date)]
    CHART_DIR.mkdir(exist_ok=True)
    (CHART_DIR / "month.svg").write_text(month_chart(this, projected, month_days, month))
    (CHART_DIR / "daily.svg").write_text(daily_chart(span, by_date, month_days))
    WORKFLOWS.write_text(workflows_page(by_date, last))

    tier_lines = ["| 段 | 月の分数 | 1日あたり | 届く日の見込み |", "|---|--:|--:|--:|"]
    for usd in TIERS_USD:
        m = tier_minutes(usd)
        tier_lines.append(f"| {tier_name(usd)} | {m:,} | {m / month_days:.0f} | {day_reaching(this[-1], pace, m, last, month_end)} |")

    unreadable = sorted({r for d, day in by_date.items() if d >= month for r in day.get("unreadable", [])})
    warning = [
        f"> [!WARNING]\n> 次のリポジトリは、今月の一部の日の実行記録を token で読めなかった。その日の分は、前に取れていた分のままか 0 分である："
        f"{'、'.join(unreadable)}。直し方は [docs/setup.md](docs/setup.md#読めないリポジトリがあるとき) にある。",
        "",
    ] if unreadable else []
    report = "\n".join([
        f"最終更新：{last} 分まで",
        "",
        *warning,
        "### 今月の見込み",
        "",
        f"{month.month}/1 からの累計は **{this[-1]:,} 分**、今月の直近{pace_days}日の1日平均は **{pace:,.0f} 分**である。"
        f"このペースだと月末は約 {projected:,.0f} 分で、無料枠を超えた分は最大で {over * USD_PER_MINUTE:.1f} ドルになる。",
        "",
        "段は、無料枠を超えた額で区切った月の分数の目安である。",
        "",
        "\n".join(tier_lines),
        "",
        "### 日ごとの分数",
        "",
        f"直近{DAILY_DAYS}日。点線は段ごとの1日あたりの目安である。"
        f"土日はほとんど使わないので、目安とは直近{PACE_DAYS}日の平均の線を比べる。",
        "",
        "![日ごとの分数](charts/daily.svg)",
        "",
        f"### {month.month}月の累計",
        "",
        "破線は、今月の1日平均で月末まで伸ばした見込みである。",
        "",
        f"![{month.month}月の累計の分数](charts/month.svg)",
    ])
    text = README.read_text()
    text = re.sub(r"(<!-- report:start -->\n).*?(<!-- report:end -->)", lambda m: m[1] + report + "\n" + m[2], text, flags=re.S)
    README.write_text(text)
    print(f"Rendered {len(by_date)} days up to {last}")


if __name__ == "__main__":
    main()
