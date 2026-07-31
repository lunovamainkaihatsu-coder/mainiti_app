import json
import os
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の優先順位3つ",
    page_icon="🎯",
    layout="wide"
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "top3_data.json"
)

CATEGORIES = [
    "アプリ開発",
    "仕事",
    "発信",
    "学習",
    "健康",
    "運動",
    "家族",
    "家事",
    "お金",
    "趣味",
    "休息",
    "その他",
]

STATUSES = [
    "未着手",
    "進行中",
    "完了",
    "中止",
    "翌日に繰り越し",
]

STATUS_ICONS = {
    "未着手": "⚪",
    "進行中": "🔵",
    "完了": "✅",
    "中止": "⛔",
    "翌日に繰り越し": "➡️",
}

PRIORITY_ICONS = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
}


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作成する。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    """初期データを作成する。"""

    return {
        "days": []
    }


def save_data(data):
    """JSONファイルへデータを保存する。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

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


def normalize_data(data):
    """保存データに不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "days",
        []
    )

    for day_data in data["days"]:
        day_data.setdefault(
            "id",
            create_id()
        )

        day_data.setdefault(
            "target_date",
            str(date.today())
        )

        day_data.setdefault(
            "tasks",
            []
        )

        day_data.setdefault(
            "not_do",
            ""
        )

        day_data.setdefault(
            "good_point",
            ""
        )

        day_data.setdefault(
            "failure_reason",
            ""
        )

        day_data.setdefault(
            "tomorrow_improvement",
            ""
        )

        day_data.setdefault(
            "focus_score",
            0
        )

        day_data.setdefault(
            "satisfaction_score",
            0
        )

        day_data.setdefault(
            "reviewed",
            False
        )

        day_data.setdefault(
            "created_at",
            ""
        )

        day_data.setdefault(
            "updated_at",
            ""
        )

        for task in day_data["tasks"]:
            task.setdefault(
                "id",
                create_id()
            )

            task.setdefault(
                "title",
                ""
            )

            task.setdefault(
                "priority",
                1
            )

            task.setdefault(
                "category",
                "その他"
            )

            task.setdefault(
                "estimated_minutes",
                30
            )

            task.setdefault(
                "actual_minutes",
                0
            )

            task.setdefault(
                "reason",
                ""
            )

            task.setdefault(
                "status",
                "未着手"
            )

            task.setdefault(
                "memo",
                ""
            )

            task.setdefault(
                "completed_at",
                ""
            )

            task.setdefault(
                "carried_from",
                ""
            )

            task.setdefault(
                "carried_to",
                ""
            )

            task.setdefault(
                "created_at",
                ""
            )

            task.setdefault(
                "updated_at",
                ""
            )

    return data


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = create_empty_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE
            ):
                os.replace(
                    DATA_FILE,
                    broken_file
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def parse_date(date_text):
    """日付文字列をdate型へ変換する。"""

    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except (
        TypeError,
        ValueError
    ):
        return None


def format_date(date_text):
    """日付を日本語表示にする。"""

    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "日付不明"

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
        parsed.weekday()
    ]

    return parsed.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_day_data(
    data,
    target_date
):
    """指定日のデータを取得する。"""

    target_text = str(
        target_date
    )

    for day_data in data["days"]:
        if (
            day_data.get(
                "target_date"
            )
            == target_text
        ):
            return day_data

    return None


def get_or_create_day(
    data,
    target_date
):
    """指定日のデータを取得し、なければ作る。"""

    day_data = get_day_data(
        data,
        target_date
    )

    if day_data:
        return day_data

    day_data = {
        "id": create_id(),
        "target_date": str(
            target_date
        ),
        "tasks": [],
        "not_do": "",
        "good_point": "",
        "failure_reason": "",
        "tomorrow_improvement": "",
        "focus_score": 0,
        "satisfaction_score": 0,
        "reviewed": False,
        "created_at": now_text(),
        "updated_at": "",
    }

    data["days"].append(
        day_data
    )

    save_data(data)

    return day_data


def get_task_by_id(
    day_data,
    task_id
):
    """IDからタスクを取得する。"""

    for task in day_data.get(
        "tasks",
        []
    ):
        if task.get("id") == task_id:
            return task

    return None


def sort_tasks(tasks):
    """優先順位順に並べる。"""

    return sorted(
        tasks,
        key=lambda task: (
            int(
                task.get(
                    "priority",
                    99
                )
            ),
            task.get(
                "created_at",
                ""
            )
        )
    )


