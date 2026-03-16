import streamlit as st
import json
import os
from datetime import datetime, timedelta, date
import pandas as pd

APP_TITLE = "Day94：感情ヒートマップ"

# Day93 の保存ファイルを読む想定
DEFAULT_DIARY_PATH = os.path.join("data", "day93_luna_diary.json")

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

MOOD_EMOJI = {
    "うれしい": "😊",
    "たのしい": "🎉",
    "わくわく": "✨",
    "ふつう": "🙂",
    "もやもや": "☁️",
    "つかれた": "😴",
    "やる気がない": "🫠",
    "かなしい": "😢",
}


# ----------------------------
# load
# ----------------------------
def load_diary(path: str):
    if not os.path.exists(path):
        return {"entries": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def to_df(data):
    rows = []
    for x in data.get("entries", []):
        mood = x.get("mood", "")
        created_at = x.get("created_at", "")
        d = x.get("date", "")

        rows.append({
            "id": x.get("id", ""),
            "created_at": created_at,
            "date": d,
            "mood": mood,
            "title": x.get("title", ""),
            "favorite": bool(x.get("favorite", False)),
            "score": MOOD_SCORE.get(mood, 0),
            "emoji": MOOD_EMOJI.get(mood, "❔"),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("created_at", ascending=False)
    return df


def build_daily_summary(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame()

    # 同じ日に複数日記がある場合は平均スコア + 最頻気分
    grouped = []
    for d, group in df.groupby(df["date"].dt.date):
        avg_score = round(group["score"].mean(), 2)
        mood_mode = group["mood"].mode().iloc[0] if not group["mood"].mode().empty else group.iloc[0]["mood"]
        count = len(group)
        grouped.append({
            "date": d.isoformat(),
            "avg_score": avg_score,
            "main_mood": mood_mode,
            "emoji": MOOD_EMOJI.get(mood_mode, "❔"),
            "count": count,
        })

    out = pd.DataFrame(grouped).sort_values("date", ascending=False)
    return out


def last_n_days_table(daily_df: pd.DataFrame, days: int = 30):
    today = date.today()
    start = today - timedelta(days=days - 1)

    mapping = {}
    if not daily_df.empty:
        for _, row in daily_df.iterrows():
            mapping[row["date"]] = row

    rows = []
    current = start
    while current <= today:
        key = current.isoformat()
        if key in mapping:
            row = mapping[key]
            rows.append({
                "date": key,
                "day": current.strftime("%m/%d"),
                "mood": row["main_mood"],
                "emoji": row["emoji"],
                "score": row["avg_score"],
                "entries": row["count"],
            })
        else:
            rows.append({
                "date": key,
                "day": current.strftime("%m/%d"),
                "mood": "記録なし",
                "emoji": "—",
                "score": None,
                "entries": 0,
            })
        current += timedelta(days=1)

    return pd.DataFrame(rows)


def mood_counts(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(columns=["mood", "count"])
    c = df["mood"].value_counts().reset_index()
    c.columns = ["mood", "count"]
    c["emoji"] = c["mood"].map(MOOD_EMOJI)
    return c


def score_label(score):
    if score is None or pd.isna(score):
        return "—"
    if score >= 4.5:
        return "かなり明るめ"
    elif score >= 3.5:
        return "明るめ"
    elif score >= 2.5:
        return "中間"
    elif score >= 1.5:
        return "低め"
    else:
        return "かなり低め"


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.title("📊 Day94：感情ヒートマップ")
st.caption("ルナ日記の気分を見える化して、最近の感情の流れを振り返るアプリ。")

with st.sidebar:
    st.subheader("📂 読み込む日記")
    diary_path = st.text_input("Day93 JSON Path", value=DEFAULT_DIARY_PATH)
    st.caption("例：data/day93_luna_diary.json")

    days_to_show = st.selectbox("表示日数", [7, 14, 30], index=2)

data = load_diary(diary_path)
df = to_df(data)

if df.empty:
    st.warning("Day93のデータが見つからないか、まだ日記がないよ。先にルナ日記を書いてみてね。")
    st.stop()

daily_df = build_daily_summary(df)
recent_df = last_n_days_table(daily_df, days=days_to_show)
count_df = mood_counts(df)

# summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("日記総数", len(df))
with col2:
    st.metric("記録日数", len(daily_df))
with col3:
    latest_score = daily_df.iloc[0]["avg_score"] if not daily_df.empty else None
    st.metric("最新日の感情傾向", score_label(latest_score))

st.divider()

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.subheader(f"🗓 最近{days_to_show}日の感情一覧")

    def color_mood(val):
        if val == "うれしい":
            return "background-color: #ffe082"
        elif val == "たのしい":
            return "background-color: #ffecb3"
        elif val == "わくわく":
            return "background-color: #fff59d"
        elif val == "ふつう":
            return "background-color: #e0e0e0"
        elif val == "もやもや":
            return "background-color: #d1c4e9"
        elif val == "つかれた":
            return "background-color: #b3e5fc"
        elif val == "やる気がない":
            return "background-color: #cfd8dc"
        elif val == "かなしい":
            return "background-color: #bbdefb"
        elif val == "記録なし":
            return "background-color: #fafafa"
        return ""

    styled = recent_df.style.map(color_mood, subset=["mood"])
    st.dataframe(styled, use_container_width=True, height=420)

with right:
    st.subheader("📌 気分の出現回数")
    st.dataframe(count_df, use_container_width=True, height=260)

    st.divider()
    st.subheader("📈 感情スコア推移")
    chart_df = recent_df.copy()
    chart_df = chart_df.dropna(subset=["score"])
    if chart_df.empty:
        st.info("スコア付きデータがまだ少ないよ。")
    else:
        chart_df = chart_df.set_index("day")[["score"]]
        st.line_chart(chart_df)

st.divider()
st.subheader("📚 日ごとの詳細")

pick_date = st.selectbox(
    "日付を選んでね",
    options=[d.strftime("%Y-%m-%d") for d in sorted(df["date"].dropna().unique(), reverse=True)]
)

picked_rows = df[df["date"].dt.strftime("%Y-%m-%d") == pick_date].copy()

if picked_rows.empty:
    st.write("この日の記録はないよ。")
else:
    picked_rows = picked_rows.sort_values("created_at", ascending=False)
    for _, row in picked_rows.iterrows():
        with st.container():
            st.markdown(f"### {row['emoji']} {row['title']}")
            st.write(f"日時：{row['created_at']}")
            st.write(f"気分：{row['mood']} / スコア：{row['score']}")
            st.write(f"お気に入り：{'⭐' if row['favorite'] else '—'}")
            st.divider()

csv = recent_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ 最近の感情一覧をCSVダウンロード",
    data=csv,
    file_name="day94_emotion_heatmap.csv",
    mime="text/csv"
)
