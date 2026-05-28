#!/usr/bin/env python3
"""AVA 对战结果可视化：CSV → HTML (Chart.js)"""

import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent / "ava_results.csv"
OUT_PATH = Path(__file__).parent / "ava_report.html"


def load_matches(csv_path: Path) -> list[list[dict]]:
    """Load CSV and group into matches (MATCH_START to next MATCH_START)."""
    all_rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            all_rows.append(row)

    matches: list[list[dict]] = []
    current: list[dict] = []
    for row in all_rows:
        if row["event_type"] == "MATCH_START":
            if current:
                matches.append(current)
            current = [row]
        else:
            current.append(row)
    if current:
        matches.append(current)
    return matches


def compute_ratings(matches: list[list[dict]]) -> tuple[dict[str, float], dict[str, dict]]:
    """Compute Elo ratings and head-to-head matrix from match results."""
    ratings: dict[str, float] = {}
    h2h: dict[str, dict[str, dict[str, int]]] = {}

    end_events = []
    for match in matches:
        end_evt = next((e for e in match if e["event_type"] == "MATCH_END"), None)
        if end_evt:
            end_events.append(end_evt)

    end_events.sort(key=lambda e: e["iso_time"])

    for evt in end_events:
        a, b = evt["strategy_a"], evt["strategy_b"]
        for s in (a, b):
            if s not in ratings:
                ratings[s] = 1500.0
        if a not in h2h:
            h2h[a] = {}
        if b not in h2h:
            h2h[b] = {}
        if b not in h2h[a]:
            h2h[a][b] = {"W": 0, "L": 0, "D": 0}
        if a not in h2h[b]:
            h2h[b][a] = {"W": 0, "L": 0, "D": 0}

        winner = evt["leader"]
        if winner == "A":
            sa, sb = 1.0, 0.0
            h2h[a][b]["W"] += 1
            h2h[b][a]["L"] += 1
        elif winner == "B":
            sa, sb = 0.0, 1.0
            h2h[a][b]["L"] += 1
            h2h[b][a]["W"] += 1
        else:
            sa, sb = 0.5, 0.5
            h2h[a][b]["D"] += 1
            h2h[b][a]["D"] += 1

        ea = 1.0 / (1.0 + 10 ** ((ratings[b] - ratings[a]) / 400))
        eb = 1.0 - ea
        K = 32
        ratings[a] += K * (sa - ea)
        ratings[b] += K * (sb - eb)

    return ratings, h2h


def render_rating_section(ratings: dict[str, float], h2h: dict[str, dict]) -> str:
    """Render Elo rating table and head-to-head matrix as HTML."""
    strategies = sorted(ratings.keys(), key=lambda s: ratings[s], reverse=True)

    totals = {}
    for s in strategies:
        w = sum(rec["W"] for rec in h2h.get(s, {}).values())
        l = sum(rec["L"] for rec in h2h.get(s, {}).values())
        d = sum(rec["D"] for rec in h2h.get(s, {}).values())
        total = w + l + d
        totals[s] = {"W": w, "L": l, "D": d, "total": total, "rate": w / total if total else 0}

    rows_html = ""
    for rank, s in enumerate(strategies, 1):
        t = totals[s]
        rows_html += (
            f"<tr><td>{rank}</td><td><b>{s}</b></td>"
            f"<td>{ratings[s]:.0f}</td>"
            f"<td>{t['W']}</td><td>{t['L']}</td><td>{t['D']}</td>"
            f"<td>{t['rate']*100:.1f}%</td></tr>\n"
        )

    matrix_header = "<th></th>" + "".join(f"<th>{s}</th>" for s in strategies)
    matrix_rows = ""
    for s in strategies:
        cells = ""
        for opp in strategies:
            if s == opp:
                cells += "<td>-</td>"
            else:
                rec = h2h.get(s, {}).get(opp, {"W": 0, "L": 0, "D": 0})
                cells += f"<td>{rec['W']}-{rec['L']}-{rec['D']}</td>"
        matrix_rows += f"<tr><td><b>{s}</b></td>{cells}</tr>\n"

    return f"""
    <section>
      <h2>策略等级分 (Elo Rating)</h2>
      <table class="rating-table">
        <thead><tr><th>#</th><th>策略</th><th>Elo</th><th>胜</th><th>负</th><th>平</th><th>胜率</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
      <h3>对战矩阵 (W-L-D)</h3>
      <table class="matrix-table">
        <thead><tr>{matrix_header}</tr></thead>
        <tbody>{matrix_rows}</tbody>
      </table>
    </section>
"""


def compute_summary(events: list[dict]) -> dict:
    lead_changes = sum(1 for e in events if e["event_type"] == "LEAD_CHANGE")
    factory_captures = sum(1 for e in events if e["event_type"] == "FACTORY_CAPTURE")

    end_evt = next((e for e in events if e["event_type"] == "MATCH_END"), None)
    total_sec = float(end_evt["elapsed_sec"]) if end_evt else 0
    winner = end_evt["leader"] if end_evt else "TIE"

    winner_lead_sec = 0.0
    prev_time = 0.0
    prev_leader = "TIE"
    for e in events:
        t = float(e["elapsed_sec"])
        if prev_leader == winner:
            winner_lead_sec += t - prev_time
        prev_time = t
        prev_leader = e["leader"]
    if prev_leader == winner and total_sec > prev_time:
        winner_lead_sec += total_sec - prev_time

    pct = (winner_lead_sec / total_sec * 100) if total_sec > 0 else 0
    return {
        "lead_changes": lead_changes,
        "factory_captures": factory_captures,
        "winner": winner,
        "winner_lead_pct": pct,
    }


