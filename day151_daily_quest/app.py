import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day151：今日のクエスト掲示板"

DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day151_daily_quest.json"
)

QUESTS = [

{
"title":"💧 水を飲め！",
"desc":"まず一口でもOK。",
"exp":5
},

{
"title":"🧘 深呼吸せよ！",
"desc":"ゆっくり3回。",
"exp":8
},

{
"title":"💻 5分開発！",
"desc":"開くだけでもOK。",
"exp":15
},

{
"title":"📚 本を1ページ読め！",
"desc":"少しだけ知識を増やそう。",
"exp":10
},

{
"title":"🚶 外の空気を吸え！",
"desc":"ベランダでもOK。",
"exp":12
},

{
"title":"🧹 1か所片付けろ！",
"desc":"机の上だけでもOK。",
"exp":10
},

{
"title":"🌌 未来ノートを開け！",
"desc":"夢を1個見る。",
"exp":15
},

{
"title":"🙏 ありがとうを1個探せ！",
"desc":"小さいことでOK。",
"exp":8
},

{
"title":"💪 ストレッチせよ！",
"desc":"首だけでもOK。",
"exp":10
}
]


COMMENTS = [

"小さい達成でも経験値だよ。",
"ゼロじゃなければ勝ち！",
"今日のご主人、ちゃんと進んでる。",
"軽く積むのが強いんだよ。"
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
                {
                    "logs":[]
                },
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

            "quest":
            x["quest"],

            "exp":
            x["exp"],

            "done":
            x["done"]
        })

    return pd.DataFrame(
        rows
    )


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚔️",
    layout="wide"
)

st.title(
"⚔️ Day151：今日のクエスト掲示板"
)

st.caption(
"今日の小さなクエスト。"
)

data = load()

if "quest" not in st.session_state:

    st.session_state[
        "quest"
    ] = None


left,right = st.columns(
    [1,1]
)

with left:

    st.subheader(
        "クエスト受注"
    )

    if st.button(
        "⚔️ クエスト生成",
        type="primary"
    ):

        quest = random.choice(
            QUESTS
        )

        st.session_state[
            "quest"
        ] = quest

        st.rerun()


with right:

    st.subheader(
        "今日のクエスト"
    )

    quest = st.session_state.get(
        "quest"
    )

    if quest:

        st.markdown(
            f"## {quest['title']}"
        )

        st.write(
            quest["desc"]
        )

        st.metric(
            "EXP",
            quest["exp"]
        )

        st.info(
            random.choice(
                COMMENTS
            )
        )

        done = st.checkbox(
            "✅ 達成！"
        )

        memo = st.text_area(
            "メモ"
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

                "quest":
                quest[
                    "title"
                ],

                "exp":
                quest[
                    "exp"
                ],

                "done":
                done,

                "memo":
                memo
            })

            save(
                data
            )

            st.success(
                "クエスト保存！"
            )

st.divider()

df = to_df(
    data
)

if not df.empty:

    st.subheader(
        "履歴"
    )

    total_exp = int(
        df["exp"].sum()
    )

    st.metric(
        "総EXP",
        total_exp
    )

    level = (
        total_exp // 100
    ) + 1

    st.metric(
        "レベル",
        level
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=300
    )
