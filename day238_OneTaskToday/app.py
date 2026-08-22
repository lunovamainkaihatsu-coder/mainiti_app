import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の1個",
    page_icon="🎯",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "one_task_data.json",
)


# =========================================================
# データ管理
# =========================================================

def create_empty_data():
    return {
        "tasks": []
    }


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


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


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = create_empty_data()

        save_data(
            data
        )

        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "tasks",
            [],
        )

        for task in data[
            "tasks"
        ]:
            task.setdefault(
                "date",
                str(
                    date.today()
                ),
            )

            task.setdefault(
                "task",
                "",
            )

            task.setdefault(
                "completed",
                False,
            )

            task.setdefault(
                "result_memo",
                "",
            )

            task.setdefault(
                "created_at",
                "",
            )

            task.setdefault(
                "completed_at",
                "",
            )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = create_empty_data()

        save_data(
            data
        )

        return data


# =========================================================
# 補助関数
# =========================================================

def get_task_for_date(
    data,
    target_date,
):
    target_text = str(
        target_date
    )

    return next(
        (
            task
            for task in data[
                "tasks"
            ]
            if task.get(
                "date"
            ) == target_text
        ),
        None,
    )


def format_date(
    date_text,
):
    try:
        target = datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

        weekdays = [
            "月",
            "火",
            "水",
            "木",
            "金",
            "土",
            "日",
        ]

        weekday = weekdays[
            target.weekday()
        ]

        return target.strftime(
            f"%Y年%m月%d日（{weekday}）"
        )

    except ValueError:
        return date_text


def calculate_streak(
    tasks,
):
    completed_dates = {
        task.get(
            "date"
        )
        for task in tasks
        if task.get(
            "completed",
            False,
        )
    }

    if not completed_dates:
        return 0

    current = date.today()

    if str(current) not in completed_dates:
        current -= timedelta(
            days=1
        )

        if str(current) not in completed_dates:
            return 0

    streak = 0

    while str(current) in completed_dates:
        streak += 1

        current -= timedelta(
            days=1
        )

    return streak


# =========================================================
# データ操作
# =========================================================

def save_today_task(
    data,
    task_text,
):
    today = date.today()

    existing = get_task_for_date(
        data,
        today,
    )

    if existing:
        existing[
            "task"
        ] = task_text

    else:
        data[
            "tasks"
        ].append(
            {
                "date": str(
                    today
                ),
                "task": task_text,
                "completed": False,
                "result_memo": "",
                "created_at": (
                    now_text()
                ),
                "completed_at": "",
            }
        )

    save_data(
        data
    )


def complete_today_task(
    data,
    memo,
):
    task = get_task_for_date(
        data,
        date.today(),
    )

    if not task:
        return

    task[
        "completed"
    ] = True

    task[
        "result_memo"
    ] = memo

    task[
        "completed_at"
    ] = now_text()

    save_data(
        data
    )


def undo_today_completion(
    data,
):
    task = get_task_for_date(
        data,
        date.today(),
    )

    if not task:
        return

    task[
        "completed"
    ] = False

    task[
        "completed_at"
    ] = ""

    save_data(
        data
    )