def completed_count(day_data):
    """完了したタスク数を返す。"""

    return len(
        [
            task
            for task in day_data.get(
                "tasks",
                []
            )
            if task.get("status")
            == "完了"
        ]
    )


def completion_rate(day_data):
    """その日の達成率を計算する。"""

    tasks = day_data.get(
        "tasks",
        []
    )

    if not tasks:
        return 0

    return (
        completed_count(day_data)
        / len(tasks)
        * 100
    )


def total_estimated_minutes(day_data):
    """予定時間の合計を返す。"""

    return sum(
        int(
            task.get(
                "estimated_minutes",
                0
            )
        )
        for task in day_data.get(
            "tasks",
            []
        )
    )


def total_actual_minutes(day_data):
    """実績時間の合計を返す。"""

    return sum(
        int(
            task.get(
                "actual_minutes",
                0
            )
        )
        for task in day_data.get(
            "tasks",
            []
        )
    )


def calculate_full_completion_streak(
    days
):
    """3件すべて達成した連続日数を計算する。"""

    if not days:
        return 0

    date_map = {
        parse_date(
            day_data.get(
                "target_date",
                ""
            )
        ): day_data
        for day_data in days
        if parse_date(
            day_data.get(
                "target_date",
                ""
            )
        )
    }

    current_date = date.today()

    if current_date not in date_map:
        current_date -= timedelta(
            days=1
        )

    streak = 0

    while current_date in date_map:
        day_data = date_map[
            current_date
        ]

        tasks = day_data.get(
            "tasks",
            []
        )

        if (
            len(tasks) == 3
            and completed_count(
                day_data
            ) == 3
        ):
            streak += 1
            current_date -= timedelta(
                days=1
            )

        else:
            break

    return streak


def weekly_completion_rate(days):
    """直近7日間の達成率を計算する。"""

    start_date = (
        date.today()
        - timedelta(
            days=6
        )
    )

    weekly_tasks = []

    for day_data in days:
        target_date = parse_date(
            day_data.get(
                "target_date",
                ""
            )
        )

        if (
            target_date
            and start_date
            <= target_date
            <= date.today()
        ):
            weekly_tasks.extend(
                day_data.get(
                    "tasks",
                    []
                )
            )

    if not weekly_tasks:
        return 0

    done = len(
        [
            task
            for task in weekly_tasks
            if task.get("status")
            == "完了"
        ]
    )

    return (
        done
        / len(weekly_tasks)
        * 100
    )


# =========================================================
# データ操作
# =========================================================

def add_task(
    data,
    target_date,
    values
):
    """タスクを追加する。"""

    day_data = get_or_create_day(
        data,
        target_date
    )

    if len(
        day_data.get(
            "tasks",
            []
        )
    ) >= 3:
        return False

    used_priorities = {
        int(
            task.get(
                "priority",
                0
            )
        )
        for task in day_data.get(
            "tasks",
            []
        )
    }

    if int(
        values["priority"]
    ) in used_priorities:
        return False

    task = {
        "id": create_id(),
        "title": values["title"],
        "priority": int(
            values["priority"]
        ),
        "category": values["category"],
        "estimated_minutes": int(
            values["estimated_minutes"]
        ),
        "actual_minutes": 0,
        "reason": values["reason"],
        "status": "未着手",
        "memo": values["memo"],
        "completed_at": "",
        "carried_from": (
            values.get(
                "carried_from",
                ""
            )
        ),
        "carried_to": "",
        "created_at": now_text(),
        "updated_at": "",
    }

    day_data["tasks"].append(
        task
    )

    day_data["updated_at"] = (
        now_text()
    )

    save_data(data)

    return True


def update_task(
    data,
    target_date,
    task_id,
    values
):
    """タスクを更新する。"""

    day_data = get_day_data(
        data,
        target_date
    )

    if not day_data:
        return False

    task = get_task_by_id(
        day_data,
        task_id
    )

    if not task:
        return False

    new_priority = int(
        values["priority"]
    )

    duplicate_priority = any(
        int(
            other.get(
                "priority",
                0
            )
        )
        == new_priority
        and other.get("id")
        != task_id
        for other in day_data.get(
            "tasks",
            []
        )
    )

    if duplicate_priority:
        return False

    previous_status = task.get(
        "status",
        "未着手"
    )

    for key, value in values.items():
        task[key] = value

    task["priority"] = (
        new_priority
    )

    task["estimated_minutes"] = int(
        task.get(
            "estimated_minutes",
            0
        )
    )

    task["actual_minutes"] = int(
        task.get(
            "actual_minutes",
            0
        )
    )

    if (
        task.get("status")
        == "完了"
        and previous_status
        != "完了"
    ):
        task["completed_at"] = (
            now_text()
        )

    elif task.get(
        "status"
    ) != "完了":
        task["completed_at"] = ""

    task["updated_at"] = now_text()
    day_data["updated_at"] = now_text()

    save_data(data)

    return True


