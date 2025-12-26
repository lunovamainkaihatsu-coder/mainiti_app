# app.py
from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import streamlit as st

APP_TITLE = "今日の自分、合格？（Day43）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "self_pass_log.json"


@dataclass
class PassLog:
    id: str
    date: str       # YYYY-MM-DD
    result: str     # 合格 / まあまあ / 無理してた
    message: str
    created_at: str

    @staticmethod
    def new(date: str, result: str, message: str) -> "PassLog":
        return PassLog(
            id=str(uuid.uuid4()),
            date=date,
            result=result,
            message=message,
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


def load_logs() -> List[PassLog]:
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        out = []
        for r in raw:
            out.append(
                PassLog(
                    id=r.get("id", str(uuid.uuid4())),
                    date=r.get("date", dt.date.today().isoformat()),
                    result=r.get("result", ""),
                    message=r.get("message", ""),
                    created_at=r.get("created_at", ""),
                )
            )
        return out
    except Exception:
        return []


def save_logs(logs: List[PassLog]):
    DATA_PATH.write_text(
        json.dumps([asdict(x) for x in logs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def result_message(result: str) -> str:
    if result == "合格":
        return "今日は合格。それ以上は望まなくていい。"
    if result == "まあまあ":
        return "十分やった。今日はこれでOK。"
    return "無理してたと気づけた時点で、もう合格。"


# =========================
# UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption("評価しない。ただ、選ぶだけ。")

if "pass_logs" not in st.session_state:
    st.session_state["pass_logs"] = load_logs()

logs: List[PassLog] = st.session_state["pass_logs"]
logs_sorted = sorted(logs, key=lambda x: (x.date, x.created_at), reverse=True)

today = dt.date.today().isoformat()

st.subheader("🔘 今日の自分は？")

choice = st.radio(
    "選んでください",
    ["合格", "まあまあ", "無理してた"],
    horizontal=True,
)

if st.button("✅ 保存する", use_container_width=True):
    msg = result_message(choice)
    logs.append(PassLog.new(today, choice, msg))
    save_logs(logs)
    st.success(msg)
    st.rerun()

st.divider()

st.subheader("🗓 最近の記録")

if not logs_sorted:
    st.info("まだ記録がありません。")
else:
    for log in logs_sorted[:14]:
        with st.container(border=True):
            st.markdown(f"### {log.date}：**{log.result}**")
            st.write(log.message)
            st.caption(log.created_at)

with st.expander("⚠️ 危険：全削除", expanded=False):
    if st.button("🧨 全ログ削除", type="primary"):
        st.session_state["pass_logs"] = []
        save_logs([])
        st.success("全削除しました")
        st.rerun()
