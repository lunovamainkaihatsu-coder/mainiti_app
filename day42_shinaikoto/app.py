# app.py
from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple

import streamlit as st

APP_TITLE = "やらないことリスト（Day42）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "dont_list.json"


@dataclass
class DontLog:
    id: str
    date: str          # YYYY-MM-DD
    items: List[str]   # up to 3
    note: str          # optional
    created_at: str    # ISO

    @staticmethod
    def new(date: str, items: List[str], note: str) -> "DontLog":
        clean = [x.strip() for x in items if x and x.strip()]
        clean = clean[:3]
        return DontLog(
            id=str(uuid.uuid4()),
            date=date,
            items=clean,
            note=note.strip(),
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


def load_logs() -> List[DontLog]:
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        out: List[DontLog] = []
        for r in raw:
            if not isinstance(r, dict):
                continue
            items = r.get("items", [])
            if not isinstance(items, list):
                items = []
            out.append(
                DontLog(
                    id=str(r.get("id", "")) or str(uuid.uuid4()),
                    date=str(r.get("date", "")) or dt.date.today().isoformat(),
                    items=[str(x) for x in items][:3],
                    note=str(r.get("note", "")),
                    created_at=str(r.get("created_at", "")) or dt.datetime.now().isoformat(timespec="seconds"),
                )
            )
        return out
    except Exception:
        return []


def save_logs(logs: List[DontLog]) -> None:
    DATA_PATH.write_text(json.dumps([asdict(x) for x in logs], ensure_ascii=False, indent=2), encoding="utf-8")


def to_csv_text(logs: List[DontLog]) -> str:
    # 固定で3枠に展開
    header = "id,date,dont1,dont2,dont3,note,created_at\n"
    lines = [header.strip()]
    for x in logs:
        d1 = x.items[0] if len(x.items) > 0 else ""
        d2 = x.items[1] if len(x.items) > 1 else ""
        d3 = x.items[2] if len(x.items) > 2 else ""

        row = [x.id, x.date, d1, d2, d3, x.note, x.created_at]
        escaped = []
        for v in row:
            v = v or ""
            if any(ch in v for ch in [",", '"', "\n"]):
                v = '"' + v.replace('"', '""') + '"'
            escaped.append(v)
        lines.append(",".join(escaped))
    return "\n".join(lines) + "\n"


def yohaku_message(n_items: int) -> Tuple[str, str]:
    # 宣言数でメッセージ変化
    if n_items <= 0:
        return "🫧 まだ決めてない", "今日は“やらない”を1つ決めるだけで、余白が生まれる。"
    if n_items == 1:
        return "🟩 余白、確保", "いいね。たった1つの手放しが、今日の心を救う。"
    if n_items == 2:
        return "🟦 余白、強い", "いい。守る余白が増えた。今日は軽く進めよう。"
    return "👑 余白、防衛完了", "完璧。今日は“やらない”を守り切った時点で勝ち。"


# =========================
# UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("今日“やらないこと”を決めるだけ。余白は、守った人から増える。")

if "dont_logs" not in st.session_state:
    st.session_state["dont_logs"] = load_logs()

logs: List[DontLog] = st.session_state["dont_logs"]
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

today = dt.date.today().isoformat()

st.subheader("🧿 今日の“やらないこと”宣言（最大3つ）")

col1, col2 = st.columns([1.2, 1.0], gap="large")

with col1:
    with st.form("dont_form", clear_on_submit=True):
        dont1 = st.text_input("やらない①", value="", placeholder="例：SNSをだらだら見る")
        dont2 = st.text_input("やらない②", value="", placeholder="例：完璧主義で機能追加しすぎる")
        dont3 = st.text_input("やらない③", value="", placeholder="例：夜に無理して頑張る")
        note = st.text_area("一言（任意）", value="", height=80, placeholder="例：余白を守るのが今日の勝ち")
        ok = st.form_submit_button("✅ 今日の宣言を保存")

    chosen = [dont1, dont2, dont3]
    n = len([x for x in chosen if x.strip()])
    badge, msg = yohaku_message(n)
    st.markdown(f"### {badge}")
    st.write(msg)

    if ok:
        clean = [x.strip() for x in chosen if x and x.strip()]
        if not clean:
            st.error("最低1つは入れてね！（1つで十分）")
        else:
            logs.append(DontLog.new(date=today, items=clean, note=note))
            save_logs(logs)
            st.success("保存した。今日はここまででOK。")
            st.rerun()

with col2:
    st.markdown("#### ✅ 今日の宣言（最新）")
    todays = [x for x in logs_sorted if x.date == today]
    if not todays:
        st.info("まだ今日の宣言がないよ。左で1つ書こう。")
    else:
        latest = todays[0]
        st.write(f"保存：{latest.created_at}")
        for i, t in enumerate(latest.items, start=1):
            st.write(f"- {i}. {t}")
        if latest.note:
            st.caption(latest.note)

st.divider()

# 過去ログ
st.subheader("🗓️ 過去ログ")

cutoff = dt.date.today() - dt.timedelta(days=show_days - 1)
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
        with st.container(border=True):
            left, right = st.columns([1.2, 0.8])
            with left:
                st.markdown(f"### {x.date}")
                for i, t in enumerate(x.items, start=1):
                    st.write(f"- {i}. {t}")
                if x.note:
                    st.caption(x.note)
            with right:
                if st.button("🗑 このログを削除", key=f"del_{x.id}", use_container_width=True):
                    st.session_state["dont_logs"] = [a for a in logs if a.id != x.id]
                    save_logs(st.session_state["dont_logs"])
                    st.success("削除したよ")
                    st.rerun()
                st.caption(f"saved: {x.created_at}")

st.divider()

# CSV
st.subheader("📦 CSV エクスポート")
csv_text = to_csv_text(logs_sorted)
st.download_button(
    "⬇️ CSVをダウンロード",
    data=csv_text.encode("utf-8"),
    file_name="dont_list.csv",
    mime="text/csv",
    use_container_width=True,
)

with st.expander("⚠️ 危険：全削除", expanded=False):
    st.warning("元に戻せません。")
    if st.button("🧨 全ログ削除", type="primary"):
        st.session_state["dont_logs"] = []
        save_logs([])
        st.success("全削除しました。")
        st.rerun()