def delete_task(
    data,
    target_date,
    task_id
):
    """タスクを削除する。"""

    day_data = get_day_data(
        data,
        target_date
    )

    if not day_data:
        return

    day_data["tasks"] = [
        task
        for task in day_data.get(
            "tasks",
            []
        )
        if task.get("id")
        != task_id
    ]

    day_data["updated_at"] = (
        now_text()
    )

    save_data(data)


def mark_task_completed(
    data,
    target_date,
    task_id
):
    """タスクを完了にする。"""

    day_data = get_day_data(
        data,
        target_date
    )

    if not day_data:
        return

    task = get_task_by_id(
        day_data,
        task_id
    )

    if not task:
        return

    task["status"] = "完了"
    task["completed_at"] = now_text()
    task["updated_at"] = now_text()
    day_data["updated_at"] = now_text()

    save_data(data)


def carry_task_to_next_day(
    data,
    target_date,
    task_id
):
    """タスクを翌日に繰り越す。"""

    day_data = get_day_data(
        data,
        target_date
    )

    if not day_data:
        return False, "元のデータがありません。"

    task = get_task_by_id(
        day_data,
        task_id
    )

    if not task:
        return False, "タスクがありません。"

    next_date = (
        target_date
        + timedelta(
            days=1
        )
    )

    next_day = get_or_create_day(
        data,
        next_date
    )

    if len(
        next_day.get(
            "tasks",
            []
        )
    ) >= 3:
        return (
            False,
            "翌日にはすでに3つのタスクがあります。"
        )

    used_priorities = {
        int(
            next_task.get(
                "priority",
                0
            )
        )
        for next_task in next_day.get(
            "tasks",
            []
        )
    }

    available_priorities = [
        priority
        for priority in [
            1,
            2,
            3,
        ]
        if priority
        not in used_priorities
    ]

    if not available_priorities:
        return (
            False,
            "翌日に空いている順位がありません。"
        )

    new_task = {
        "id": create_id(),
        "title": task.get(
            "title",
            ""
        ),
        "priority": available_priorities[
            0
        ],
        "category": task.get(
            "category",
            "その他"
        ),
        "estimated_minutes": int(
            task.get(
                "estimated_minutes",
                30
            )
        ),
        "actual_minutes": 0,
        "reason": task.get(
            "reason",
            ""
        ),
        "status": "未着手",
        "memo": (
            task.get(
                "memo",
                ""
            )
            + "\n前日から繰り越し"
        ).strip(),
        "completed_at": "",
        "carried_from": str(
            target_date
        ),
        "carried_to": "",
        "created_at": now_text(),
        "updated_at": "",
    }

    next_day["tasks"].append(
        new_task
    )

    task["status"] = (
        "翌日に繰り越し"
    )

    task["carried_to"] = str(
        next_date
    )

    task["updated_at"] = now_text()
    day_data["updated_at"] = now_text()
    next_day["updated_at"] = now_text()

    save_data(data)

    return (
        True,
        f"{next_date}へ繰り越しました。"
    )


def save_not_do(
    data,
    target_date,
    not_do
):
    """やらないことを保存する。"""

    day_data = get_or_create_day(
        data,
        target_date
    )

    day_data["not_do"] = not_do
    day_data["updated_at"] = now_text()

    save_data(data)


