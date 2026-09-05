import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の優先3つ",
    page_icon="🏆",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "priorities.json",
)

RANK_LABELS = {
    1: "🥇 1位",
    2: "🥈 2位",
    3: "🥉 3位",
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "days": []
    }


# =========================================================
# 保存・読み込み
# =========================================================

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
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "days",
            [],
        )

        for day_record in data["days"]:
            day_record.setdefault(
                "id",
                create_id(),
            )

            day_record.setdefault(
                "date",
                str(date.today()),
            )

            day_record.setdefault(
                "created_at",
                "",
            )

            day_record.setdefault(
                "updated_at",
                "",
            )

            day_record.setdefault(
                "tasks",
                [],
            )

            for task in day_record["tasks"]:
                task.setdefault(
                    "id",
                    create_id(),
                )

                task.setdefault(
                    "rank",
                    1,
                )

                task.setdefault(
                    "title",
                    "",
                )

                task.setdefault(
                    "memo",
                    "",
                )

                task.setdefault(
                    "completed",
                    False,
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
        save_data(data)
        return data


# =========================================================
# データ取得
# =========================================================

def get_day_record(
    data,
    target_date,
):
    target_text = str(
        target_date
    )

    return next(
        (
            day_record
            for day_record in data["days"]
            if day_record.get(
                "date"
            )
            == target_text
        ),
        None,
    )


def get_or_create_today(
    data,
):
    today_record = get_day_record(
        data,
        date.today(),
    )

    if today_record:
        return today_record

    today_record = {
        "id": create_id(),
        "date": str(
            date.today()
        ),
        "created_at": now_text(),
        "updated_at": "",
        "tasks": [],
    }

    data["days"].append(
        today_record
    )

    save_data(data)

    return today_record


def get_task_by_id(
    day_record,
    task_id,
):
    return next(
        (
            task
            for task in day_record[
                "tasks"
            ]
            if task.get(
                "id"
            )
            == task_id
        ),
        None,
    )


# =========================================================
# 補助関数
# =========================================================

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

    except (
        ValueError,
        TypeError,
    ):
        return date_text


def get_completed_count(
    day_record,
):
    return len(
        [
            task
            for task in day_record.get(
                "tasks",
                [],
            )
            if task.get(
                "completed",
                False,
            )
        ]
    )


def is_full_clear(
    day_record,
):
    tasks = day_record.get(
        "tasks",
        [],
    )

    return (
        len(tasks) == 3
        and all(
            task.get(
                "completed",
                False,
            )
            for task in tasks
        )
    )


def calculate_full_clear_streak(
    data,
):
    full_clear_dates = {
        day_record.get(
            "date"
        )
        for day_record in data.get(
            "days",
            [],
        )
        if is_full_clear(
            day_record
        )
    }

    if not full_clear_dates:
        return 0

    current = date.today()

    if str(current) not in full_clear_dates:
        current -= timedelta(
            days=1
        )

        if (
            str(current)
            not in full_clear_dates
        ):
            return 0

    streak = 0

    while (
        str(current)
        in full_clear_dates
    ):
        streak += 1

        current -= timedelta(
            days=1
        )

    return streak


def next_available_rank(
    day_record,
):
    used_ranks = {
        int(
            task.get(
                "rank",
                1,
            )
        )
        for task in day_record.get(
            "tasks",
            [],
        )
    }

    for rank in [
        1,
        2,
        3,
    ]:
        if rank not in used_ranks:
            return rank

    return None


# =========================================================
# CRUD
# =========================================================

def add_task(
    data,
    day_record,
    title,
    memo,
):
    if len(
        day_record[
            "tasks"
        ]
    ) >= 3:
        return False

    rank = next_available_rank(
        day_record
    )

    if rank is None:
        return False

    day_record[
        "tasks"
    ].append(
        {
            "id": create_id(),
            "rank": rank,
            "title": title,
            "memo": memo,
            "completed": False,
            "completed_at": "",
        }
    )

    day_record[
        "updated_at"
    ] = now_text()

    save_data(data)

    return True


def toggle_complete(
    data,
    day_record,
    task_id,
):
    task = get_task_by_id(
        day_record,
        task_id,
    )

    if not task:
        return

    task[
        "completed"
    ] = not task.get(
        "completed",
        False,
    )

    if task[
        "completed"
    ]:
        task[
            "completed_at"
        ] = now_text()

    else:
        task[
            "completed_at"
        ] = ""

    day_record[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_task(
    data,
    day_record,
    task_id,
    title,
    memo,
    rank,
):
    task = get_task_by_id(
        day_record,
        task_id,
    )

    if not task:
        return

    old_rank = int(
        task.get(
            "rank",
            1,
        )
    )

    new_rank = int(
        rank
    )

    if old_rank != new_rank:
        other_task = next(
            (
                other
                for other in day_record[
                    "tasks"
                ]
                if other.get(
                    "id"
                )
                != task_id
                and int(
                    other.get(
                        "rank",
                        1,
                    )
                )
                == new_rank
            ),
            None,
        )

        if other_task:
            other_task[
                "rank"
            ] = old_rank

    task[
        "title"
    ] = title

    task[
        "memo"
    ] = memo

    task[
        "rank"
    ] = new_rank

    day_record[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_task(
    data,
    day_record,
    task_id,
):
    day_record[
        "tasks"
    ] = [
        task
        for task in day_record[
            "tasks"
        ]
        if task.get(
            "id"
        )
        != task_id
    ]

    # 順位を1・2・3へ詰め直す
    sorted_tasks = sorted(
        day_record[
            "tasks"
        ],
        key=lambda task: int(
            task.get(
                "rank",
                1,
            )
        ),
    )

    for index, task in enumerate(
        sorted_tasks,
        start=1,
    ):
        task[
            "rank"
        ] = index

    day_record[
        "updated_at"
    ] = now_text()

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 180, 80, 0.08);
        border: 1px solid rgba(255, 180, 80, 0.16);
        border-radius: 16px;
        padding: 15px;
    }

    .hero {
        padding: 26px;
        border-radius: 22px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 180, 80, 0.18),
                rgba(110, 150, 255, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.76;
    }

    .priority-card {
        padding: 22px;
        border-radius: 18px;
        margin-bottom: 12px;

        background:
            rgba(120, 140, 255, 0.05);
    }

    .rank {
        font-size: 1.05rem;
        font-weight: 800;
        opacity: 0.8;
    }

    .priority-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 6px;
        margin-bottom: 8px;
    }

    .complete {
        opacity: 0.55;
        text-decoration: line-through;
    }

    .clear-box {
        padding: 28px;
        border-radius: 20px;
        text-align: center;
        margin-top: 18px;
        margin-bottom: 18px;

        background:
            rgba(255, 190, 80, 0.10);
    }

    .clear-title {
        font-size: 1.45rem;
        font-weight: 900;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

today_record = get_or_create_today(
    data
)

today_tasks = sorted(
    today_record[
        "tasks"
    ],
    key=lambda task: int(
        task.get(
            "rank",
            1,
        )
    ),
)

completed_count = (
    get_completed_count(
        today_record
    )
)

progress = (
    completed_count / 3
)

full_clear_streak = (
    calculate_full_clear_streak(
        data
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🏆 今日の優先3つ</h1>

        <p>
            今日見るのは、3つだけ。
            本当に大事なことに集中しよう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3 = st.columns(
    3
)

col1.metric(
    "🎯 今日の登録",
    f"{len(today_tasks)} / 3",
)

col2.metric(
    "✅ 完了",
    f"{completed_count} / 3",
)

col3.metric(
    "🔥 3/3連続",
    f"{full_clear_streak}日",
)

st.write(
    f"**今日の達成率：{round(progress * 100)}%**"
)

st.progress(
    progress
)


# =========================================================
# 全クリア表示
# =========================================================

if is_full_clear(
    today_record
):
    st.markdown(
        """
        <div class="clear-box">

            <div class="clear-title">
                🎉 今日の優先3つ、全部クリア！
            </div>

            <div style="margin-top:8px;">
                今日、本当に大事な3つを終えました。
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 今日の優先3つ
# =========================================================

st.divider()

st.subheader(
    "🎯 今日の3つ"
)

if not today_tasks:
    st.info(
        "まだ何も決めていません。まず1つ登録してみよう！"
    )

else:
    for task in today_tasks:
        task_id = task.get(
            "id",
            "",
        )

        rank = int(
            task.get(
                "rank",
                1,
            )
        )

        completed = task.get(
            "completed",
            False,
        )

        with st.container(
            border=True,
        ):
            css_class = (
                " complete"
                if completed
                else ""
            )

            st.markdown(
                f"""
                <div class="priority-card">

                    <div class="rank">
                        {RANK_LABELS.get(rank, f"{rank}位")}
                    </div>

                    <div class="priority-title{css_class}">
                        {task.get('title', '')}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if task.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{task.get('memo', '')}"
                )

            if completed:
                button_text = (
                    "↩ 未完了に戻す"
                )

            else:
                button_text = (
                    "✅ 完了！"
                )

            if st.button(
                button_text,
                key=(
                    "toggle_"
                    + task_id
                ),
                use_container_width=True,
            ):
                toggle_complete(
                    data,
                    today_record,
                    task_id,
                )

                st.rerun()


# =========================================================
# 追加
# =========================================================

st.divider()

st.subheader(
    "➕ 今日の優先を追加"
)

if len(
    today_tasks
) >= 3:
    st.success(
        "今日の3つは決まりました！"
    )

    st.caption(
        "4つ目は追加できません。"
        "追加したい場合は、今ある3つを見直してみよう。"
    )

else:
    next_rank = next_available_rank(
        today_record
    )

    st.info(
        f"次に登録するのは "
        f"{RANK_LABELS.get(next_rank, '')} です。"
    )

    with st.form(
        "add_priority_form"
    ):
        title = st.text_input(
            "何をやる？",
            placeholder=(
                "例：AIのコードを10分読む"
            ),
        )

        memo = st.text_input(
            "ひとことメモ",
            placeholder=(
                "例：全部理解しなくてもOK"
            ),
        )

        submitted = (
            st.form_submit_button(
                "➕ 今日の3つに追加",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.error(
                    "やることを入力してください。"
                )

            else:
                result = add_task(
                    data,
                    today_record,
                    title.strip(),
                    memo.strip(),
                )

                if result:
                    st.success(
                        "今日の優先に追加しました！"
                    )

                st.rerun()


# =========================================================
# 編集・順位変更
# =========================================================

st.divider()

with st.expander(
    "✏️ 今日の3つを編集"
):
    if not today_tasks:
        st.caption(
            "編集できる項目はまだありません。"
        )

    else:
        for task in today_tasks:
            task_id = task.get(
                "id",
                "",
            )

            rank = int(
                task.get(
                    "rank",
                    1,
                )
            )

            st.markdown(
                f"### "
                f"{RANK_LABELS.get(rank, '')} "
                f"{task.get('title', '')}"
            )

            edit_title = st.text_input(
                "やること",
                value=task.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + task_id
                ),
            )

            edit_memo = st.text_input(
                "メモ",
                value=task.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + task_id
                ),
            )

            available_ranks = list(
                range(
                    1,
                    len(today_tasks) + 1,
                )
            )

            edit_rank = st.selectbox(
                "優先順位",
                available_ranks,
                index=(
                    available_ranks.index(
                        rank
                    )
                    if rank
                    in available_ranks
                    else 0
                ),
                format_func=lambda value: (
                    RANK_LABELS.get(
                        value,
                        f"{value}位",
                    )
                ),
                key=(
                    "edit_rank_"
                    + task_id
                ),
            )

            if st.button(
                "💾 変更を保存",
                key=(
                    "save_edit_"
                    + task_id
                ),
                use_container_width=True,
            ):
                if not edit_title.strip():
                    st.error(
                        "やることを入力してください。"
                    )

                else:
                    update_task(
                        data,
                        today_record,
                        task_id,
                        edit_title.strip(),
                        edit_memo.strip(),
                        edit_rank,
                    )

                    st.rerun()

            with st.expander(
                "🗑️ この項目を削除"
            ):
                if st.button(
                    "削除する",
                    key=(
                        "delete_"
                        + task_id
                    ),
                    use_container_width=True,
                ):
                    delete_task(
                        data,
                        today_record,
                        task_id,
                    )

                    st.rerun()

            st.divider()


# =========================================================
# 過去7日
# =========================================================

st.divider()

st.subheader(
    "📅 最近7日"
)

week_rows = []

for offset in range(
    6,
    -1,
    -1,
):
    target = (
        date.today()
        - timedelta(
            days=offset
        )
    )

    record = get_day_record(
        data,
        target,
    )

    if record:
        task_count = len(
            record.get(
                "tasks",
                [],
            )
        )

        done_count = (
            get_completed_count(
                record
            )
        )

        full_clear = (
            is_full_clear(
                record
            )
        )

    else:
        task_count = 0
        done_count = 0
        full_clear = False

    week_rows.append(
        {
            "日付": target.strftime(
                "%m/%d"
            ),
            "登録": (
                f"{task_count}/3"
            ),
            "完了": (
                f"{done_count}/3"
            ),
            "3/3": (
                "🏆"
                if full_clear
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
# 過去履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の優先3つを見る"
):
    past_days = [
        day_record
        for day_record in data[
            "days"
        ]
        if day_record.get(
            "date"
        )
        != str(
            date.today()
        )
    ]

    past_days = sorted(
        past_days,
        key=lambda item: (
            item.get(
                "date",
                "",
            )
        ),
        reverse=True,
    )

    if not past_days:
        st.caption(
            "まだ過去の記録はありません。"
        )

    else:
        for day_record in past_days:
            tasks = sorted(
                day_record.get(
                    "tasks",
                    [],
                ),
                key=lambda task: int(
                    task.get(
                        "rank",
                        1,
                    )
                ),
            )

            done_count = (
                get_completed_count(
                    day_record
                )
            )

            st.markdown(
                f"### 📅 "
                f"{format_date(day_record.get('date', ''))}"
            )

            st.caption(
                f"達成：{done_count} / 3"
            )

            if is_full_clear(
                day_record
            ):
                st.success(
                    "🏆 3/3達成！"
                )

            if not tasks:
                st.write(
                    "この日は登録なし"
                )

            for task in tasks:
                icon = (
                    "✅"
                    if task.get(
                        "completed",
                        False,
                    )
                    else "⬜"
                )

                st.write(
                    f"{icon} "
                    f"{RANK_LABELS.get(int(task.get('rank', 1)), '')} "
                    f"{task.get('title', '')}"
                )

                if task.get(
                    "memo",
                    "",
                ):
                    st.caption(
                        f"💬 {task.get('memo', '')}"
                    )

            st.divider()


# =========================================================
# 月間集計
# =========================================================

st.divider()

st.subheader(
    "📊 今月の達成"
)

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_days = [
    day_record
    for day_record in data[
        "days"
    ]
    if day_record.get(
        "date",
        "",
    ).startswith(
        current_month
    )
]

registered_total = sum(
    len(
        day_record.get(
            "tasks",
            [],
        )
    )
    for day_record in month_days
)

completed_total = sum(
    get_completed_count(
        day_record
    )
    for day_record in month_days
)

full_clear_total = len(
    [
        day_record
        for day_record in month_days
        if is_full_clear(
            day_record
        )
    ]
)

col1, col2, col3 = st.columns(
    3
)

col1.metric(
    "登録",
    f"{registered_total}個",
)

col2.metric(
    "完了",
    f"{completed_total}個",
)

col3.metric(
    "3/3達成日",
    f"{full_clear_total}日",
)


# =========================================================
# JSONバックアップ
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
            "top_three_today_"
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
    "全部やらなくていい。今日は、大事な3つだけ。🏆"
)
