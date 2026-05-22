import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day145：お金つかったログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day145_money_log.json")

CATEGORIES = [
    "食費",
    "日用品",
    "趣味",
    "勉強",
    "家族",
    "健康",
    "交通",
    "娯楽",
    "開発",
    "その他"
]

SATISFACTION = [
    "😊 大満足",
    "🙂 満足",
    "😐 普通",
    "😢 後悔"
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today():
    return date.today().isoformat()


def to_df(data):

    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "date": x["date"],
            "category": x["category"],
            "amount": x["amount"],
            "title": x["title"],
            "satisfaction": x["satisfaction"],
            "memo": x["memo"]
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("date", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💴",
    layout="wide"
)

st.title("💴 Day145：お金つかったログ")
st.caption("何に使ったかと、満足度を記録する。")

data = load_data()

left, right = st.columns([1,1])

with left:

    st.subheader("支出記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    title = st.text_input(
        "何に使った？",
        placeholder="例：カレー、サプリ、本"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    amount = st.number_input(
        "金額",
        min_value=0,
        value=500
    )

    satisfaction = st.radio(
        "満足度",
        SATISFACTION
    )

    memo = st.text_area(
        "メモ",
        placeholder="思ったこと"
    )

    if st.button("💴 保存", type="primary"):

        item = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": log_date.isoformat(),
            "title": title,
            "category": category,
            "amount": amount,
            "satisfaction": satisfaction,
            "memo": memo,
        }

        data["logs"].append(item)

        save_data(data)

        st.success("保存したよ！")

        st.rerun()


with right:

    st.subheader("今日の合計")

    today_logs = [
        x
        for x in data["logs"]
        if x["date"] == today()
    ]

    total = sum(
        x["amount"]
        for x in today_logs
    )

    st.metric(
        "今日使ったお金",
        f"{total:,} 円"
    )

    if today_logs:

        best = max(
            today_logs,
            key=lambda x: SATISFACTION.index(
                x["satisfaction"]
            )
        )

        st.info(
            f"今日の記憶：{best['title']}"
        )

st.divider()

df = to_df(data)

st.subheader("履歴")

if df.empty:

    st.write("まだ履歴がないよ")

else:

    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )

    csv = (
        df
        .to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        "⬇️ CSV",
        csv,
        "day145_money_log.csv"
    )