def save_review(
    data,
    target_date,
    values
):
    """1日の振り返りを保存する。"""

    day_data = get_or_create_day(
        data,
        target_date
    )

    day_data["good_point"] = (
        values["good_point"]
    )

    day_data["failure_reason"] = (
        values["failure_reason"]
    )

    day_data[
        "tomorrow_improvement"
    ] = values[
        "tomorrow_improvement"
    ]

    day_data["focus_score"] = int(
        values["focus_score"]
    )

    day_data[
        "satisfaction_score"
    ] = int(
        values[
            "satisfaction_score"
        ]
    )

    day_data["reviewed"] = True
    day_data["updated_at"] = now_text()

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
        background: rgba(90, 110, 255, 0.07);
        border: 1px solid rgba(90, 110, 255, 0.15);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(90, 110, 255, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(90, 110, 255, 0.18),
                rgba(100, 220, 190, 0.12)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()
days = data["days"]

today = date.today()
today_data = get_or_create_day(
    data,
    today
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🎯 今日の優先順位3つ</h1>
        <p>
            今日、本当に大切な3つだけを決めて集中するアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ダッシュボード
# =========================================================

today_task_count = len(
    today_data.get(
        "tasks",
        []
    )
)

today_completed_count = (
    completed_count(
        today_data
    )
)

today_completion_rate = (
    completion_rate(
        today_data
    )
)

week_rate = weekly_completion_rate(
    days
)

full_streak = (
    calculate_full_completion_streak(
        days
    )
)

carry_count = sum(
    1
    for day_data in days
    for task in day_data.get(
        "tasks",
        []
    )
    if task.get("status")
    == "翌日に繰り越し"
)

metric_row1 = st.columns(4)

metric_row1[0].metric(
    "今日の登録",
    f"{today_task_count}/3"
)

metric_row1[1].metric(
    "今日の完了",
    f"{today_completed_count}件"
)

metric_row1[2].metric(
    "今日の達成率",
    f"{today_completion_rate:.1f}%"
)

metric_row1[3].metric(
    "今週の達成率",
    f"{week_rate:.1f}%"
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "3つ達成の連続",
    f"{full_streak}日"
)

metric_row2[1].metric(
    "今日の予定時間",
    f"{total_estimated_minutes(today_data)}分"
)

metric_row2[2].metric(
    "今日の実績時間",
    f"{total_actual_minutes(today_data)}分"
)

metric_row2[3].metric(
    "繰り越し履歴",
    f"{carry_count}件"
)


# =========================================================
# 今日最重要の1つ
# =========================================================

today_tasks = sort_tasks(
    today_data.get(
        "tasks",
        []
    )
)

if today_tasks:
    st.divider()

    most_important = (
        today_tasks[0]
    )

    st.subheader(
        "🔥 今日これだけは終える"
    )

    with st.container(
        border=True
    ):
        important_column1, important_column2 = (
            st.columns(
                [
                    4,
                    1,
                ]
            )
        )

        with important_column1:
            st.markdown(
                f"### "
                f"{PRIORITY_ICONS.get(most_important.get('priority', 1), '')} "
                f"{most_important.get('title', '')}"
            )

            st.caption(
                f"{most_important.get('category', '')} ／ "
                f"予定："
                f"{most_important.get('estimated_minutes', 0)}分"
            )

            if most_important.get(
                "reason",
                ""
            ):
                st.info(
                    "今日やる理由\n\n"
                    + most_important.get(
                        "reason",
                        ""
                    )
                )

        with important_column2:
            important_status = (
                most_important.get(
                    "status",
                    "未着手"
                )
            )

            st.metric(
                "状態",
                f"{STATUS_ICONS.get(important_status, '')} "
                f"{important_status}"
            )


# =========================================================
# 今日やらないこと
# =========================================================

st.divider()

st.subheader(
    "🚫 今日やらないこと"
)

not_do_text = st.text_input(
    "優先順位を守るために、今日は何をしない？",
    value=today_data.get(
        "not_do",
        ""
    ),
    placeholder=(
        "例：新しいアプリ案を増やさない"
    )
)

if st.button(
    "やらないことを保存",
    use_container_width=True
):
    save_not_do(
        data,
        today,
        not_do_text.strip()
    )

    st.success(
        "今日やらないことを保存しました！"
    )

    st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    today_tab,
    add_tab,
    history_tab,
    review_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "✅ 今日の3つ",
        "➕ タスク登録",
        "📅 過去の記録",
        "📝 1日の振り返り",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 今日の3つ
# =========================================================

with today_tab:
    st.header(
        f"✅ {format_date(str(today))}"
    )

    if not today_tasks:
        st.info(
            "今日の優先タスクはまだ登録されていません。"
        )

    else:
        for task in today_tasks:
            task_id = task["id"]

            with st.container(
                border=True
            ):
                task_column1, task_column2 = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with task_column1:
                    st.markdown(
                        f"### "
                        f"{PRIORITY_ICONS.get(task.get('priority', 1), '')} "
                        f"{task.get('title', '')}"
                    )

                    st.caption(
                        f"{task.get('category', '')} ／ "
                        f"予定："
                        f"{task.get('estimated_minutes', 0)}分"
                    )

                with task_column2:
                    current_status = (
                        task.get(
                            "status",
                            "未着手"
                        )
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(current_status, '')} "
                        f"{current_status}"
                    )

                if task.get(
                    "reason",
                    ""
                ):
                    st.info(
                        "今日やる理由\n\n"
                        + task.get(
                            "reason",
                            ""
                        )
                    )

                if task.get(
                    "memo",
                    ""
                ):
                    st.write(
                        f"📝 "
                        f"{task.get('memo', '')}"
                    )

                if task.get(
                    "carried_from",
                    ""
                ):
                    st.warning(
                        f"{task.get('carried_from')}から"
                        "繰り越されたタスクです。"
                    )

                action_columns = (
                    st.columns(3)
                )

                with action_columns[0]:
                    if (
                        task.get("status")
                        != "完了"
                        and st.button(
                            "✅ 完了",
                            key=(
                                f"complete_"
                                f"{task_id}"
                            ),
                            use_container_width=True
                        )
                    ):
                        mark_task_completed(
                            data,
                            today,
                            task_id
                        )

                        st.balloons()
                        st.rerun()

                with action_columns[1]:
                    if (
                        task.get("status")
                        not in [
                            "完了",
                            "翌日に繰り越し",
                        ]
                        and st.button(
                            "➡️ 翌日へ",
                            key=(
                                f"carry_"
                                f"{task_id}"
                            ),
                            use_container_width=True
                        )
                    ):
                        success, message = (
                            carry_task_to_next_day(
                                data,
                                today,
                                task_id
                            )
                        )

                        if success:
                            st.success(
                                message
                            )

                        else:
                            st.error(
                                message
                            )

                        st.rerun()

                with action_columns[2]:
                    st.write(
                        f"実績："
                        f"{task.get('actual_minutes', 0)}分"
                    )

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = st.text_input(
                        "タスク名",
                        value=task.get(
                            "title",
                            ""
                        ),
                        key=(
                            f"edit_title_"
                            f"{task_id}"
                        )
                    )

                    edit_column1, edit_column2 = (
                        st.columns(2)
                    )

                    with edit_column1:
                        edit_priority = (
                            st.selectbox(
                                "順位",
                                [
                                    1,
                                    2,
                                    3,
                                ],
                                index=(
                                    int(
                                        task.get(
                                            "priority",
                                            1
                                        )
                                    )
                                    - 1
                                ),
                                key=(
                                    f"edit_priority_"
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
                                        len(CATEGORIES)
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_category_"
                                    f"{task_id}"
                                )
                            )
                        )

                        edit_estimated = (
                            st.number_input(
                                "予定時間（分）",
                                min_value=1,
                                max_value=1440,
                                value=int(
                                    task.get(
                                        "estimated_minutes",
                                        30
                                    )
                                ),
                                key=(
                                    f"edit_estimated_"
                                    f"{task_id}"
                                )
                            )
                        )

                    with edit_column2:
                        current_status = (
                            task.get(
                                "status",
                                "未着手"
                            )
                        )

                        edit_status = (
                            st.selectbox(
                                "状態",
                                STATUSES,
                                index=(
                                    STATUSES.index(
                                        current_status
                                    )
                                    if current_status
                                    in STATUSES
                                    else 0
                                ),
                                key=(
                                    f"edit_status_"
                                    f"{task_id}"
                                )
                            )
                        )

                        edit_actual = (
                            st.number_input(
                                "実績時間（分）",
                                min_value=0,
                                max_value=1440,
                                value=int(
                                    task.get(
                                        "actual_minutes",
                                        0
                                    )
                                ),
                                key=(
                                    f"edit_actual_"
                                    f"{task_id}"
                                )
                            )
                        )

                    edit_reason = (
                        st.text_area(
                            "今日やる理由",
                            value=task.get(
                                "reason",
                                ""
                            ),
                            key=(
                                f"edit_reason_"
                                f"{task_id}"
                            )
                        )
                    )

                    edit_memo = st.text_area(
                        "メモ",
                        value=task.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_memo_"
                            f"{task_id}"
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
                        if not edit_title.strip():
                            st.error(
                                "タスク名を入力してください。"
                            )

                        else:
                            success = update_task(
                                data,
                                today,
                                task_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "estimated_minutes": (
                                        edit_estimated
                                    ),
                                    "actual_minutes": (
                                        edit_actual
                                    ),
                                    "reason": (
                                        edit_reason.strip()
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                }
                            )

                            if success:
                                st.success(
                                    "タスクを更新しました！"
                                )

                                st.rerun()

                            else:
                                st.error(
                                    "同じ順位が使われています。"
                                )

                with st.expander(
                    "🗑️ 削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{task_id}"
                            )
                        )
                    )

                    if st.button(
                        "このタスクを削除",
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
                            today,
                            task_id
                        )

                        st.rerun()


# =========================================================
# タスク登録
# =========================================================

with add_tab:
    st.header(
        "➕ 今日の優先タスクを登録"
    )

    current_task_count = len(
        today_data.get(
            "tasks",
            []
        )
    )

    st.metric(
        "登録状況",
        f"{current_task_count}/3"
    )

    if current_task_count >= 3:
        st.warning(
            "今日はすでに3つ決まっています。"
            "追加する場合は、どれか1つを削除してください。"
        )

    else:
        used_priorities = {
            int(
                task.get(
                    "priority",
                    0
                )
            )
            for task in today_data.get(
                "tasks",
                []
            )
        }

        available_priorities = [
            priority
            for priority in [
                1,
                2,
                3,
            ]
            if priority
            not in used_priorities
        ]

        with st.form(
            "add_task_form",
            clear_on_submit=True
        ):
            add_column1, add_column2 = (
                st.columns(2)
            )

            with add_column1:
                task_title = (
                    st.text_input(
                        "タスク名",
                        placeholder=(
                            "例：AI Router βの画面を整える"
                        )
                    )
                )

                task_priority = (
                    st.selectbox(
                        "優先順位",
                        available_priorities,
                        format_func=lambda value: (
                            f"{PRIORITY_ICONS.get(value, '')} "
                            f"{value}位"
                        )
                    )
                )

                task_category = (
                    st.selectbox(
                        "カテゴリー",
                        CATEGORIES
                    )
                )

            with add_column2:
                estimated_minutes = (
                    st.number_input(
                        "予定時間（分）",
                        min_value=1,
                        max_value=1440,
                        value=30,
                        step=5
                    )
                )

                task_reason = (
                    st.text_area(
                        "今日やる理由",
                        placeholder=(
                            "なぜ今日やる必要があるのか"
                        ),
                        height=100
                    )
                )

            task_memo = st.text_area(
                "メモ",
                placeholder=(
                    "具体的な作業内容や注意点"
                ),
                height=90
            )

            add_task_submitted = (
                st.form_submit_button(
                    "🎯 優先タスクに追加",
                    use_container_width=True
                )
            )

            if add_task_submitted:
                if not task_title.strip():
                    st.error(
                        "タスク名を入力してください。"
                    )

                else:
                    success = add_task(
                        data,
                        today,
                        {
                            "title": (
                                task_title.strip()
                            ),
                            "priority": (
                                task_priority
                            ),
                            "category": (
                                task_category
                            ),
                            "estimated_minutes": (
                                estimated_minutes
                            ),
                            "reason": (
                                task_reason.strip()
                            ),
                            "memo": (
                                task_memo.strip()
                            ),
                        }
                    )

                    if success:
                        st.success(
                            "優先タスクを追加しました！"
                        )

                        st.rerun()

                    else:
                        st.error(
                            "登録上限または順位の重複があります。"
                        )


