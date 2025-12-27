# app.py
from __future__ import annotations

import datetime as dt
import json
import random
from pathlib import Path

import streamlit as st

APP_TITLE = "ミニご褒美ガチャ（Day44）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "reward_log.json"

REWARDS = [
    "温かい飲み物をゆっくり飲む",
    "10分だけストレッチ",
    "目を閉じて深呼吸30秒",
    "今日は風呂を最優先にする",
    "好きな音楽を1曲聴く",
    "5分だけ片付け",
    "今日は何もしない許可を出す",
]


def load_log():
    if not DATA_PATH.exists():
        return {}
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_log(log):
    DATA_PATH.write_text(
        json.dumps(log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption("がんばったかどうかは関係ない。押していい。")

today = dt.date.today().isoformat()
log = load_log()

if today in log:
    st.subheader("🎉 今日のご褒美")
    st.success(log[today])
    st.info("今日はもう引いてるよ。明日またね。")
else:
    if st.button("🎰 ご褒美を引く", use_container_width=True):
        random.seed(today)  # 日替わり固定
        reward = random.choice(REWARDS)
        log[today] = reward
        save_log(log)
        st.success(reward)
        st.balloons()

st.divider()
st.subheader("📜 過去のご褒美")

if not log:
    st.info("まだ記録がありません。")
else:
    for d, r in sorted(log.items(), reverse=True)[:14]:
        with st.container(border=True):
            st.markdown(f"**{d}**")
            st.write(r)

with st.expander("⚠️ 全削除"):
    if st.button("🧨 ログ全削除", type="primary"):
        save_log({})
        st.success("削除しました")
        st.rerun()
