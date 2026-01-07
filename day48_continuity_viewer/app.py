# app.py
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import streamlit as st

APP_TITLE = "ちゃんと続いてる可視化"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "days_log.json"

st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption("止まった日より、続いた日を正しく見る。")

# =========
# 設定
# =========
START_DATE = dt.date(2025, 11, 19)  # ← Day1の日付に合わせて調整

# =========
# データ操作
# =========
def load_days():
    if not DATA_PATH.exists():
        return []
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_days(days):
    DATA_PATH.write_text(
        json.dumps(days, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

# =========
# 今日を記録
# =========
days = load_days()
today = dt.date.today().isoformat()

if st.button("📌 今日も作ったと記録する", use_container_width=True):
    if today not in days:
        days.append(today)
        save_days(days)
        st.success("今日を“継続日”として記録しました。")
        st.rerun()
    else:
        st.info("今日はすでに記録されています。")

st.divider()

# =========
# 可視化
# =========
today_date = dt.date.today()
total_days = (today_date - START_DATE).days + 1
continued_days = len(days)
stopped_days = total_days - continued_days

rate = (continued_days / total_days) * 100 if total_days > 0 else 0

st.subheader("📊 継続の事実")

st.metric("経過日数", f"{total_days} 日")
st.metric("作った日数", f"{continued_days} 日")
st.metric("止まった日数", f"{stopped_days} 日")
st.metric("継続率", f"{rate:.1f} %")

st.divider()

# =========
# メッセージ
# =========
if rate >= 80:
    msg = "これはもう“習慣”。胸張っていい。"
elif rate >= 50:
    msg = "半分以上やってる。十分すぎる。"
elif rate >= 30:
    msg = "止まりながらも、続いてる。"
else:
    msg = "それでも、ゼロじゃない。それが大事。"

st.success(msg)

st.caption("※ 継続とは、止まらないことではなく「戻ってくること」。")

with st.expander("📅 記録された日"):
    for d in sorted(days, reverse=True):
        st.write(d)

with st.expander("⚠️ 全削除"):
    if st.button("🧨 記録をすべて消す", type="primary"):
        save_days([])
        st.success("リセットしました")
        st.rerun()