# =========================================================
# 過去の記録
# =========================================================

with history_tab:
    st.header(
        "📅 過去の記録"
    )

    recorded_days = [
        day_data
        for day_data in days
        if day_data.get(
            "tasks",
            []
        )
    ]

    if not recorded_days:
        st.info(
            "過去の記録はありません。"
        )

    else:
        date_options = {
            format_date(
                day_data.get(
                    "target_date",
                    ""
                )
            ): day_data.get(
                "target_date",
                ""
            )
            for day_data in sorted(
                recorded_days,
                key=lambda item: item.get(
                    "target_date",
                    ""
                ),
                reverse=True
            )
        }

        selected_date_label = (
            st.selectbox(
                "表示する日",
                list(
                    date_options.keys()
                )
            )
        )

        selected_date_text = (
            date_options[
                selected_date_label
            ]
        )

        selected_date = parse_date(
            selected_date_text
        )

        selected_day_data = (
            get_day_data(
                data,
                selected_date
            )
        )

        if selected_day_data:
            summary_columns = (
                st.columns(4)
            )

            summary_columns[0].metric(
                "登録数",
                len(
                    selected_day_data.get(
                        "tasks",
                        []
                    )
                )
            )

            summary_columns[1].metric(
                "完了数",
                completed_count(
                    selected_day_data
                )
            )

            summary_columns[2].metric(
                "達成率",
                f"{completion_rate(selected_day_data):.1f}%"
            )

            summary_columns[3].metric(
                "予定時間",
                f"{total_estimated_minutes(selected_day_data)}分"
            )

            if selected_day_data.get(
                "not_do",
                ""
            ):
                st.warning(
                    "🚫 やらないこと\n\n"
                    + selected_day_data.get(
                        "not_do",
                        ""
                    )
                )

            for task in sort_tasks(
                selected_day_data.get(
                    "tasks",
                    []
                )
            ):
                with st.container(
                    border=True
                ):
                    st.markdown(
                        f"### "
                        f"{PRIORITY_ICONS.get(task.get('priority', 1), '')} "
                        f"{task.get('title', '')}"
                    )

                    st.caption(
                        f"{task.get('category', '')} ／ "
                        f"{STATUS_ICONS.get(task.get('status', ''), '')} "
                        f"{task.get('status', '')}"
                    )

                    st.write(
                        f"予定："
                        f"{task.get('estimated_minutes', 0)}分 ／ "
                        f"実績："
                        f"{task.get('actual_minutes', 0)}分"
                    )

                    if task.get(
                        "reason",
                        ""
                    ):
                        st.info(
                            task.get(
                                "reason",
                                ""
                            )
                        )

            if selected_day_data.get(
                "reviewed",
                False
            ):
                st.divider()

                st.subheader(
                    "📝 1日の振り返り"
                )

                if selected_day_data.get(
                    "good_point",
                    ""
                ):
                    st.success(
                        "うまくいったこと\n\n"
                        + selected_day_data.get(
                            "good_point",
                            ""
                        )
                    )

                if selected_day_data.get(
                    "failure_reason",
                    ""
                ):
                    st.warning(
                        "できなかった理由\n\n"
                        + selected_day_data.get(
                            "failure_reason",
                            ""
                        )
                    )

                if selected_day_data.get(
                    "tomorrow_improvement",
                    ""
                ):
                    st.info(
                        "明日の改善\n\n"
                        + selected_day_data.get(
                            "tomorrow_improvement",
                            ""
                        )
                    )


