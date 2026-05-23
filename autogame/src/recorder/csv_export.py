"""JSONL 事件文件 → CSV 追加导出"""

import csv
import json
from pathlib import Path

CSV_COLUMNS = [
    "match_id", "event_type", "iso_time", "elapsed_sec", "loop_seq",
    "strategy_a", "strategy_b", "score_a", "score_b",
    "leader", "factory_owner", "detail",
]


def export_events_to_csv(events_path: str, csv_path: str) -> int:
    """读取 JSONL 事件文件，追加到 CSV。不存在则创建含表头。返回追加行数。"""
    csv_file = Path(csv_path)
    write_header = not csv_file.exists() or csv_file.stat().st_size == 0

    events = []
    with open(events_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))

    if not events:
        return 0

    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for event in events:
            writer.writerow(event)

    return len(events)
