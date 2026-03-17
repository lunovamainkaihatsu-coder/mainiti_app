import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta, date

APP_TITLE = "Day95：ごきげん予報"

DATA_PATH = os.path.join("data", "day93_luna_diary.json")

MOOD_SCORE = {
    "うれしい": 5,
    "たのしい": 4,
    "わくわく": 4,
    "ふつう": 3,
    "もやもや": 2,
    "つかれた": 2,
    "やる気がない": 1,
    "かなしい": 1,
}


# -----------------------
# load
# -----------------------
def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", [])


def to_df(entries):
    rows = []
    for x in entries:
        mood = x.get("mood", "")
        score = MOOD_SCORE.get(mood, 0)

        rows.append({
            "date": x.get("date"),
            "mood": mood,
            "score": score,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


# -----------------------
# forecast logic
# -----------------------
def forecast(df, days=7):
    if df.empty:
        return None, None, None

    recent = df.sort_values("date", ascending=False).head(days)

    avg = recent["score"].mean()

    trend = recent["score"].diff().mean()

    # 判定
    if avg >= 4:
        state = "攻め"
    elif avg >= 2.5:
        state = "守り"
    else:
        state = "回復"

    # トレンド補正
    if trend > 0.3:
        trend_text = "上昇中"
    elif trend < -0.3:
        trend_text = "下降中"
    else:
        trend_text = "安定"

    return state, avg, trend_text


def advice(state):
    if state == "攻め":
        return "新しいこと or 前に進める行動を1つやろう"
    elif state == "守り":
        return "小さく整える行動を1つやろう"
    else:
        return "無理せず回復を最優先にしよう"


# -----------------------
# UI
# -----------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🌤")

st.title("🌤 Day95：ごきげん予報")
st.caption("最近の感情から、明日の状態を予測する")

entries = load_data()
df = to_df(entries)

if df.empty:
    st.warning("データがないよ。まずはルナ日記を書こう！")
    st.stop()

days = st.selectbox("分析日数", [3, 5, 7, 14], index=2)

state, avg, trend = forecast(df, days)

# 表示
st.subheader("🌙 明日の予測")

if state == "攻め":
    st.success(f"🔥 攻めの日")
elif state == "守り":
    st.info(f"⚖️ 守りの日")
else:
    st.warning(f"🌙 回復の日")

st.write(f"平均スコア：{round(avg,2)}")
st.write(f"トレンド：{trend}")

st.divider()

st.subheader("🧠 ルナのアドバイス")
st.success(advice(state))

st.divider()

st.subheader("📈 最近の感情推移")

chart_df = df.sort_values("date").set_index("date")[["score"]]
st.line_chart(chart_df)

st.divider()

st.subheader("📊 データ一覧")
st.dataframe(df, use_container_width=True)
