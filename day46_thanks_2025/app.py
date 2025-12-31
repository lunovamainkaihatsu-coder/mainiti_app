# app.py
from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import streamlit as st

APP_TITLE = "今年のありがとう、3つだけ"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "thanks_year.json"

YEAR = dt.date.today().year


@dataclass
class ThanksLog:
    id: str
    year: int
    thanks: List[str]
    note: str
    created_at: str

    @staticmethod
    def new(year: int, thanks: List[str], note: str) -> "ThanksLog":
        clean = [x.strip() for x in thanks if x and x.strip()]
        clean = clean[:3]
        return ThanksLog(
            id=str(uuid.uuid4()),
            year=year,
            thanks=clean,
            note=note.strip(),
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


def load_logs() -> List[ThanksLog]:
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        out: List[ThanksLog] = []
        for r in raw:
            out.append(
                ThanksLog(
                    id=r.get("id", str(uuid.uuid4())),
                    year=int(r.get("year", YEAR)),
                    thanks=list(r.get("thanks", [])),
                    note=r.get("note", ""),
                    created_at=r.get("created_at", ""),
                )
            )
        return out
    except Exception:
        return []


def save_logs(logs: List[ThanksLog]):
    DATA_PATH.write_text(
        json.dumps([asdict(x) for x in logs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# =========================
# UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption("振り返らない。ただ、受け取る。")

if "thanks_logs" not in st.session_state:
    st.session_state["thanks_logs"] = load_logs()

logs: List[ThanksLog] = st.session_state["thanks_logs"]
this_year = [x for x in logs if x.year == YEAR]

st.subheader(f"🎁 {YEAR}年のありがとう")

if this_year:
    log = this_year[0]
    st.success("この年は、もう受け取っています。")
    for i, t in enumerate(log.thanks, start=1):
        st.write(f"- {i}. {t}")
    if log.note:
        st.caption(log.note)
    st.caption(f"保存日時：{log.created_at}")
else:
    with st.form("thanks_form"):
        t1 = st.text_input("ありがとう①", placeholder="例：最後まで生きた自分")
        t2 = st.text_input("ありがとう②", placeholder="例：家族")
        t3 = st.text_input("ありがとう③", placeholder="例：ルナ")
        note = st.text_area(
            "一言（任意）",
            placeholder="例：いろいろあったけど、ここまで来た。",
            height=100,
        )
        ok = st.form_submit_button("🌙 この年を受け取る")

    if ok:
        thanks = [t1, t2, t3]
        clean = [x for x in thanks if x.strip()]
        if not clean:
            st.error("1つでいい。何か1つだけ入れて。")
        else:
            logs.append(ThanksLog.new(YEAR, thanks, note))
            save_logs(logs)
            st.success("この年は、ちゃんと受け取られました。")
            st.balloons()
            st.rerun()

st.divider()

with st.expander("📜 過去の年"):
    if not logs:
        st.info("まだ記録はありません。")
    else:
        for x in sorted(logs, key=lambda z: z.year, reverse=True):
            with st.container(border=True):
                st.markdown(f"### {x.year}年")
                for i, t in enumerate(x.thanks, start=1):
                    st.write(f"- {i}. {t}")
                if x.note:
                    st.caption(x.note)

with st.expander("⚠️ 全削除"):
    if st.button("🧨 全ログ削除", type="primary"):
        st.session_state["thanks_logs"] = []
        save_logs([])
        st.success("削除しました")
        st.rerun()
