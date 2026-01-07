# app.py
from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

APP_TITLE = "継続トラッカー Pro（Day49）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

HABITS_PATH = DATA_DIR / "habits.json"  # 習慣マスタ
LOGS_PATH = DATA_DIR / "logs.json"      # 日別ログ

STATUS_DONE = "done"
STATUS_REST = "rest"
STATUS_MISS = "miss"

STATUS_LABEL = {
    STATUS_DONE: "✅ done",
    STATUS_REST: "💤 rest",
    STATUS_MISS: "❌ miss",
}

STATUS_EMOJI = {
    STATUS_DONE: "✅",
    STATUS_REST: "💤",
    STATUS_MISS: "❌",
}


@dataclass
class Habit:
    id: str
    name: str
    created_at: str

    @staticmethod
    def new(name: str) -> "Habit":
        return Habit(
            id=str(uuid.uuid4()),
            name=name.strip(),
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_habits() -> List[Habit]:
    raw = _read_json(HABITS_PATH, [])
    habits: List[Habit] = []
    if isinstance(raw, list):
        for r in raw:
            if isinstance(r, dict):
                habits.append(
                    Habit(
                        id=str(r.get("id", "")) or str(uuid.uuid4()),
                        name=str(r.get("name", "")).strip() or "untitled",
                        created_at=str(r.get("created_at", "")) or dt.datetime.now().isoformat(timespec="seconds"),
                    )
                )
    return habits


def save_habits(habits: List[Habit]) -> None:
    _write_json(HABITS_PATH, [asdict(h) for h in habits])


def load_logs() -> Dict[str, Dict[str, str]]:
    """
    logs[date][habit_id] = status
    """
    raw = _read_json(LOGS_PATH, {})
    if isinstance(raw, dict):
        # できるだけ整形
        out: Dict[str, Dict[str, str]] = {}
        for date, v in raw.items():
            if not isinstance(v, dict):
                continue
            out[str(date)] = {str(hid): str(sts) for hid, sts in v.items()}
        return out
    return {}


def save_logs(logs: Dict[str, Dict[str, str]]) -> None:
    _write_json(LOGS_PATH, logs)


def iso(d: dt.date) -> str:
    return d.isoformat()


def daterange(end_date: dt.date, days: int) -> List[dt.date]:
    days = max(1, int(days))
    start = end_date - dt.timedelta(days=days - 1)
    return [start + dt.timedelta(days=i) for i in range(days)]


def calc_streak_for_habit(logs: Dict[str, Dict[str, str]], habit_id: str, up_to: dt.date) -> int:
    """up_to から遡って連続 done 日数を数える（rest/miss/未記録で止まる）"""
    streak = 0
    cur = up_to
    while True:
        day = iso(cur)
        status = logs.get(day, {}).get(habit_id)
        if status == STATUS_DONE:
            streak += 1
            cur -= dt.timedelta(days=1)
            continue
        break
    return streak


def calc_max_streak_for_habit(logs: Dict[str, Dict[str, str]], habit_id: str, dates: List[dt.date]) -> int:
    max_streak = 0
    cur = 0
    for d in dates:
        status = logs.get(iso(d), {}).get(habit_id)
        if status == STATUS_DONE:
            cur += 1
            max_streak = max(max_streak, cur)
        else:
            cur = 0
    return max_streak


def calc_rate_for_habit(logs: Dict[str, Dict[str, str]], habit_id: str, dates: List[dt.date]) -> float:
    done = 0
    total = len(dates)
    for d in dates:
        if logs.get(iso(d), {}).get(habit_id) == STATUS_DONE:
            done += 1
    return (done / total) * 100 if total > 0 else 0.0


# =========================
# UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("複数の習慣を、日別に記録。数字で“続いてる”を見える化。")

if "habits" not in st.session_state:
    st.session_state["habits"] = load_habits()
if "logs" not in st.session_state:
    st.session_state["logs"] = load_logs()

habits: List[Habit] = st.session_state["habits"]
logs: Dict[str, Dict[str, str]] = st.session_state["logs"]

today = dt.date.today()

with st.sidebar:
    st.header("設定")
    period_days = st.slider("表示期間（日）", 7, 90, 30)
    st.divider()
    st.subheader("習慣を追加")
    new_name = st.text_input("習慣名", placeholder="例：毎日アプリ / 勉強30分 / 腕立て10回")
    if st.button("➕ 追加"):
        if new_name.strip():
            habits.append(Habit.new(new_name))
            save_habits(habits)
            st.success("追加したよ")
            st.rerun()
        else:
            st.error("習慣名を入れてね")
    st.divider()
    st.subheader("データ")
    st.caption(f"HABITS: `{HABITS_PATH}`")
    st.caption(f"LOGS: `{LOGS_PATH}`")
    if st.button("💾 保存（手動）"):
        save_habits(habits)
        save_logs(logs)
        st.success("保存したよ")

if not habits:
    st.info("まずは左のサイドバーで“習慣”を1つ追加してね。")
    st.stop()

dates = daterange(today, period_days)
date_keys = [iso(d) for d in dates]

# 今日の記録パネル
st.subheader("📌 今日の記録")

for h in habits:
    c1, c2, c3, c4 = st.columns([1.6, 1, 1, 1])
    current = logs.get(iso(today), {}).get(h.id)
    with c1:
        st.markdown(f"**{h.name}**　（今日：{STATUS_LABEL.get(current,'— 未記録')}）")
    if c2.button("✅ done", key=f"done_{h.id}", use_container_width=True):
        logs.setdefault(iso(today), {})[h.id] = STATUS_DONE
        save_logs(logs)
        st.rerun()
    if c3.button("💤 rest", key=f"rest_{h.id}", use_container_width=True):
        logs.setdefault(iso(today), {})[h.id] = STATUS_REST
        save_logs(logs)
        st.rerun()
    if c4.button("❌ miss", key=f"miss_{h.id}", use_container_width=True):
        logs.setdefault(iso(today), {})[h.id] = STATUS_MISS
        save_logs(logs)
        st.rerun()

st.divider()

# 集計
st.subheader("📊 集計（表示期間）")
cols = st.columns(min(4, len(habits)))
for i, h in enumerate(habits):
    rate = calc_rate_for_habit(logs, h.id, dates)
    streak = calc_streak_for_habit(logs, h.id, today)
    max_streak = calc_max_streak_for_habit(logs, h.id, dates)
    with cols[i % len(cols)]:
        st.metric(h.name, f"{rate:.1f}%", help="done の割合（表示期間）")
        st.caption(f"連続 done：{streak}日 / 最大：{max_streak}日")

st.divider()

# 表（簡易カレンダー）
st.subheader("🗓️ カレンダー（簡易）")
st.caption("✅=done / 💤=rest / ❌=miss / ・=未記録")

# ヘッダ行
header = ["習慣 \\ 日付"] + [d.strftime("%m/%d") for d in dates]
rows = []
for h in habits:
    row = [h.name]
    for d in dates:
        status = logs.get(iso(d), {}).get(h.id)
        row.append(STATUS_EMOJI.get(status, "・"))
    rows.append(row)

# 表示（Streamlitのdataframeより読みやすいようにmarkdown風）
# 文字幅が崩れる環境もあるので、dataframeも併記
st.dataframe(
    rows,
    use_container_width=True,
    hide_index=True,
)

with st.expander("⚙️ 習慣の削除（危険）"):
    st.warning("習慣を削除すると、その習慣の表示が消えます（ログはファイルに残るので復元は可能）。")
    habit_names = {h.name: h.id for h in habits}
    target = st.selectbox("削除する習慣", list(habit_names.keys()))
    if st.button("🗑 習慣を削除", type="primary"):
        hid = habit_names[target]
        st.session_state["habits"] = [h for h in habits if h.id != hid]
        save_habits(st.session_state["habits"])
        st.success("削除しました")
        st.rerun()

with st.expander("⚠️ 全ログ削除（危険）"):
    st.warning("全ログを消します。戻せません。")
    if st.button("🧨 logs.json を全削除", type="primary"):
        st.session_state["logs"] = {}
        save_logs({})
        st.success("全削除しました")
        st.rerun()