def delete_today_task(
    data,
):
    today_text = str(
        date.today()
    )

    data[
        "tasks"
    ] = [
        task
        for task in data[
            "tasks"
        ]
        if task.get(
            "date"
        ) != today_text
    ]

    save_data(
        data
    )


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
        padding: 22px;
        border-radius: 20px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 150, 255, 0.18),
                rgba(120, 210, 170, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.75;
    }

    .today-task {
        text-align: center;
        padding: 28px 20px;
        border-radius: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        background: rgba(90, 150, 255, 0.06);
    }

    .today-task-text {
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.5;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

tasks = data[
    "tasks"
]

today = date.today()

today_task = get_task_for_date(
    data,
    today,
)

current_month = today.strftime(
    "%Y-%m"
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🎯 今日の1個</h1>
        <p>
            今日これだけ終わればOK。
            1日1個だけ決めるタスクアプリ。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

monthly_tasks = [
    task
    for task in tasks
    if task.get(
        "date",
        "",
    ).startswith(
        current_month
    )
]

monthly_completed = [
    task
    for task in monthly_tasks
    if task.get(
        "completed",
        False,
    )
]

streak = calculate_streak(
    tasks
)


columns = st.columns(
    3
)

columns[0].metric(
    "今日",
    (
        "✅ 達成"
        if (
            today_task
            and today_task.get(
                "completed",
                False,
            )
        )
        else "未達成"
        if today_task
        else "未設定"
    ),
)

columns[1].metric(
    "連続達成",
    f"{streak}日",
)

columns[2].metric(
    "今月",
    f"{len(monthly_completed)}日達成",
)


# =========================================================
# 今日の1個
# =========================================================

st.divider()

st.subheader(
    "🌱 今日の1個"
)

if not today_task:
    with st.form(
        "today_task_form"
    ):
        task_text = st.text_input(
            "今日は何を1個やる？",
            placeholder=(
                "例：アプリのコードを10分だけ読む"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🎯 今日の1個に決定",
                use_container_width=True,
            )
        )

        if submitted:
            if not task_text.strip():
                st.error(
                    "今日やることを入力してください。"
                )

            else:
                save_today_task(
                    data,
                    task_text.strip(),
                )

                st.success(
                    "今日の1個を決めました！"
                )

                st.rerun()

else:
    st.markdown(
        f"""
        <div class="today-task">
            <div class="today-task-text">
                {today_task.get('task', '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not today_task.get(
        "completed",
        False,
    ):
        st.info(
            "今日はこれだけ終わればOK。"
        )

        with st.form(
            "complete_task_form"
        ):
            result_memo = st.text_input(
                "終わったら一言",
                placeholder=(
                    "例：10分のつもりが20分できた！"
                ),
            )

            complete = (
                st.form_submit_button(
                    "✅ できた！",
                    use_container_width=True,
                )
            )

            if complete:
                complete_today_task(
                    data,
                    result_memo.strip(),
                )

                st.success(
                    "🎉 今日の1個、達成！"
                )

                st.balloons()
                st.rerun()

        with st.expander(
            "✏️ 今日の1個を変更"
        ):
            edit_text = st.text_input(
                "今日の1個",
                value=today_task.get(
                    "task",
                    "",
                ),
            )

            if st.button(
                "変更を保存",
                use_container_width=True,
            ):
                if not edit_text.strip():
                    st.error(
                        "内容を入力してください。"
                    )

                else:
                    save_today_task(
                        data,
                        edit_text.strip(),
                    )

                    st.rerun()

    else:
        st.success(
            "🎉 今日の1個、達成！今日はこれでOK。"
        )

        if today_task.get(
            "result_memo",
            "",
        ):
            st.write(
                f"「"
                f"{today_task.get('result_memo', '')}"
                f"」"
            )

        if st.button(
            "↩️ 完了を取り消す",
            use_container_width=True,
        ):
            undo_today_completion(
                data
            )

            st.rerun()

    with st.expander(
        "🗑️ 今日の1個を削除"
    ):
        if st.button(
            "削除する",
            use_container_width=True,
        ):
            delete_today_task(
                data
            )

            st.rerun()


# =========================================================
# 最近7日間
# =========================================================

st.divider()

st.subheader(
    "📅 最近7日間"
)

week_start = (
    today
    - timedelta(
        days=6
    )
)

week_rows = []

for i in range(
    7
):
    target_date = (
        week_start
        + timedelta(
            days=i
        )
    )

    target_task = get_task_for_date(
        data,
        target_date,
    )

    week_rows.append(
        {
            "日付": target_date.strftime(
                "%m/%d"
            ),
            "今日の1個": (
                target_task.get(
                    "task",
                    "",
                )
                if target_task
                else ""
            ),
            "達成": (
                "✅"
                if (
                    target_task
                    and target_task.get(
                        "completed",
                        False,
                    )
                )
                else "—"
            ),
        }
    )

week_df = pd.DataFrame(
    week_rows
)

st.dataframe(
    week_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# 今月の達成率
# =========================================================

st.divider()

st.subheader(
    "📊 今月"
)

if not monthly_tasks:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    monthly_rate = (
        len(
            monthly_completed
        )
        / len(
            monthly_tasks
        )
    )

    st.progress(
        monthly_rate
    )

    st.write(
        f"**{len(monthly_completed)} / "
        f"{len(monthly_tasks)}日 達成**"
    )

    st.caption(
        f"達成率："
        f"{monthly_rate * 100:.1f}%"
    )


# =========================================================
# 過去の今日の1個
# =========================================================

st.divider()

with st.expander(
    "📚 過去の「今日の1個」"
):
    if not tasks:
        st.info(
            "まだ履歴がありません。"
        )

    else:
        sorted_tasks = sorted(
            tasks,
            key=lambda task: (
                task.get(
                    "date",
                    "",
                )
            ),
            reverse=True,
        )

        history_rows = []

        for task in sorted_tasks:
            history_rows.append(
                {
                    "日付": format_date(
                        task.get(
                            "date",
                            "",
                        )
                    ),
                    "今日の1個": (
                        task.get(
                            "task",
                            "",
                        )
                    ),
                    "結果": (
                        "✅ 達成"
                        if task.get(
                            "completed",
                            False,
                        )
                        else "未達成"
                    ),
                    "ひとこと": (
                        task.get(
                            "result_memo",
                            "",
                        )
                    ),
                }
            )

        history_df = pd.DataFrame(
            history_rows
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# バックアップ
# =========================================================

st.divider()

with st.expander(
    "💾 データ管理"
):
    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            f"one_task_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "全部やらなくていい。今日の1個だけ終わらせよう。🎯"
)
