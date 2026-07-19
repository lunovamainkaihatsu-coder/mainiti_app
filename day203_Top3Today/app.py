import json
import os
from datetime import date

import streamlit as st


st.set_page_config(
    page_title="今日の優先順位3つ",
    page_icon="🎯",
    layout="centered"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "priorities.json"
)


def save_data(data):
    """優先順位データをJSONへ保存する"""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_data():
    """優先順位データをJSONから読み込む"""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        save_data({})
        return {}

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    save_data({})
    return {}


def create_empty_day():
    """1日分の空データを作る"""
    return {
        "tasks": [
            {
                "title": "",
                "completed": False
            },
            {
                "title": "",
                "completed": False
            },
            {
                "title": "",
                "completed": False
            }
        ]
    }


data = load_data()

today_key = str(date.today())

if today_key not in data:
    data[today_key] = create_empty_day()
    save_data(data)


today_data = data[today_key]
today_tasks = today_data.get(
    "tasks",
    create_empty_day()["tasks"]
)


st.title("🎯 今日の優先順位3つ")

st.caption(
    "今日、本当に大切なことを"
    "3つだけ決めよう。"
)

st.write(
    date.today().strftime(
        "%Y年%m月%d日"
    )
)

st.divider()


st.header("✍️ 今日やること")

with st.form(
    "priority_form"
):
    task1 = st.text_input(
        "🥇 1位",
        value=today_tasks[0].get(
            "title",
            ""
        ),
        placeholder=(
            "例：アプリを完成させる"
        )
    )

    task2 = st.text_input(
        "🥈 2位",
        value=today_tasks[1].get(
            "title",
            ""
        ),
        placeholder=(
            "例：noteを投稿する"
        )
    )

    task3 = st.text_input(
        "🥉 3位",
        value=today_tasks[2].get(
            "title",
            ""
        ),
        placeholder=(
            "例：軽く筋トレする"
        )
    )

    save_button = st.form_submit_button(
        "💾 優先順位を保存",
        use_container_width=True
    )

    if save_button:
        new_titles = [
            task1.strip(),
            task2.strip(),
            task3.strip()
        ]

        for index, title in enumerate(
            new_titles
        ):
            today_tasks[index][
                "title"
            ] = title

        data[today_key][
            "tasks"
        ] = today_tasks

        save_data(data)

        st.success(
            "今日の優先順位を"
            "保存しました！"
        )

        st.rerun()


st.divider()


st.header("✅ 今日の進捗")

rank_labels = [
    "🥇 1位",
    "🥈 2位",
    "🥉 3位"
]

changed = False

for index, task in enumerate(
    today_tasks
):
    title = task.get(
        "title",
        ""
    )

    if not title:
        st.info(
            f"{rank_labels[index]}は"
            "まだ登録されていません。"
        )
        continue

    completed = st.checkbox(
        f"{rank_labels[index]}　{title}",
        value=task.get(
            "completed",
            False
        ),
        key=f"task_{today_key}_{index}"
    )

    if completed != task.get(
        "completed",
        False
    ):
        today_tasks[index][
            "completed"
        ] = completed
        changed = True


if changed:
    data[today_key][
        "tasks"
    ] = today_tasks

    save_data(data)

    st.rerun()


registered_tasks = [
    task
    for task in today_tasks
    if task.get(
        "title",
        ""
    ).strip()
]

completed_count = sum(
    1
    for task in registered_tasks
    if task.get(
        "completed",
        False
    )
)

registered_count = len(
    registered_tasks
)

if registered_count > 0:
    progress = (
        completed_count
        / registered_count
    )

else:
    progress = 0


st.divider()

st.subheader("📊 今日の達成率")

st.progress(progress)

st.write(
    f"**{completed_count} / "
    f"{registered_count}件達成**"
)

st.write(
    f"達成率："
    f"**{int(progress * 100)}％**"
)


if registered_count == 0:
    st.info(
        "まずは今日やることを"
        "1つ登録してみよう。"
    )

elif progress == 1:
    st.success(
        "🎉 今日の優先順位を"
        "すべて達成しました！"
    )

elif progress >= 0.67:
    st.success(
        "🔥 あと少し！"
        "かなり良いペースです。"
    )

elif progress > 0:
    st.info(
        "🌱 ひとつ達成できました。"
        "着実に進んでいます。"
    )

else:
    st.info(
        "まずは1位から、"
        "少しだけ始めてみよう。"
    )


st.divider()


st.header("📚 過去の記録")

past_dates = sorted(
    [
        saved_date
        for saved_date in data.keys()
        if saved_date != today_key
    ],
    reverse=True
)


if not past_dates:
    st.info(
        "過去の記録は"
        "まだありません。"
    )

else:
    selected_date = st.selectbox(
        "確認する日",
        past_dates
    )

    past_tasks = data[
        selected_date
    ].get(
        "tasks",
        []
    )

    past_registered = [
        task
        for task in past_tasks
        if task.get(
            "title",
            ""
        ).strip()
    ]

    past_completed = sum(
        1
        for task in past_registered
        if task.get(
            "completed",
            False
        )
    )

    st.subheader(
        selected_date.replace(
            "-",
            "/"
        )
    )

    for index, task in enumerate(
        past_tasks
    ):
        title = task.get(
            "title",
            ""
        )

        if not title:
            continue

        mark = (
            "✅"
            if task.get(
                "completed",
                False
            )
            else "⬜"
        )

        st.write(
            f"{rank_labels[index]} "
            f"{mark} {title}"
        )

    if past_registered:
        past_progress = (
            past_completed
            / len(
                past_registered
            )
        )

        st.progress(
            past_progress
        )

        st.caption(
            f"{past_completed} / "
            f"{len(past_registered)}件達成"
        )


st.divider()

st.success(
    "今日は3つで十分。"
    "大切なことから進めよう。🎯"
)
