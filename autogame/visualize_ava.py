#!/usr/bin/env python3
"""AVA 对战结果可视化：CSV → HTML (Chart.js)"""

import csv
from collections import defaultdict
from pathlib import Path

CSV_PATH = Path(__file__).parent / "ava_results.csv"
OUT_PATH = Path(__file__).parent / "ava_report.html"


def load_matches(csv_path: Path) -> dict[str, list[dict]]:
    matches: dict[str, list[dict]] = defaultdict(list)
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            matches[row["match_id"]].append(row)
    return matches


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


def render_html(matches: dict[str, list[dict]]) -> str:
    import json

    sections = []
    for i, (match_id, events) in enumerate(matches.items()):
        strat_a = events[0]["strategy_a"]
        strat_b = events[0]["strategy_b"]
        chart_data = build_chart_data(events)
        summary = compute_summary(events)

        winner_label = f"策略 {strat_a}" if summary["winner"] == "A" else f"策略 {strat_b}" if summary["winner"] == "B" else "平局"

        summary_html = (
            f'<div class="summary">'
            f'<p><b>比分交换领先次数:</b> {summary["lead_changes"]}</p>'
            f'<p><b>Factory 易手次数:</b> {summary["factory_captures"]}</p>'
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
        const ctx = document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx, {{
          type: 'line',
          data: {{
            labels: d.times.map(t => (t/60).toFixed(1) + 'm'),
            datasets: [
              {{
                label: '{strat_a} (A)',
                data: d.scores_a,
                borderColor: '#2563eb',
                backgroundColor: '#2563eb22',
                tension: 0.2,
                pointRadius: d.pr_a,
                pointStyle: d.ps_a,
                pointBackgroundColor: '#2563eb',
              }},
              {{
                label: '{strat_b} (B)',
                data: d.scores_b,
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
              x: {{ title: {{ display: true, text: '时间 (分钟)' }} }},
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
  </style>
</head>
<body>
  <h1>AVA 对战结果可视化</h1>
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
