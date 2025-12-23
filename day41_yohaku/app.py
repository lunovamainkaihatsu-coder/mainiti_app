# app.py
from __future__ import annotations

import csv
import datetime as dt
import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

APP_TITLE = "余白スイッチ（Day41）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "yohaku_log.json"


@dataclass
class YohakuLog:
    id: str
    date: str  # YYYY-MM-DD
    yohaku: int  # 0-100
    note: str
    created_at: str  # ISO datetime

    @staticmethod
    def new(date: str, yohaku: int, note: str) -> "YohakuLog":
        return YohakuLog(
            id=str(uuid.uuid4()),
            date=date,
            yohaku=int(yohaku),
            note=note.strip(),
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


def load_logs() -> List[YohakuLog]:
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        out: List[YohakuLog] = []
        for r in raw:
            if not isinstance(r, dict):
                continue
            out.append(
                YohakuLog(
                    id=str(r.get("id", "")) or str(uuid.uuid4()),
                    date=str(r.get("date", "")) or dt.date.today().isoformat(),
                    yohaku=int(r.get("yohaku", 0)),
                    note=str(r.get("note", "")),
                    created_at=str(r.get("created_at", "")) or dt.datetime.now().isoformat(timespec="seconds"),
                )
            )
        return out
    except Exception:
        return []


def save_logs(logs: List[YohakuLog]) -> None:
    DATA_PATH.write_text(json.dumps([asdict(x) for x in logs], ensure_ascii=False, indent=2), encoding="utf-8")


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(n)))


def yohaku_message(score: int) -> Tuple[str, str]:
    """
    return (badge, message)
    """
    score = clamp(score, 0, 100)
    if score <= 10:
        return "🟥 余白ほぼゼロ", "今日は“頑張りすぎ警報”。まず深呼吸して、1つ手放そう。"
    if score <= 25:
        return "🟧 余白すくなめ", "詰め込み気味。やらないことを1つ決めるだけで勝ち。"
    if score <= 45:
        return "🟨 余白ふつう", "いい感じ。最後に“余白5分”だけ残して終われたら最高。"
    if score <= 70:
        return "🟩 余白あり", "余白が未来を作る日。小さな遊びを入れてOK。"
    return "🟦 余白たっぷり", "今日は回復日で天才。休むほど強くなる。"


def to_csv_text(logs: List[YohakuLog]) -> str:
    rows = [
        {
            "id": x.id,
            "date": x.date,
            "yohaku": str(x.yohaku),
            "note": x.note,
            "created_at": x.created_at,
        }
        for x in logs
    ]
    if not rows:
        return "id,date,yohaku,note,created_at\n"

    fieldnames = list(rows[0].keys())
    out = [",".join(fieldnames)]
    for r in rows:
        line = []
        for fn in fieldnames:
            v = r.get(fn, "") or ""
            if any(ch in v for ch in [",", '"', "\n"]):
                v = '"' + v.replace('"', '""') + '"'
            line.append(v)
        out.append(",".join(line))
    return "\n".join(out)


# =========================
# UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("余白を“測って、許して、記録する”だけ。未来の余白は、今日の余白から。")

# session_stateは[]アクセス（items衝突回避）
if "yohaku_logs" not in st.session_state:
    st.session_state["yohaku_logs"] = load_logs()

logs: List[YohakuLog] = st.session_state["yohaku_logs"]
logs_sorted = sorted(logs, key=lambda x: (x.date, x.created_at), reverse=True)

with st.sidebar:
    st.header("表示")
    show_days = st.slider("何日分表示する？", 3, 60, 14)
    st.divider()
    st.subheader("データ")
    st.write(f"保存先: `{DATA_PATH}`")
    if st.button("💾 保存（手動）"):
        save_logs(logs)
        st.success("保存したよ")

# 入力エリア
st.subheader("🔘 今日の余白を入れる")

today = dt.date.today().isoformat()

col1, col2 = st.columns([1.0, 1.4], gap="large")
with col1:
    score = st.slider("余白（0〜100）", 0, 100, 35)
    badge, msg = yohaku_message(score)
    st.markdown(f"### {badge}")
    st.write(msg)

with col2:
    note = st.text_area("今日の一言（任意）", value="", height=120, placeholder="例：今日はGit地獄を抜けた。えらい。")
    cA, cB = st.columns([1, 1])
    save_btn = cA.button("✅ 今日はここでOK（保存）", use_container_width=True)
    quick5 = cB.button("🕊️ 余白+5（ちょい増し）", use_container_width=True)

    if quick5:
        score = clamp(score + 5, 0, 100)
        st.session_state["_temp_score"] = score
        st.rerun()

# quick5反映（rerun後）
if "_temp_score" in st.session_state:
    # sliderはrerun後に初期値として反映しづらいので、表示側だけ整合を取る（記録はボタンで）
    pass

if save_btn:
    new_log = YohakuLog.new(date=today, yohaku=score, note=note)
    logs.append(new_log)
    save_logs(logs)
    st.success("保存した。ご主人、今日はここでOK。")
    st.rerun()

st.divider()

# 統計
st.subheader("📊 ざっくり集計")

# 期間フィルタ（過去N日）
cutoff = dt.date.today() - dt.timedelta(days=show_days - 1)
filtered = []
for x in logs:
    try:
        d = dt.date.fromisoformat(x.date)
    except Exception:
        continue
    if d >= cutoff:
        filtered.append(x)

if not filtered:
    st.info("まだログがないよ。まずは1回保存してみよう。")
else:
    # 日別の最新だけ取る（同日に複数あれば最新）
    by_date = {}
    for x in sorted(filtered, key=lambda z: (z.date, z.created_at)):
        by_date[x.date] = x

    daily = list(by_date.values())
    daily_sorted = sorted(daily, key=lambda z: z.date)

    avg = round(sum(x.yohaku for x in daily) / len(daily), 1)
    best = max(daily, key=lambda x: x.yohaku)
    worst = min(daily, key=lambda x: x.yohaku)

    a, b, c = st.columns(3)
    a.metric("平均余白", f"{avg}")
    b.metric("最高", f"{best.yohaku}", help=f"{best.date}")
    c.metric("最低", f"{worst.yohaku}", help=f"{worst.date}")

    st.caption("※ 1日1件（最新）で集計。")

st.divider()

# 最近のログ
st.subheader("🗓️ 最近のログ")

# 表示用：過去N日 + 新しい順
display = []
for x in logs_sorted:
    try:
        d = dt.date.fromisoformat(x.date)
    except Exception:
        continue
    if d >= cutoff:
        display.append(x)

if not display:
    st.info("表示対象のログがないよ。サイドバーの期間を伸ばしてみて。")
else:
    for x in display[:80]:
        badge, msg = yohaku_message(x.yohaku)
        with st.container(border=True):
            left, right = st.columns([1.2, 1.0])
            with left:
                st.markdown(f"### {x.date}　{badge}")
                st.write(msg)
            with right:
                if x.note:
                    st.write(x.note)
                st.caption(f"saved: {x.created_at}")

st.divider()

# CSV
st.subheader("📦 CSV エクスポート")
csv_text = to_csv_text(logs)
st.download_button(
    "⬇️ CSVをダウンロード",
    data=csv_text.encode("utf-8"),
    file_name="yohaku_log.csv",
    mime="text/csv",
    use_container_width=True,
)

with st.expander("⚠️ 危険：全削除", expanded=False):
    st.warning("元に戻せません。")
    if st.button("🧨 全ログ削除", type="primary"):
        st.session_state["yohaku_logs"] = []
        save_logs([])
        st.success("全削除しました。")
        st.rerun()