def build_chart_data(events: list[dict]) -> dict:
    times, scores_a, scores_b = [], [], []
    point_radius_a, point_radius_b = [], []
    point_style_a, point_style_b = [], []

    for e in events:
        t = float(e["elapsed_sec"])
        sa, sb = int(e["score_a"]), int(e["score_b"])
        times.append(t)
        scores_a.append(sa)
        scores_b.append(sb)

        is_factory = e["event_type"] == "FACTORY_CAPTURE"
        detail = e.get("detail", "")
        factory_to_a = is_factory and ("-> A" in detail or "-> a" in detail)
        factory_to_b = is_factory and ("-> B" in detail or "-> b" in detail)

        point_radius_a.append(8 if factory_to_a else 0)
        point_style_a.append("star" if factory_to_a else "circle")
        point_radius_b.append(8 if factory_to_b else 0)
        point_style_b.append("star" if factory_to_b else "circle")

    return {
        "times": times,
        "scores_a": scores_a,
        "scores_b": scores_b,
        "pr_a": point_radius_a,
        "ps_a": point_style_a,
        "pr_b": point_radius_b,
        "ps_b": point_style_b,
    }


def render_html(matches: list[list[dict]]) -> str:
    import json

    ratings, h2h = compute_ratings(matches)
    rating_html = render_rating_section(ratings, h2h)

    sections = []
    for i, events in enumerate(matches):
        match_id = events[0]["match_id"]
        strat_a = events[0]["strategy_a"]
        strat_b = events[0]["strategy_b"]
        chart_data = build_chart_data(events)
        summary = compute_summary(events)

        winner_label = f"策略 {strat_a}" if summary["winner"] == "A" else f"策略 {strat_b}" if summary["winner"] == "B" else "平局"

        summary_html = (
            f'<div class="summary">'
            f'<p><b>比分交换领先次数:</b> {summary["lead_changes"]}</p>'
            f'<p><b>Factory 易手次数(*号):</b> {summary["factory_captures"]}</p>'
            f'<p><b>最终胜方 ({winner_label}) 领先时间占比:</b> {summary["winner_lead_pct"]:.1f}%</p>'
            f'</div>'
        )

        chart_id = f"chart_{i}"
        chart_js = json.dumps(chart_data)

        sections.append(f"""
    <section>
      <h2>{match_id} — {strat_a} vs {strat_b}</h2>
      <canvas id="{chart_id}" height="100"></canvas>
      {summary_html}
      <script>
      (function() {{
        const d = {chart_js};
        const minutes = d.times.map(t => t / 60);
        const dataA = minutes.map((m, i) => ({{x: m, y: d.scores_a[i]}}));
        const dataB = minutes.map((m, i) => ({{x: m, y: d.scores_b[i]}}));
        const ctx = document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx, {{
          type: 'line',
          data: {{
            datasets: [
              {{
                label: '{strat_a} (A)',
                data: dataA,
                borderColor: '#2563eb',
                backgroundColor: '#2563eb22',
                tension: 0.2,
                pointRadius: d.pr_a,
                pointStyle: d.ps_a,
                pointBackgroundColor: '#2563eb',
              }},
              {{
                label: '{strat_b} (B)',
                data: dataB,
                borderColor: '#dc2626',
                backgroundColor: '#dc262622',
                tension: 0.2,
                pointRadius: d.pr_b,
                pointStyle: d.ps_b,
                pointBackgroundColor: '#dc2626',
              }}
            ]
          }},
          options: {{
            responsive: true,
            plugins: {{
              title: {{ display: true, text: '{strat_a} vs {strat_b}' }},
              tooltip: {{ mode: 'index', intersect: false }}
            }},
            scales: {{
              x: {{
                type: 'linear',
                title: {{ display: true, text: '时间 (分钟)' }},
                ticks: {{ stepSize: 1, callback: v => v + 'm' }}
              }},
              y: {{ title: {{ display: true, text: '积分' }}, beginAtZero: true }}
            }}
          }}
        }});
      }})();
      </script>
    </section>
""")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>AVA 对战结果可视化</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f8fafc; }}
    h1 {{ color: #1e293b; }}
    section {{ background: white; border-radius: 12px; padding: 24px; margin: 24px 0; box-shadow: 0 2px 8px #0001; }}
    h2 {{ color: #334155; margin-top: 0; }}
    .summary {{ margin-top: 16px; padding: 12px 16px; background: #f1f5f9; border-radius: 8px; }}
    .summary p {{ margin: 4px 0; }}
    .rating-table, .matrix-table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
    .rating-table th, .rating-table td, .matrix-table th, .matrix-table td {{ border: 1px solid #e2e8f0; padding: 8px 12px; text-align: center; }}
    .rating-table thead, .matrix-table thead {{ background: #e2e8f0; }}
    .rating-table tbody tr:nth-child(odd) {{ background: #f8fafc; }}
  </style>
</head>
<body>
  <h1>AVA 对战结果可视化</h1>
  {rating_html}
  {''.join(sections)}
</body>
</html>"""


def main():
    matches = load_matches(CSV_PATH)
    html = render_html(matches)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Generated: {OUT_PATH} ({len(matches)} match(es))")


if __name__ == "__main__":
    main()
