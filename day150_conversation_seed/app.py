import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day150：会話のタネメーカー"

DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day150_conversation_seed.json"
)

TOPICS = {

"家族":[
"最近一番笑ったことは？",
"次に旅行するならどこ？",
"子供の頃好きだった遊びは？",
"今日一番よかったことは？",
"最近食べておいしかったものは？"
],

"友達":[
"最近ハマってるものある？",
"次の休みに何したい？",
"おすすめしたいものある？",
"今やってみたいことは？"
],

"SNS":[
"最近考えていること",
"最近の小さな発見",
"今週やったこと",
"未来に向けて始めたいこと"
],

"自分":[
"今気になっていること",
"次に挑戦したいこと",
"今日できたこと",
"今の自分に必要なこと"
]
}


COMMENTS = [
"答えがなくても大丈夫。",
"軽く話すくらいでちょうどいいよ。",
"雑談って意外と楽しいんだよ。",
"全部埋めなくてもOK。"
]


def ensure():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(
        DATA_PATH
    ):

        with open(
            DATA_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {"logs":[]},
                f,
                ensure_ascii=False,
                indent=2
            )


def load():

    ensure()

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save(data):

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

    rows=[]

    for x in data["logs"]:

        rows.append({

            "date":
            x["date"],

            "theme":
            x["theme"],

            "seed":
            x["seed"],

            "memo":
            x["memo"]
        })

    return pd.DataFrame(
        rows
    )


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💬"
)

st.title(
"💬 Day150：会話のタネメーカー"
)

data = load()

theme = st.selectbox(
"テーマ",
list(
TOPICS.keys()
)
)

if st.button(
"💬 タネを出す",
type="primary"
):

    seed = random.choice(
        TOPICS[theme]
    )

    st.session_state[
        "seed"
    ] = seed

if (
"seed"
in st.session_state
):

    st.success(
        st.session_state[
            "seed"
        ]
    )

    st.info(
        random.choice(
            COMMENTS
        )
    )

    memo = st.text_area(
        "話した感想"
    )

    fav = st.checkbox(
        "⭐ お気に入り"
    )

    if st.button(
        "保存"
    ):

        data[
            "logs"
        ].append({

            "id":
            datetime.now()
            .strftime(
                "%Y%m%d%H%M%S"
            ),

            "date":
            date.today()
            .isoformat(),

            "theme":
            theme,

            "seed":
            st.session_state[
                "seed"
            ],

            "memo":
            memo,

            "favorite":
            fav
        })

        save(
            data
        )

        st.success(
            "保存したよ"
        )

st.divider()

df = to_df(
data
)

if not df.empty:

    st.subheader(
        "履歴"
    )

    st.dataframe(
        df,
        use_container_width=True
    )
