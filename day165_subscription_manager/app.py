import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day165：サブスク管理帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day165_subscription_manager.json"
)

CATEGORIES = [
    "動画",
    "音楽",
    "AI",
    "仕事",
    "学習",
    "ゲーム",
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(
            DATA_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                {"subs": []},
                f,
                ensure_ascii=False,
                indent=2
            )


def load_data():
    ensure_storage()

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_data(data):
    with open(
        DATA_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def today_str():
    return date.today().isoformat()


def now_str():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💳",
    layout="wide"
)

st.title("💳 Day165：サブスク管理帳")

data = load_data()

left, right = st.columns(2)

with left:

    st.subheader("登録")

    name = st.text_input(
        "サービス名"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    price = st.number_input(
        "月額料金",
        min_value=0,
        value=1000,
        step=100
    )

    pay_day = st.number_input(
        "支払日",
        min_value=1,
        max_value=31,
        value=1
    )

    memo = st.text_area(
        "メモ"
    )

    if st.button(
        "➕ 登録",
        type="primary"
    ):

        if name.strip():

            item = {
                "id": datetime.now().strftime(
                    "%Y%m%d%H%M%S%f"
                ),
                "created_at": now_str(),
                "date": today_str(),
                "name": name,
                "category": category,
                "price": int(price),
                "pay_day": int(pay_day),
                "memo": memo,
            }

            data["subs"].append(item)

            save_data(data)

            st.success("登録したよ！")
            st.rerun()

with right:

    df = pd.DataFrame(
        data["subs"]
    )

    if not df.empty:

        monthly = df["price"].sum()
        yearly = monthly * 12

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "月額合計",
            f"{monthly:,}円"
        )

        c2.metric(
            "年間合計",
            f"{yearly:,}円"
        )

        c3.metric(
            "サービス数",
            len(df)
        )

    else:

        st.info(
            "まだ登録がないよ"
        )

st.divider()

st.subheader("サブスク一覧")

df = pd.DataFrame(
    data["subs"]
)

if df.empty:

    st.write(
        "まだ登録されていないよ"
    )

else:

    st.dataframe(
        df[
            [
                "name",
                "category",
                "price",
                "pay_day",
                "memo",
            ]
        ],
        use_container_width=True
    )

    delete_id = st.selectbox(
        "削除するサービス",
        df["id"]
    )

    if st.button(
        "🗑️ 削除"
    ):

        data["subs"] = [
            x
            for x in data["subs"]
            if x["id"] != delete_id
        ]

        save_data(data)

        st.success(
            "削除したよ"
        )

        st.rerun()
