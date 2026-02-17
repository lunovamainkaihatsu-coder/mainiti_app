import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Destiny Log", layout="centered")

LOG_FILE = "destiny_log.json"


# -----------------------------
# ログ読み込み
# -----------------------------
def load_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# ログ保存
# -----------------------------
def save_logs(logs):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


# -----------------------------
# UI
# -----------------------------
st.title("📜 Destiny Log")
st.caption("あなたの運命は、ここに記録される。")

logs = load_logs()

st.divider()

# 入力
st.subheader("今日の記録")

text = st.text_input("今日、何を成し遂げた？")

if st.button("記録する", use_container_width=True):
    if text:
        logs.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "text": text
        })
        save_logs(logs)
        st.success("運命が記録された。")
        st.rerun()

st.divider()

# 表示
st.subheader("運命の軌跡")

if logs:
    for i, log in enumerate(reversed(logs), 1):
        st.markdown(f"**Day {len(logs)-i+1}**")
        st.write(log["text"])
        st.caption(log["date"])
        st.divider()
else:
    st.info("まだ記録はない。ここから始まる。")

# 統計
st.subheader("統計")

st.write(f"総記録数：{len(logs)} 日")

st.divider()
st.caption("🌙 すべての伝説は、小さな記録から始まる。")