# =========================================================
# 振り返り
# =========================================================

with review_tab:
    st.header(
        "📝 今日の振り返り"
    )

    st.write(
        f"今日の達成："
        f"**{today_completed_count}"
        f" / {today_task_count}**"
    )

    st.progress(
        today_completion_rate
        / 100
    )

    with st.form(
        "daily_review_form"
    ):
        good_point = st.text_area(
            "今日うまくいったこと",
            value=today_data.get(
                "good_point",
                ""
            ),
            placeholder=(
                "集中できたこと、完了できたこと"
            ),
            height=110
        )

        failure_reason = st.text_area(
            "できなかった理由",
            value=today_data.get(
                "failure_reason",
                ""
            ),
            placeholder=(
                "疲れ、予定変更、タスクが大きすぎたなど"
            ),
            height=110
        )

        tomorrow_improvement = (
            st.text_area(
                "明日の改善",
                value=today_data.get(
                    "tomorrow_improvement",
                    ""
                ),
                placeholder=(
                    "明日は何を変えるか"
                ),
                height=110
            )
        )

        score_columns = (
            st.columns(2)
        )

        focus_score = (
            score_columns[0].slider(
                "今日の集中度",
                min_value=1,
                max_value=5,
                value=(
                    int(
                        today_data.get(
                            "focus_score",
                            0
                        )
                    )
                    or 3
                )
            )
        )

        satisfaction_score = (
            score_columns[1].slider(
                "今日の達成感",
                min_value=1,
                max_value=5,
                value=(
                    int(
                        today_data.get(
                            "satisfaction_score",
                            0
                        )
                    )
                    or 3
                )
            )
        )

        review_submitted = (
            st.form_submit_button(
                "📝 振り返りを保存",
                use_container_width=True
            )
        )

        if review_submitted:
            save_review(
                data,
                today,
                {
                    "good_point": (
                        good_point.strip()
                    ),
                    "failure_reason": (
                        failure_reason.strip()
                    ),
                    "tomorrow_improvement": (
                        tomorrow_improvement.strip()
                    ),
                    "focus_score": (
                        focus_score
                    ),
                    "satisfaction_score": (
                        satisfaction_score
                    ),
                }
            )

            st.success(
                "今日の振り返りを保存しました！"
            )

            st.rerun()


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 優先順位の分析"
    )

    analysis_rows = []

    for day_data in days:
        target_date = parse_date(
            day_data.get(
                "target_date",
                ""
            )
        )

        for task in day_data.get(
            "tasks",
            []
        ):
            analysis_rows.append(
                {
                    "日付": target_date,
                    "タスク": task.get(
                        "title",
                        ""
                    ),
                    "順位": int(
                        task.get(
                            "priority",
                            1
                        )
                    ),
                    "カテゴリー": task.get(
                        "category",
                        ""
                    ),
                    "状態": task.get(
                        "status",
                        ""
                    ),
                    "予定時間": int(
                        task.get(
                            "estimated_minutes",
                            0
                        )
                    ),
                    "実績時間": int(
                        task.get(
                            "actual_minutes",
                            0
                        )
                    ),
                }
            )

    if not analysis_rows:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "カテゴリー別タスク数"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["件数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "カテゴリー別達成率"
        )

        category_rate_rows = []

        for category in analysis_df[
            "カテゴリー"
        ].unique():
            category_df = analysis_df[
                analysis_df[
                    "カテゴリー"
                ]
                == category
            ]

            done_count = len(
                category_df[
                    category_df[
                        "状態"
                    ]
                    == "完了"
                ]
            )

            rate = (
                done_count
                / len(category_df)
                * 100
            )

            category_rate_rows.append(
                {
                    "カテゴリー": category,
                    "達成率": round(
                        rate,
                        1
                    ),
                }
            )

        category_rate_df = (
            pd.DataFrame(
                category_rate_rows
            )
            .sort_values(
                "達成率",
                ascending=False
            )
        )

        st.bar_chart(
            category_rate_df.set_index(
                "カテゴリー"
            )[["達成率"]]
        )

        st.dataframe(
            category_rate_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "順位別達成率"
        )

        priority_rows = []

        for priority in [
            1,
            2,
            3,
        ]:
            priority_df = analysis_df[
                analysis_df[
                    "順位"
                ]
                == priority
            ]

            if priority_df.empty:
                continue

            done_count = len(
                priority_df[
                    priority_df[
                        "状態"
                    ]
                    == "完了"
                ]
            )

            priority_rows.append(
                {
                    "順位": (
                        f"{priority}位"
                    ),
                    "登録数": len(
                        priority_df
                    ),
                    "完了数": done_count,
                    "達成率": round(
                        done_count
                        / len(
                            priority_df
                        )
                        * 100,
                        1
                    ),
                }
            )

        priority_df = pd.DataFrame(
            priority_rows
        )

        st.bar_chart(
            priority_df.set_index(
                "順位"
            )[["達成率"]]
        )

        st.dataframe(
            priority_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "日別達成率"
        )

        day_rows = []

        for day_data in days:
            if not day_data.get(
                "tasks",
                []
            ):
                continue

            day_rows.append(
                {
                    "日付": day_data.get(
                        "target_date",
                        ""
                    ),
                    "達成率": round(
                        completion_rate(
                            day_data
                        ),
                        1
                    ),
                    "登録数": len(
                        day_data.get(
                            "tasks",
                            []
                        )
                    ),
                    "完了数": completed_count(
                        day_data
                    ),
                }
            )

        day_summary_df = pd.DataFrame(
            day_rows
        ).sort_values(
            "日付"
        )

        st.line_chart(
            day_summary_df.set_index(
                "日付"
            )[["達成率"]]
        )

        st.dataframe(
            day_summary_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "予定時間と実績時間"
        )

        time_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False
            )[
                [
                    "予定時間",
                    "実績時間",
                ]
            ]
            .sum()
        )

        st.bar_chart(
            time_summary.set_index(
                "カテゴリー"
            )[
                [
                    "予定時間",
                    "実績時間",
                ]
            ]
        )

        st.dataframe(
            time_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "よく選ぶカテゴリー"
        )

        category_counter = Counter(
            analysis_df[
                "カテゴリー"
            ]
        )

        if category_counter:
            top_category, top_count = (
                category_counter.most_common(
                    1
                )[0]
            )

            st.metric(
                "最多カテゴリー",
                top_category,
                f"{top_count}件"
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
            f"top3_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = st.file_uploader(
        "バックアップJSONを選択",
        type=[
            "json"
        ]
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict
                )
                or "days"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "days"
                    ],
                    list
                )
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
        "すべてのタスクと振り返り記録が削除されます。"
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
    "全部やろうとしなくていい。今日、大切な3つを進めよう。🎯"
)
