import streamlit as st
import json
import os
from datetime import date, timedelta
import pandas as pd

APP_TITLE = "Day123：習慣分析ダッシュボード"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day122_habit_tracker.json")


def load_data():
    if not os.path.exists(DATA_PATH):
        return {"habits": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_streak(logs):
    streak = 0
    today = date.today()
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if d in logs:
            streak += 1
        else:
            break
    return streak


def calc_30day_rate(logs):
    today = date.today()
    count = 0
    for i in range(30):
        d = (today - timedelta(days=i)).isoformat()
        if d in logs:
            count += 1
    return int(count / 30 * 100)


st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.title("📊 Day123：習慣分析ダッシュボード")
st.caption("習慣の継続状況を見える化するアプリ。")

data = load_data()

if not data["habits"]:
    st.info("習慣データがないよ（Day122を先に使ってね）")
    st.stop()

# ----------------------------
# データ整理
# ----------------------------
rows = []
for h in data["habits"]:
    streak = calc_streak(h["logs"])
    rate = calc_30day_rate(h["logs"])

    rows.append({
        "習慣": h["name"],
        "連続日数": streak,
        "達成率(30日)": rate,
        "回数": len(h["logs"]),
    })

df = pd.DataFrame(rows)

# ----------------------------
# 全体指標
# ----------------------------
st.subheader("全体")

col1, col2 = st.columns(2)

with col1:
    st.metric("平均達成率", f"{df['達成率(30日)'].mean():.0f}%")

with col2:
    st.metric("最長継続", f"{df['連続日数'].max()}日")

# ----------------------------
# ランキング
# ----------------------------
st.subheader("ランキング")

df_sorted = df.sort_values("達成率(30日)", ascending=False)
st.dataframe(df_sorted, use_container_width=True)

# ----------------------------
# グラフ
# ----------------------------
st.subheader("グラフ")

st.bar_chart(df.set_index("習慣")["達成率(30日)"])

# ----------------------------
# CSV
# ----------------------------
csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ CSVダウンロード", data=csv)
