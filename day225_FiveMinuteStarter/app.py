import json
import os
import time
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="5分だけやる",
    page_icon="⏱️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "five_minute_data.json",
)

CATEGORIES = [
    "アプリ開発",
    "勉強",
    "読書",
    "イラスト",
    "運動",
    "家事",
    "仕事",
    "片付け",
    "発信",
    "ストレッチ",
    "その他",
]

MOODS = [
    "😩 やる気なし",
    "😕 少し重い",
    "😐 普通",
    "🙂 少しやる気あり",
    "🔥 やる気あり",
]

RESULTS = [
    "5分で終了",
    "もう5分続けた",
    "そのまま続けた",
]

RESULT_ICONS = {
    "5分で終了": "✅",
    "もう5分続けた": "▶️",
    "そのまま続けた": "🔥",
}


# =========================================================
# データ管理
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "tasks": [],
        "sessions": [],
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def normalize_data(data):
    if not isinstance(
        data,
        dict,
    ):
        data = create_empty_data()

    data.setdefault(
        "tasks",
        [],
    )

    data.setdefault(
        "sessions",
        [],
    )

    for task in data["tasks"]:
        task.setdefault(
            "id",
            create_id(),
        )

        task.setdefault(
            "name",
            "",
        )

        task.setdefault(
            "category",
            "その他",
        )

        task.setdefault(
            "memo",
            "",
        )

        task.setdefault(
            "active",
            True,
        )

        task.setdefault(
            "created_at",
            "",
        )

        task.setdefault(
            "updated_at",
            "",
        )

    for session in data["sessions"]:
        session.setdefault(
            "id",
            create_id(),
        )

        session.setdefault(
            "task_id",
            "",
        )

        session.setdefault(
            "task_name",
            "",
        )

        session.setdefault(
            "category",
            "その他",
        )

        session.setdefault(
            "session_date",
            str(date.today()),
        )

        session.setdefault(
            "started_at",
            "",
        )

        session.setdefault(
            "ended_at",
            "",
        )

        session.setdefault(
            "before_mood",
            "😐 普通",
        )

        session.setdefault(
            "after_mood",
            "😐 普通",
        )

        session.setdefault(
            "result",
            "5分で終了",
        )

        session.setdefault(
            "total_minutes",
            5,
        )

        session.setdefault(
            "memo",
            "",
        )

        session.setdefault(
            "created_at",
            "",
        )

    return data


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE,
    ):
        data = create_empty_data()
        save_data(data)

        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE,
            ):
                os.replace(
                    DATA_FILE,
                    broken_file,
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def parse_datetime(text):
    if not text:
        return None

    try:
        return datetime.fromisoformat(
            text
        )

    except ValueError:
        return None


def get_task_by_id(
    data,
    task_id,
):
    for task in data["tasks"]:
        if task.get(
            "id"
        ) == task_id:
            return task

    return None


def calculate_streak(
    sessions,
):
    recorded_dates = {
        session.get(
            "session_date"
        )
        for session in sessions
        if session.get(
            "session_date"
        )
    }

    if not recorded_dates:
        return 0

    current = date.today()

    if str(current) not in recorded_dates:
        current -= timedelta(
            days=1
        )

        if str(current) not in recorded_dates:
            return 0

    streak = 0

    while str(current) in recorded_dates:
        streak += 1

        current -= timedelta(
            days=1
        )

    return streak


def continuation_rate(
    sessions,
):
    if not sessions:
        return 0

    continued = len(
        [
            session
            for session in sessions
            if session.get(
                "result"
            )
            in [
                "もう5分続けた",
                "そのまま続けた",
            ]
        ]
    )

    return (
        continued
        / len(sessions)
        * 100
    )


def average_minutes(
    sessions,
):
    if not sessions:
        return 0

    values = [
        int(
            session.get(
                "total_minutes",
                0,
            )
        )
        for session in sessions
    ]

    if not values:
        return 0

    return (
        sum(values)
        / len(values)
    )


def mood_value(
    mood,
):
    try:
        return (
            MOODS.index(
                mood
            )
            + 1
        )

    except ValueError:
        return 3


# =========================================================
# データ操作
# =========================================================

def add_task(
    data,
    name,
    category,
    memo,
):
    data["tasks"].append(
        {
            "id": create_id(),
            "name": name,
            "category": category,
            "memo": memo,
            "active": True,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_task(
    data,
    task_id,
    values,
):
    task = get_task_by_id(
        data,
        task_id,
    )

    if not task:
        return

    for key, value in values.items():
        task[key] = value

    task["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_task(
    data,
    task_id,
):
    data["tasks"] = [
        task
        for task in data[
            "tasks"
        ]
        if task.get(
            "id"
        ) != task_id
    ]

    save_data(data)


def add_session(
    data,
    values,
):
    session = {
        "id": create_id(),
        "task_id": values[
            "task_id"
        ],
        "task_name": values[
            "task_name"
        ],
        "category": values[
            "category"
        ],
        "session_date": str(
            date.today()
        ),
        "started_at": values[
            "started_at"
        ],
        "ended_at": now_text(),
        "before_mood": values[
            "before_mood"
        ],
        "after_mood": values[
            "after_mood"
        ],
        "result": values[
            "result"
        ],
        "total_minutes": int(
            values[
                "total_minutes"
            ]
        ),
        "memo": values[
            "memo"
        ],
        "created_at": now_text(),
    }

    data["sessions"].append(
        session
    )

    save_data(data)


def delete_session(
    data,
    session_id,
):
    data["sessions"] = [
        session
        for session in data[
            "sessions"
        ]
        if session.get(
            "id"
        ) != session_id
    ]

    save_data(data)


# =========================================================
# デザイン
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(90, 150, 255, 0.08);
        border: 1px solid rgba(90, 150, 255, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(90, 150, 255, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(90, 150, 255, 0.18),
                rgba(90, 220, 180, 0.12)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }

    .timer {
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        padding: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 初期化
# =========================================================

data = load_data()

tasks = data[
    "tasks"
]

sessions = data[
    "sessions"
]

if (
    "timer_running"
    not in st.session_state
):
    st.session_state[
        "timer_running"
    ] = False

if (
    "timer_end_time"
    not in st.session_state
):
    st.session_state[
        "timer_end_time"
    ] = None

if (
    "current_task_id"
    not in st.session_state
):
    st.session_state[
        "current_task_id"
    ] = ""

if (
    "current_before_mood"
    not in st.session_state
):
    st.session_state[
        "current_before_mood"
    ] = "😐 普通"

if (
    "current_started_at"
    not in st.session_state
):
    st.session_state[
        "current_started_at"
    ] = ""

if (
    "timer_finished"
    not in st.session_state
):
    st.session_state[
        "timer_finished"
    ] = False


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⏱️ 5分だけやる</h1>
        <p>
            やる気が出るまで待たない。
            とりあえず5分だけ始めるためのアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_sessions = [
    session
    for session in sessions
    if session.get(
        "session_date"
    )
    == str(
        date.today()
    )
]

week_start = (
    date.today()
    - timedelta(
        days=6
    )
)

weekly_sessions = [
    session
    for session in sessions
    if (
        session.get(
            "session_date"
        )
        and week_start
        <= datetime.strptime(
            session.get(
                "session_date"
            ),
            "%Y-%m-%d"
        ).date()
        <= date.today()
    )
]

category_counter = Counter(
    session.get(
        "category",
        "その他"
    )
    for session in sessions
)

top_category = (
    category_counter.most_common(
        1
    )[0][0]
    if category_counter
    else "なし"
)

hour_counter = Counter()

for session in sessions:
    started_at = parse_datetime(
        session.get(
            "started_at"
        )
    )

    if started_at:
        hour_counter[
            started_at.hour
        ] += 1

top_hour = (
    hour_counter.most_common(
        1
    )[0][0]
    if hour_counter
    else None
)


metric_row1 = st.columns(
    4
)

metric_row1[0].metric(
    "今日のチャレンジ",
    f"{len(today_sessions)}回"
)

metric_row1[1].metric(
    "今週の実行",
    f"{len(weekly_sessions)}回"
)

metric_row1[2].metric(
    "累計実行",
    f"{len(sessions)}回"
)

metric_row1[3].metric(
    "連続実行",
    f"{calculate_streak(sessions)}日"
)


metric_row2 = st.columns(
    4
)

metric_row2[0].metric(
    "5分後も続けた率",
    f"{continuation_rate(sessions):.1f}%"
)

metric_row2[1].metric(
    "平均継続時間",
    f"{average_minutes(sessions):.1f}分"
)

metric_row2[2].metric(
    "最多カテゴリー",
    top_category
)

metric_row2[3].metric(
    "始めやすい時間",
    (
        f"{top_hour}時台"
        if top_hour
        is not None
        else "未記録"
    )
)


# =========================================================
# タイマー
# =========================================================

st.divider()

st.header(
    "🔥 5分チャレンジ"
)

active_tasks = [
    task
    for task in tasks
    if task.get(
        "active",
        True
    )
]

if not active_tasks:
    st.info(
        "まずは「やること管理」からタスクを登録しよう。"
    )

else:
    task_options = {
        (
            f"{task.get('name', '')}"
            f"｜{task.get('category', '')}"
        ): task["id"]
        for task in active_tasks
    }

    current_task_id = (
        st.session_state[
            "current_task_id"
        ]
    )

    current_label = next(
        (
            label
            for label, task_id
            in task_options.items()
            if task_id
            == current_task_id
        ),
        list(
            task_options.keys()
        )[0]
    )

    selected_task_label = (
        st.selectbox(
            "今から何を5分やる？",
            list(
                task_options.keys()
            ),
            index=list(
                task_options.keys()
            ).index(
                current_label
            ),
            disabled=(
                st.session_state[
                    "timer_running"
                ]
            )
        )
    )

    selected_task_id = (
        task_options[
            selected_task_label
        ]
    )

    selected_task = (
        get_task_by_id(
            data,
            selected_task_id
        )
    )

    before_mood = st.selectbox(
        "始める前の気分",
        MOODS,
        index=MOODS.index(
            st.session_state[
                "current_before_mood"
            ]
        ),
        disabled=(
            st.session_state[
                "timer_running"
            ]
        )
    )

    if not st.session_state[
        "timer_running"
    ] and not st.session_state[
        "timer_finished"
    ]:
        st.info(
            "5分で終わっても成功。"
            "まず始めることだけを目標にしよう。"
        )

        if st.button(
            "▶️ 5分スタート",
            use_container_width=True
        ):
            st.session_state[
                "timer_running"
            ] = True

            st.session_state[
                "timer_finished"
            ] = False

            st.session_state[
                "current_task_id"
            ] = selected_task_id

            st.session_state[
                "current_before_mood"
            ] = before_mood

            st.session_state[
                "current_started_at"
            ] = now_text()

            st.session_state[
                "timer_end_time"
            ] = (
                datetime.now()
                + timedelta(
                    minutes=5
                )
            )

            st.rerun()

    if st.session_state[
        "timer_running"
    ]:
        end_time = st.session_state[
            "timer_end_time"
        ]

        remaining = (
            end_time
            - datetime.now()
        ).total_seconds()

        if remaining <= 0:
            st.session_state[
                "timer_running"
            ] = False

            st.session_state[
                "timer_finished"
            ] = True

            st.rerun()

        remaining = int(
            remaining
        )

        minutes = (
            remaining
            // 60
        )

        seconds = (
            remaining
            % 60
        )

        st.markdown(
            f"""
            <div class="timer">
                {minutes:02d}:{seconds:02d}
            </div>
            """,
            unsafe_allow_html=True
        )

        current_task = (
            get_task_by_id(
                data,
                st.session_state[
                    "current_task_id"
                ]
            )
        )

        if current_task:
            st.subheader(
                current_task.get(
                    "name",
                    ""
                )
            )

        st.caption(
            "今は5分だけでOK。"
        )

        if st.button(
            "⏹️ 途中で終了",
            use_container_width=True
        ):
            st.session_state[
                "timer_running"
            ] = False

            st.session_state[
                "timer_finished"
            ] = True

            st.rerun()

        time.sleep(
            1
        )

        st.rerun()

    if st.session_state[
        "timer_finished"
    ]:
        current_task = (
            get_task_by_id(
                data,
                st.session_state[
                    "current_task_id"
                ]
            )
        )

        st.success(
            "🎉 5分できた！"
        )

        st.subheader(
            "どうする？"
        )

        with st.form(
            "finish_session_form"
        ):
            result = st.radio(
                "このあと",
                RESULTS,
                format_func=lambda value: (
                    f"{RESULT_ICONS.get(value, '')} "
                    f"{value}"
                )
            )

            total_minutes = 5

            if result == (
                "もう5分続けた"
            ):
                total_minutes = 10

            elif result == (
                "そのまま続けた"
            ):
                total_minutes = (
                    st.number_input(
                        "合計で何分続けた？",
                        min_value=6,
                        max_value=600,
                        value=20,
                        step=1
                    )
                )

            after_mood = st.selectbox(
                "終わった後の気分",
                MOODS,
                index=2
            )

            session_memo = (
                st.text_area(
                    "ひとことメモ",
                    placeholder=(
                        "例：始める前より気分が軽くなった"
                    )
                )
            )

            finish_submit = (
                st.form_submit_button(
                    "✅ 今日のチャレンジを記録",
                    use_container_width=True
                )
            )

            if finish_submit:
                if current_task:
                    add_session(
                        data,
                        {
                            "task_id": (
                                current_task[
                                    "id"
                                ]
                            ),
                            "task_name": (
                                current_task.get(
                                    "name",
                                    ""
                                )
                            ),
                            "category": (
                                current_task.get(
                                    "category",
                                    "その他"
                                )
                            ),
                            "started_at": (
                                st.session_state[
                                    "current_started_at"
                                ]
                            ),
                            "before_mood": (
                                st.session_state[
                                    "current_before_mood"
                                ]
                            ),
                            "after_mood": (
                                after_mood
                            ),
                            "result": result,
                            "total_minutes": (
                                total_minutes
                            ),
                            "memo": (
                                session_memo.strip()
                            ),
                        }
                    )

                st.session_state[
                    "timer_finished"
                ] = False

                st.session_state[
                    "current_task_id"
                ] = ""

                st.session_state[
                    "current_started_at"
                ] = ""

                st.session_state[
                    "timer_end_time"
                ] = None

                st.success(
                    "記録しました！5分でも立派な達成！"
                )

                st.balloons()
                st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    task_tab,
    history_tab,
    mood_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "📝 やること管理",
        "📚 実行履歴",
        "🙂 気分の変化",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# やること管理
# =========================================================

with task_tab:
    st.header(
        "📝 やること管理"
    )

    with st.form(
        "add_task_form",
        clear_on_submit=True
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            task_name = st.text_input(
                "やること",
                placeholder=(
                    "例：Reactのコードを読む"
                )
            )

        with column2:
            task_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES
                )
            )

        task_memo = st.text_area(
            "メモ",
            placeholder=(
                "最初の目標や、取りかかり方"
            )
        )

        submitted = (
            st.form_submit_button(
                "➕ やることを登録",
                use_container_width=True
            )
        )

        if submitted:
            if not task_name.strip():
                st.error(
                    "やることを入力してください。"
                )

            else:
                add_task(
                    data,
                    task_name.strip(),
                    task_category,
                    task_memo.strip()
                )

                st.rerun()

    st.divider()

    if not tasks:
        st.info(
            "やることはまだ登録されていません。"
        )

    for task in tasks:
        task_id = task[
            "id"
        ]

        task_sessions = [
            session
            for session in sessions
            if session.get(
                "task_id"
            )
            == task_id
        ]

        with st.container(
            border=True
        ):
            column1, column2 = (
                st.columns(
                    [
                        4,
                        1,
                    ]
                )
            )

            with column1:
                st.markdown(
                    f"### "
                    f"{task.get('name', '')}"
                )

                st.caption(
                    task.get(
                        "category",
                        ""
                    )
                )

                if task.get(
                    "memo",
                    ""
                ):
                    st.write(
                        task.get(
                            "memo",
                            ""
                        )
                    )

            with column2:
                st.metric(
                    "実行回数",
                    len(
                        task_sessions
                    )
                )

            with st.expander(
                "✏️ 編集"
            ):
                edit_name = (
                    st.text_input(
                        "やること",
                        value=task.get(
                            "name",
                            ""
                        ),
                        key=(
                            f"edit_task_name_"
                            f"{task_id}"
                        )
                    )
                )

                current_category = (
                    task.get(
                        "category",
                        "その他"
                    )
                )

                edit_category = (
                    st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=(
                            CATEGORIES.index(
                                current_category
                            )
                            if current_category
                            in CATEGORIES
                            else (
                                len(
                                    CATEGORIES
                                )
                                - 1
                            )
                        ),
                        key=(
                            f"edit_task_category_"
                            f"{task_id}"
                        )
                    )
                )

                edit_memo = (
                    st.text_area(
                        "メモ",
                        value=task.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_task_memo_"
                            f"{task_id}"
                        )
                    )
                )

                edit_active = (
                    st.checkbox(
                        "使用中",
                        value=bool(
                            task.get(
                                "active",
                                True
                            )
                        ),
                        key=(
                            f"edit_task_active_"
                            f"{task_id}"
                        )
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_task_"
                        f"{task_id}"
                    ),
                    use_container_width=True
                ):
                    if not edit_name.strip():
                        st.error(
                            "やることを入力してください。"
                        )

                    else:
                        update_task(
                            data,
                            task_id,
                            {
                                "name": (
                                    edit_name.strip()
                                ),
                                "category": (
                                    edit_category
                                ),
                                "memo": (
                                    edit_memo.strip()
                                ),
                                "active": (
                                    edit_active
                                ),
                            }
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                confirm_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_task_delete_"
                            f"{task_id}"
                        )
                    )
                )

                if st.button(
                    "このやることを削除",
                    key=(
                        f"delete_task_"
                        f"{task_id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True
                ):
                    delete_task(
                        data,
                        task_id
                    )

                    st.rerun()


# =========================================================
# 実行履歴
# =========================================================

with history_tab:
    st.header(
        "📚 5分チャレンジ履歴"
    )

    if not sessions:
        st.info(
            "実行履歴はまだありません。"
        )

    else:
        category_filter = (
            st.selectbox(
                "カテゴリー",
                [
                    "すべて"
                ]
                + CATEGORIES
            )
        )

        filtered_sessions = list(
            sessions
        )

        if category_filter != (
            "すべて"
        ):
            filtered_sessions = [
                session
                for session
                in filtered_sessions
                if session.get(
                    "category"
                )
                == category_filter
            ]

        filtered_sessions.sort(
            key=lambda session: (
                session.get(
                    "started_at",
                    ""
                )
            ),
            reverse=True
        )

        for session in filtered_sessions:
            session_id = (
                session[
                    "id"
                ]
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### "
                    f"{RESULT_ICONS.get(session.get('result', ''), '')} "
                    f"{session.get('task_name', '')}"
                )

                st.caption(
                    f"{session.get('session_date', '')} ／ "
                    f"{session.get('category', '')}"
                )

                columns = st.columns(
                    4
                )

                columns[0].metric(
                    "時間",
                    f"{session.get('total_minutes', 0)}分"
                )

                columns[1].metric(
                    "結果",
                    session.get(
                        "result",
                        ""
                    )
                )

                columns[2].metric(
                    "開始前",
                    session.get(
                        "before_mood",
                        ""
                    )
                )

                columns[3].metric(
                    "終了後",
                    session.get(
                        "after_mood",
                        ""
                    )
                )

                if session.get(
                    "memo",
                    ""
                ):
                    st.info(
                        session.get(
                            "memo",
                            ""
                        )
                    )

                with st.expander(
                    "🗑️ 履歴を削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_session_delete_"
                                f"{session_id}"
                            )
                        )
                    )

                    if st.button(
                        "この履歴を削除",
                        key=(
                            f"delete_session_"
                            f"{session_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_session(
                            data,
                            session_id
                        )

                        st.rerun()


# =========================================================
# 気分の変化
# =========================================================

with mood_tab:
    st.header(
        "🙂 始める前と後の気分"
    )

    if not sessions:
        st.info(
            "気分データはまだありません。"
        )

    else:
        improved = 0
        same = 0
        declined = 0

        mood_rows = []

        for session in sessions:
            before = mood_value(
                session.get(
                    "before_mood",
                    "😐 普通"
                )
            )

            after = mood_value(
                session.get(
                    "after_mood",
                    "😐 普通"
                )
            )

            difference = (
                after
                - before
            )

            if difference > 0:
                improved += 1

            elif difference == 0:
                same += 1

            else:
                declined += 1

            mood_rows.append(
                {
                    "日付": (
                        session.get(
                            "session_date",
                            ""
                        )
                    ),
                    "タスク": (
                        session.get(
                            "task_name",
                            ""
                        )
                    ),
                    "開始前": before,
                    "終了後": after,
                    "変化": difference,
                }
            )

        mood_columns = (
            st.columns(3)
        )

        mood_columns[0].metric(
            "気分アップ",
            f"{improved}回"
        )

        mood_columns[1].metric(
            "変化なし",
            f"{same}回"
        )

        mood_columns[2].metric(
            "気分ダウン",
            f"{declined}回"
        )

        mood_df = pd.DataFrame(
            mood_rows
        )

        st.line_chart(
            mood_df.set_index(
                "日付"
            )[
                [
                    "開始前",
                    "終了後",
                ]
            ]
        )

        if sessions:
            improvement_rate = (
                improved
                / len(sessions)
                * 100
            )

            st.success(
                f"5分始めたあとに気分が良くなった割合："
                f"**{improvement_rate:.1f}%**"
            )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 行動分析"
    )

    if not sessions:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for session in sessions:
            started_at = (
                parse_datetime(
                    session.get(
                        "started_at",
                        ""
                    )
                )
            )

            analysis_rows.append(
                {
                    "日付": (
                        session.get(
                            "session_date",
                            ""
                        )
                    ),
                    "カテゴリー": (
                        session.get(
                            "category",
                            ""
                        )
                    ),
                    "タスク": (
                        session.get(
                            "task_name",
                            ""
                        )
                    ),
                    "結果": (
                        session.get(
                            "result",
                            ""
                        )
                    ),
                    "時間": int(
                        session.get(
                            "total_minutes",
                            0
                        )
                    ),
                    "開始時刻": (
                        started_at.hour
                        if started_at
                        else None
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "カテゴリー別実行回数"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False
            )
            .agg(
                実行回数=(
                    "タスク",
                    "count"
                ),
                合計時間=(
                    "時間",
                    "sum"
                ),
            )
            .sort_values(
                "実行回数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["実行回数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "結果別"
        )

        result_summary = (
            analysis_df.groupby(
                "結果",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "回数"
                }
            )
            .sort_values(
                "回数",
                ascending=False
            )
        )

        st.bar_chart(
            result_summary.set_index(
                "結果"
            )[["回数"]]
        )

        st.dataframe(
            result_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "日別実行時間"
        )

        daily_summary = (
            analysis_df.groupby(
                "日付",
                as_index=False
            )
            .agg(
                実行回数=(
                    "タスク",
                    "count"
                ),
                合計時間=(
                    "時間",
                    "sum"
                ),
            )
            .sort_values(
                "日付"
            )
        )

        st.line_chart(
            daily_summary.set_index(
                "日付"
            )[
                [
                    "合計時間"
                ]
            ]
        )

        st.dataframe(
            daily_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "始めやすい時間帯"
        )

        hour_df = (
            analysis_df.dropna(
                subset=[
                    "開始時刻"
                ]
            )
        )

        if hour_df.empty:
            st.info(
                "開始時刻を分析できません。"
            )

        else:
            hour_summary = (
                hour_df.groupby(
                    "開始時刻",
                    as_index=False
                )
                .size()
                .rename(
                    columns={
                        "size": "実行回数"
                    }
                )
                .sort_values(
                    "開始時刻"
                )
            )

            hour_summary[
                "時間帯"
            ] = hour_summary[
                "開始時刻"
            ].apply(
                lambda hour: (
                    f"{int(hour)}時"
                )
            )

            st.bar_chart(
                hour_summary.set_index(
                    "時間帯"
                )[["実行回数"]]
            )

            st.dataframe(
                hour_summary[
                    [
                        "時間帯",
                        "実行回数",
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "よくやるタスク"
        )

        task_summary = (
            analysis_df.groupby(
                "タスク",
                as_index=False
            )
            .agg(
                実行回数=(
                    "タスク",
                    "count"
                ),
                合計時間=(
                    "時間",
                    "sum"
                ),
            )
            .sort_values(
                "実行回数",
                ascending=False
            )
        )

        st.dataframe(
            task_summary,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# データ管理
# =========================================================

with data_tab:
    st.header(
        "💾 データ管理"
    )

    st.subheader(
        "JSONバックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"five_minute_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = (
        st.file_uploader(
            "バックアップJSONを選択",
            type=[
                "json"
            ]
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = (
                json.load(
                    uploaded_file
                )
            )

            if (
                not isinstance(
                    imported_data,
                    dict
                )
                or "tasks"
                not in imported_data
                or "sessions"
                not in imported_data
            ):
                st.error(
                    "対応していないJSON形式です。"
                )

            else:
                imported_data = (
                    normalize_data(
                        imported_data
                    )
                )

                st.warning(
                    "復元すると現在のデータが上書きされます。"
                )

                confirm_restore = (
                    st.checkbox(
                        "上書き復元を確認しました"
                    )
                )

                if st.button(
                    "JSONから復元",
                    disabled=(
                        not confirm_restore
                    ),
                    use_container_width=True
                ):
                    save_data(
                        imported_data
                    )

                    st.success(
                        "データを復元しました！"
                    )

                    st.rerun()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "やること・5分チャレンジ履歴がすべて削除されます。"
    )

    confirm_delete_all = (
        st.checkbox(
            "全データ削除を確認しました"
        )
    )

    if st.button(
        "すべて削除",
        disabled=(
            not confirm_delete_all
        ),
        use_container_width=True
    ):
        save_data(
            create_empty_data()
        )

        st.success(
            "すべてのデータを削除しました。"
        )

        st.rerun()


# =========================================================
# フッター
# =========================================================

st.divider()

st.success(
    "5分で終わっても成功。始められたことが、今日の一歩。⏱️"
)
