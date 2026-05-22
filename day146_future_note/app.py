import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day146：未来ノート"

DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day146_future_note.json"
)

ENERGY = [
    "🌱 少し",
    "✨ いい感じ",
    "🔥 ワクワク",
    "🌕 絶対やる"
]


def ensure_storage():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_PATH):

        with open(
            DATA_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "dreams": []
                },
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


def to_df(data):

    rows = []

    for x in data["dreams"]:

        rows.append({

            "date":
            x["created"],

            "dream":
            x["dream"],

            "step":
            x["step"],

            "energy":
            x["energy"],

            "done":
            x["done"]
        })

    return pd.DataFrame(rows)


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌌",
    layout="wide"
)

st.title("🌌 Day146：未来ノート")

st.caption(
    "未来を書く。小さく進む。"
)

data = load_data()

left, right = st.columns(
    [1,1]
)

with left:

    st.subheader(
        "未来を書く"
    )

    dream = st.text_input(
        "叶えたいこと",
        placeholder=
        "例：アプリを公開する"
    )

    future = st.text_area(
        "未来のイメージ",
        placeholder=
        "どうなっていたら嬉しい？"
    )

    step = st.text_input(
        "次の一歩",
        placeholder=
        "例：タイトルだけ考える"
    )

    energy = st.radio(
        "今の気持ち",
        ENERGY
    )

    if st.button(
        "🌌 保存",
        type="primary"
    ):

        if dream:

            item = {

                "id":
                datetime.now()
                .strftime(
                    "%Y%m%d%H%M%S"
                ),

                "created":
                date.today()
                .isoformat(),

                "dream":
                dream,

                "future":
                future,

                "step":
                step,

                "energy":
                energy,

                "done":
                False
            }

            data[
                "dreams"
            ].append(
                item
            )

            save_data(
                data
            )

            st.success(
                "未来を保存したよ"
            )

            st.rerun()

with right:

    st.subheader(
        "夢一覧"
    )

    for item in reversed(
        data["dreams"]
    ):

        done = st.checkbox(
            f"✅ {item['dream']}",
            value=
            item[
                "done"
            ],

            key=
            item[
                "id"
            ]
        )

        item[
            "done"
        ] = done

        with st.expander(
            "見る"
        ):

            st.write(
                f"未来：{item['future']}"
            )

            st.write(
                f"次：{item['step']}"
            )

            st.write(
                item[
                    "energy"
                ]
            )

    save_data(data)

st.divider()

st.subheader(
    "履歴"
)

df = to_df(
    data
)

if df.empty:

    st.write(
        "まだ未来がないよ"
    )

else:

    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )
