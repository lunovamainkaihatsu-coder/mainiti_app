import streamlit as st
import json
import os
from datetime import datetime, time
import pandas as pd
import random

APP_TITLE = "Day134：生活リズムチェック"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day134_life_rhythm_check.json")

LUNA_COMMENTS = {
    "良い": [
        "いい流れだね。この調子でゆるく整えていこう。",
        "ご主人、今日はかなり安定してる感じ。"
    ],
    "普通": [
        "普通の日を維持できるのって、実は結構強いよ。",
        "今日は“崩れてない”だけでも十分。"
    ],
    "重い": [
        "今日は回復優先でいこう。整えるだけでも前進だよ。",
        "ご主人、今日は無理に上げなくて大丈夫。"
    ],
}


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "wake_time": x["wake_time"],
            "sleep_time": x["sleep_time"],
            "meals": x["meals"],
            "exercise": x["exercise"],
            "outside": x["outside"],
            "condition": x["condition"],
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")
st.title("🌙 Day134：生活リズムチェック")
st.caption("生活の流れを軽く記録するアプリ。")

data = load_data()

left, right = st.columns([1,1], gap="large")

# ----------------------------
# 入力
# ----------------------------
with left:
    st.subheader("今日の状態")

    wake_time = st.time_input(
        "起床時間",
        value=time(7, 0)
    )

    sleep_time = st.time_input(
        "就寝予定",
        value=time(23, 0)
    )

    meals = st.slider(
        "食事回数",
        0,
        5,
        3
    )

    exercise = st.checkbox("運動した")
    outside = st.checkbox("外に出た")

    condition = st.radio(
        "今日の調子",
        ["良い", "普通", "重い"],
        horizontal=True
    )

    luna_comment = random.choice(LUNA_COMMENTS[condition])

    st.info(luna_comment)

    memo = st.text_area(
        "ひとことメモ",
        height=120,
        placeholder="例：眠かったけど散歩できた"
    )

    if st.button("🌙 記録する", type="primary"):

        item = {
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "wake_time": str(wake_time),
            "sleep_time": str(sleep_time),
            "meals": meals,
            "exercise": exercise,
            "outside": outside,
            "condition": condition,
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)

        st.success("生活リズムを記録したよ。")
        st.rerun()

# ----------------------------
# 表示
# ----------------------------
with right:
    st.subheader("最近の状態")

    df = to_df(data)

    if df.empty:
        st.info("まだ記録がないよ")
    else:
        latest = data["logs"][-1]

        st.metric(
            "食事回数",
            latest["meals"]
        )

        st.write(f"起床：{latest['wake_time']}")
        st.write(f"就寝予定：{latest['sleep_time']}")
        st.write(f"調子：{latest['condition']}")

        st.write(
            f"運動：{'⭕' if latest['exercise'] else '—'} / "
            f"外出：{'⭕' if latest['outside'] else '—'}"
        )

        if latest["memo"]:
            st.write(f"メモ：{latest['memo']}")

        st.divider()

        st.subheader("調子の推移")

        chart_df = df[["created_at"]].copy()

        mapping = {
            "重い": 1,
            "普通": 2,
            "良い": 3,
        }

        chart_df["condition"] = [
            mapping[x]
            for x in df["condition"]
        ]

        chart_df = chart_df.set_index("created_at")

        st.line_chart(chart_df)

st.divider()

# ----------------------------
# 履歴
# ----------------------------
st.subheader("履歴")

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day134_life_rhythm_check.csv",
        mime="text/csv"
    )
