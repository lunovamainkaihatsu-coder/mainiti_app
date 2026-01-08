# app.py
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import streamlit as st

APP_TITLE = "Day50 記念レコード"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "milestone_day50.json"

# ===== 設定 =====
START_DATE = dt.date(2025, 11, 19)  # Day1の日付に合わせて調整
DAY_NUMBER = 50

# ===== 計算 =====
today = dt.date.today()
elapsed_days = (today - START_DATE).days + 1

made_days = min(elapsed_days, DAY_NUMBER)  # 簡易：Day50想定
stopped_days = DAY_NUMBER - made_days
max_streak = None  # 厳密計算はDay49ログ連携で拡張可能

record = {
    "day": DAY_NUMBER,
    "date": today.isoformat(),
    "start_date": START_DATE.isoformat(),
    "elapsed_days": elapsed_days,
    "made_days": made_days,
    "stopped_days": max(stopped_days, 0),
    "message": "止まりながら、50日続いた。",
    "created_at": dt.datetime.now().isoformat(timespec="seconds"),
}

# ===== UI =====
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🎉 Day50")
st.subheader("ここまで来た")

st.divider()

st.markdown(
    f"""
    ### 📊 記録
    - 経過日数：**{elapsed_days}日**
    - 作った日数：**{made_days}日**
    - 止まった日数：**{record['stopped_days']}日**
    """
)

st.divider()

st.success("止まりながら、50日続いた。")
st.caption("これは結果ではなく、事実。")

st.divider()

if DATA_PATH.exists():
    st.info("この記念レコードは、すでに保存されています。")
    st.json(json.loads(DATA_PATH.read_text(encoding="utf-8")))
else:
    if st.button("🏅 Day50を記録する", use_container_width=True):
        DATA_PATH.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        st.balloons()
        st.success("Day50は、正式に記録されました。")
        st.rerun()

st.caption("※ この記録は編集できません。未来のあなたのためのものです。")
