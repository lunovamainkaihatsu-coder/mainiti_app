import streamlit as st
import json
import os
from datetime import datetime, date, time
import pandas as pd

APP_TITLE = "Day152：やったことタイムライン"

DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day152_timeline_log.json"
)

CATEGORIES = [

"生活",
"仕事",
"開発",
"勉強",
"回復",
"運動",
"趣味",
"家族",
"その他"
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

            "time":
            x["time"],

            "category":
            x["category"],

            "title":
            x["title"],

            "memo":
            x["memo"]
        })

    df = pd.DataFrame(
        rows
    )

    if not df.empty:

        df = df.sort_values(
            ["date","time"],
            ascending=False
        )

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🕒",
    layout="wide"
)

st.title(
"🕒 Day152：やったことタイムライン"
)

st.caption(
"今日やったことを時系列で残す。"
)

data = load()

left,right = st.columns(
    [1,1]
)

with left:

    st.subheader(
        "記録する"
    )

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    log_time = st.time_input(
        "時間",
        value=datetime.now().time()
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    title = st.text_input(
        "やったこと",
        placeholder=
        "例：アプリ修正"
    )

    memo = st.text_area(
        "メモ"
    )

    if st.button(
        "🕒 保存",
        type="primary"
    ):

        if title:

            data[
                "logs"
            ].append({

                "id":
                datetime.now()
                .strftime(
                    "%Y%m%d%H%M%S"
                ),

                "date":
                log_date
                .isoformat(),

                "time":
                log_time
                .strftime(
                    "%H:%M"
                ),

                "category":
                category,

                "title":
                title,

                "memo":
                memo
            })

            save(
                data
            )

            st.success(
                "保存したよ！"
            )

            st.rerun()

with right:

    st.subheader(
        "今日のタイムライン"
    )

    today_logs = [

        x for x
        in data["logs"]

        if x["date"]
        ==
        date.today()
        .isoformat()
    ]

    if today_logs:

        sorted_logs = sorted(

            today_logs,

            key=lambda x:
            x["time"]
        )

        for log in sorted_logs:

            st.markdown(
                f"""
### {log['time']}｜{log['title']}

**カテゴリ**
{log['category']}

{log['memo']}
"""
            )

            st.divider()

    else:

        st.info(
            "まだ記録がないよ"
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
        use_container_width=True,
        height=300
    )
