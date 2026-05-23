"""AVA 对战观察者 — 通过独立进程调用获取积分，检测关键事件并写入 JSONL

设计：每次 poll 都是一个独立的 CLI 调用（和 get_ava_score 完全相同的代码路径），
避免长驻进程中 API 返回空数据的问题。
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STEAM_FACTORY_KEY = 10103


@dataclass
class PollState:
    timestamp: datetime
    elapsed_sec: float
    loop_seq: int
    score_a: int
    score_b: int
    factory_owner: str  # "A" | "B" | "NEUTRAL"


@dataclass
class MatchEvent:
    match_id: str
    event_type: str
    iso_time: str
    elapsed_sec: float
    loop_seq: int
    strategy_a: str
    strategy_b: str
    score_a: int
    score_b: int
    leader: str
    factory_owner: str
    detail: str


def _determine_leader(score_a: int, score_b: int) -> str:
    if score_a > score_b:
        return "A"
    elif score_b > score_a:
        return "B"
    return "TIE"


def _write_event(output_path: Path, event: MatchEvent) -> None:
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def detect_events(prev_state_file: str, curr_score_a: int, curr_score_b: int,
                  curr_factory_owner: str, elapsed_sec: float, loop_seq: int,
                  strategy_a: str, strategy_b: str, match_id: str,
                  output_path: str) -> None:
    """单次调用：对比前一状态，检测事件，写入 JSONL，更新状态文件。

    由 shell 脚本每次 poll 时作为独立进程调用。
    """
    out = Path(output_path)
    state_file = Path(prev_state_file)
    now = datetime.now(timezone.utc)

    curr = PollState(
        timestamp=now,
        elapsed_sec=elapsed_sec,
        loop_seq=loop_seq,
        score_a=curr_score_a,
        score_b=curr_score_b,
        factory_owner=curr_factory_owner,
    )

    # 读取前一状态
    prev: Optional[PollState] = None
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            prev = PollState(
                timestamp=datetime.fromisoformat(data["timestamp"]),
                elapsed_sec=data["elapsed_sec"],
                loop_seq=data["loop_seq"],
                score_a=data["score_a"],
                score_b=data["score_b"],
                factory_owner=data["factory_owner"],
            )
        except (json.JSONDecodeError, KeyError):
            pass

    # 检测事件
    events: list[MatchEvent] = []
    if prev is None:
        events.append(_make_event(curr, "MATCH_START", "match started",
                                  strategy_a, strategy_b, match_id))
    else:
        prev_leader = _determine_leader(prev.score_a, prev.score_b)
        curr_leader = _determine_leader(curr.score_a, curr.score_b)

        if curr_leader != prev_leader and curr_leader != "TIE":
            loser = "B" if curr_leader == "A" else "A"
            diff = abs(curr.score_a - curr.score_b)
            detail = f"{curr_leader} overtakes {loser} (+{diff})"
            events.append(_make_event(curr, "LEAD_CHANGE", detail,
                                      strategy_a, strategy_b, match_id))

        if curr.factory_owner != prev.factory_owner and curr.factory_owner != "NEUTRAL":
            prev_own = prev.factory_owner.lower() if prev.factory_owner != "NEUTRAL" else "neutral"
            detail = f"Factory: {prev_own} -> {curr.factory_owner}"
            events.append(_make_event(curr, "FACTORY_CAPTURE", detail,
                                      strategy_a, strategy_b, match_id))

    # 写入事件
    for ev in events:
        _write_event(out, ev)
        print(f"[observer] {ev.event_type}: {ev.detail} (A={ev.score_a} B={ev.score_b})")

    # 保存当前状态
    state_file.write_text(json.dumps({
        "timestamp": now.isoformat(),
        "elapsed_sec": elapsed_sec,
        "loop_seq": loop_seq,
        "score_a": curr_score_a,
        "score_b": curr_score_b,
        "factory_owner": curr_factory_owner,
    }), encoding="utf-8")


def write_match_end(prev_state_file: str, strategy_a: str, strategy_b: str,
                    match_id: str, output_path: str) -> None:
    """比赛结束时调用，写入 MATCH_END 事件。"""
    state_file = Path(prev_state_file)
    if not state_file.exists():
        return
    data = json.loads(state_file.read_text(encoding="utf-8"))
    score_a, score_b = data["score_a"], data["score_b"]
    leader = _determine_leader(score_a, score_b)
    diff = abs(score_a - score_b)
    detail = "TIE" if leader == "TIE" else f"winner={leader} +{diff}"

    state = PollState(
        timestamp=datetime.now(timezone.utc),
        elapsed_sec=data["elapsed_sec"],
        loop_seq=data["loop_seq"],
        score_a=score_a,
        score_b=score_b,
        factory_owner=data["factory_owner"],
    )
    ev = _make_event(state, "MATCH_END", detail, strategy_a, strategy_b, match_id)
    _write_event(Path(output_path), ev)
    print(f"[observer] {ev.event_type}: {ev.detail} (A={ev.score_a} B={ev.score_b})")


def _make_event(state: PollState, event_type: str, detail: str,
                strategy_a: str, strategy_b: str, match_id: str) -> MatchEvent:
    return MatchEvent(
        match_id=match_id,
        event_type=event_type,
        iso_time=state.timestamp.isoformat(timespec="seconds"),
        elapsed_sec=state.elapsed_sec,
        loop_seq=state.loop_seq,
        strategy_a=strategy_a,
        strategy_b=strategy_b,
        score_a=state.score_a,
        score_b=state.score_b,
        leader=_determine_leader(state.score_a, state.score_b),
        factory_owner=state.factory_owner,
        detail=detail,
    )
