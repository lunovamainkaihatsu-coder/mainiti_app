import json
import os
import random
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="あとでやる箱",
    page_icon="📦",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "later_box_data.json",
)

CATEGORIES = [
    "仕事",
    "AI・プログラミング",
    "イラスト",
    "勉強",
    "家事",
    "買い物",
    "お金",
    "整理整頓",
    "趣味",
    "その他",
]

STATUSES = [
    "📦 あとで",
    "🔥 今日やる",
    "📅 今週やる",
    "🗑 やらない",
    "✅ 完了",
]


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(
        uuid.uuid4()
    )


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "tasks": []
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
                "id",
                create_id(),
            )

            task.setdefault(
                "title",
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
                "status",
                "📦 あとで",
            )

            task.setdefault(
                "created_date",
                str(date.today()),
            )

            task.setdefault(
                "created_at",
                "",
            )

            task.setdefault(
                "updated_at",
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
        save_data(data)
        return data


# =========================================================
# 補助関数
# =========================================================

def get_task_by_id(
    data,
    task_id,
):
    return next(
        (
            task
            for task in data[
                "tasks"
            ]
            if task.get(
                "id"
            )
            == task_id
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

    except (
        ValueError,
        TypeError,
    ):
        return date_text


def days_since_created(
    task,
):
    try:
        created = datetime.strptime(
            task.get(
                "created_date",
                str(date.today()),
            ),
            "%Y-%m-%d",
        ).date()

        return (
            date.today()
            - created
        ).days

    except ValueError:
        return 0


# =========================================================
# データ操作
# =========================================================

def add_task(
    data,
    title,
    category,
    memo,
):
    data["tasks"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "memo": memo,
            "status": "📦 あとで",
            "created_date": str(
                date.today()
            ),
            "created_at": now_text(),
            "updated_at": "",
            "completed_at": "",
        }
    )

    save_data(data)


def update_status(
    data,
    task_id,
    status,
):
    task = get_task_by_id(
        data,
        task_id,
    )

    if not task:
        return

    task["status"] = status
    task["updated_at"] = now_text()

    if status == "✅ 完了":
        task["completed_at"] = (
            now_text()
        )
    else:
        task["completed_at"] = ""

    save_data(data)


def update_task(
    data,
    task_id,
    title,
    category,
    memo,
):
    task = get_task_by_id(
        data,
        task_id,
    )

    if not task:
        return

    task["title"] = title
    task["category"] = category
    task["memo"] = memo
    task["updated_at"] = now_text()

    save_data(data)


def delete_task(
    data,
    task_id,
):
    data["tasks"] = [
        task
        for task in data["tasks"]
        if task.get("id")
        != task_id
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
        background: rgba(120, 130, 255, 0.07);
        border: 1px solid rgba(120, 130, 255, 0.15);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(120, 130, 255, 0.18),
                rgba(100, 210, 180, 0.10)
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

    .pick-box {
        padding: 22px;
        border-radius: 18px;
        background: rgba(120, 130, 255, 0.06);
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .pick-title {
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.6;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

tasks = data[
    "tasks"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📦 あとでやる箱</h1>

        <p>
            今すぐやらなくていいことは、
            いったんここに置いておこう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

later_count = len(
    [
        task
        for task in tasks
        if task.get(
            "status"
        )
        == "📦 あとで"
    ]
)

today_count = len(
    [
        task
        for task in tasks
        if task.get(
            "status"
        )
        == "🔥 今日やる"
    ]
)

week_count = len(
    [
        task
        for task in tasks
        if task.get(
            "status"
        )
        == "📅 今週やる"
    ]
)

done_count = len(
    [
        task
        for task in tasks
        if task.get(
            "status"
        )
        == "✅ 完了"
    ]
)


columns = st.columns(
    4
)

columns[0].metric(
    "📦 あとで",
    f"{later_count}件",
)

columns[1].metric(
    "🔥 今日",
    f"{today_count}件",
)

columns[2].metric(
    "📅 今週",
    f"{week_count}件",
)

columns[3].metric(
    "✅ 完了",
    f"{done_count}件",
)


# =========================================================
# 新規追加
# =========================================================

st.divider()

st.subheader(
    "➕ 箱に入れる"
)

with st.form(
    "add_task_form"
):
    title = st.text_input(
        "あとでやること",
        placeholder=(
            "例：PCの不要ファイルを整理する"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    memo = st.text_input(
        "ひとことメモ",
        placeholder=(
            "例：時間がある日にやる"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📦 箱に入れる",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.error(
                "やることを入力してください。"
            )

        else:
            add_task(
                data,
                title.strip(),
                category,
                memo.strip(),
            )

            st.success(
                "あとでやる箱に入れました！"
            )

            st.rerun()


# =========================================================
# 1個だけ拾う
# =========================================================

later_tasks = [
    task
    for task in tasks
    if task.get(
        "status"
    )
    == "📦 あとで"
]


if later_tasks:
    st.divider()

    st.subheader(
        "🎲 1個だけ拾う"
    )

    if (
        "picked_task_id"
        not in st.session_state
        or not any(
            task.get(
                "id"
            )
            == st.session_state[
                "picked_task_id"
            ]
            for task
            in later_tasks
        )
    ):
        st.session_state[
            "picked_task_id"
        ] = random.choice(
            later_tasks
        ).get(
            "id"
        )

    picked_task = next(
        (
            task
            for task
            in later_tasks
            if task.get(
                "id"
            )
            == st.session_state[
                "picked_task_id"
            ]
        ),
        random.choice(
            later_tasks
        ),
    )

    with st.container(
        border=True,
    ):
        st.caption(
            f"📦 "
            f"{days_since_created(picked_task)}日前に追加"
        )

        st.markdown(
            f"""
            <div class="pick-box">
                <div class="pick-title">
                    {picked_task.get('title', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            picked_task.get(
                "category",
                "",
            )
        )

        if picked_task.get(
            "memo",
            "",
        ):
            st.write(
                f"💬 "
                f"{picked_task.get('memo', '')}"
            )

        pick_status = st.selectbox(
            "これ、どうする？",
            [
                "🔥 今日やる",
                "📅 今週やる",
                "📦 あとで",
                "🗑 やらない",
                "✅ 完了",
            ],
            key=(
                "pick_status_"
                + picked_task.get(
                    "id",
                    "",
                )
            ),
        )

        if st.button(
            "この状態にする",
            use_container_width=True,
        ):
            update_status(
                data,
                picked_task.get(
                    "id"
                ),
                pick_status,
            )

            st.session_state.pop(
                "picked_task_id",
                None,
            )

            st.rerun()

    if st.button(
        "🎲 別の1個を見る",
        use_container_width=True,
    ):
        st.session_state[
            "picked_task_id"
        ] = random.choice(
            later_tasks
        ).get(
            "id"
        )

        st.rerun()


# =========================================================
# 今日やる
# =========================================================

st.divider()

st.subheader(
    "🔥 今日やる"
)

today_tasks = [
    task
    for task in tasks
    if task.get(
        "status"
    )
    == "🔥 今日やる"
]

if not today_tasks:
    st.caption(
        "今日やることはまだありません。"
    )

else:
    for task in today_tasks:
        task_id = task.get(
            "id",
            "",
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 🔥 "
                f"{task.get('title', '')}"
            )

            st.caption(
                task.get(
                    "category",
                    "",
                )
            )

            if task.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{task.get('memo', '')}"
                )

            col1, col2 = st.columns(
                2
            )

            with col1:
                if st.button(
                    "✅ 完了",
                    key=(
                        f"today_done_"
                        f"{task_id}"
                    ),
                    use_container_width=True,
                ):
                    update_status(
                        data,
                        task_id,
                        "✅ 完了",
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "📦 あとで",
                    key=(
                        f"today_later_"
                        f"{task_id}"
                    ),
                    use_container_width=True,
                ):
                    update_status(
                        data,
                        task_id,
                        "📦 あとで",
                    )

                    st.rerun()


# =========================================================
# 今週やる
# =========================================================

st.divider()

st.subheader(
    "📅 今週やる"
)

week_tasks = [
    task
    for task in tasks
    if task.get(
        "status"
    )
    == "📅 今週やる"
]

if not week_tasks:
    st.caption(
        "今週やることはまだありません。"
    )

else:
    for task in week_tasks:
        task_id = task.get(
            "id",
            "",
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 📅 "
                f"{task.get('title', '')}"
            )

            st.caption(
                f"{task.get('category', '')}"
                f" ／ "
                f"{days_since_created(task)}日前に追加"
            )

            if task.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{task.get('memo', '')}"
                )

            col1, col2 = st.columns(
                2
            )

            with col1:
                if st.button(
                    "🔥 今日やる",
                    key=(
                        f"week_today_"
                        f"{task_id}"
                    ),
                    use_container_width=True,
                ):
                    update_status(
                        data,
                        task_id,
                        "🔥 今日やる",
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "✅ 完了",
                    key=(
                        f"week_done_"
                        f"{task_id}"
                    ),
                    use_container_width=True,
                ):
                    update_status(
                        data,
                        task_id,
                        "✅ 完了",
                    )

                    st.rerun()


# =========================================================
# あとで一覧
# =========================================================

st.divider()

st.subheader(
    "📦 あとで"
)

if not later_tasks:
    st.caption(
        "箱は空っぽです！"
    )

else:
    sorted_later_tasks = sorted(
        later_tasks,
        key=lambda task: (
            task.get(
                "created_date",
                "",
            )
        ),
    )

    for task in sorted_later_tasks:
        task_id = task.get(
            "id",
            "",
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 📦 "
                f"{task.get('title', '')}"
            )

            st.caption(
                f"{task.get('category', '')}"
                f" ／ "
                f"{days_since_created(task)}日前に追加"
            )

            if task.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{task.get('memo', '')}"
                )

            status = st.selectbox(
                "移動先",
                STATUSES,
                index=0,
                key=(
                    f"later_status_"
                    f"{task_id}"
                ),
            )

            if st.button(
                "移動する",
                key=(
                    f"move_"
                    f"{task_id}"
                ),
                use_container_width=True,
            ):
                update_status(
                    data,
                    task_id,
                    status,
                )

                st.rerun()


# =========================================================
# 状態別グラフ
# =========================================================

if tasks:
    st.divider()

    st.subheader(
        "📊 今の箱の中"
    )

    status_rows = []

    for status in STATUSES:
        count = len(
            [
                task
                for task in tasks
                if task.get(
                    "status"
                )
                == status
            ]
        )

        status_rows.append(
            {
                "状態": status,
                "件数": count,
            }
        )

    status_df = pd.DataFrame(
        status_rows
    )

    st.bar_chart(
        status_df.set_index(
            "状態"
        )
    )


# =========================================================
# 全タスク管理
# =========================================================

st.divider()

with st.expander(
    "🗂️ 全タスクを管理"
):
    if not tasks:
        st.info(
            "まだタスクがありません。"
        )

    else:
        sorted_tasks = sorted(
            tasks,
            key=lambda task: (
                task.get(
                    "created_at",
                    "",
                )
            ),
            reverse=True,
        )

        for task in sorted_tasks:
            task_id = task.get(
                "id",
                "",
            )

            with st.container(
                border=True,
            ):
                st.markdown(
                    f"### "
                    f"{task.get('status', '')} "
                    f"{task.get('title', '')}"
                )

                st.caption(
                    f"{format_date(task.get('created_date', ''))}"
                    f" ／ "
                    f"{task.get('category', '')}"
                )

                if task.get(
                    "memo",
                    "",
                ):
                    st.write(
                        f"💬 "
                        f"{task.get('memo', '')}"
                    )

                current_status = task.get(
                    "status",
                    "📦 あとで",
                )

                status = st.selectbox(
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
                        f"all_status_"
                        f"{task_id}"
                    ),
                )

                if st.button(
                    "状態を保存",
                    key=(
                        f"save_status_"
                        f"{task_id}"
                    ),
                    use_container_width=True,
                ):
                    update_status(
                        data,
                        task_id,
                        status,
                    )

                    st.rerun()

                # -----------------------------------------
                # 編集
                # -----------------------------------------

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = st.text_input(
                        "やること",
                        value=task.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{task_id}"
                        ),
                    )

                    current_category = (
                        task.get(
                            "category",
                            "その他",
                        )
                    )

                    edit_category = st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=(
                            CATEGORIES.index(
                                current_category
                            )
                            if current_category
                            in CATEGORIES
                            else 0
                        ),
                        key=(
                            f"edit_category_"
                            f"{task_id}"
                        ),
                    )

                    edit_memo = st.text_input(
                        "メモ",
                        value=task.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{task_id}"
                        ),
                    )

                    if st.button(
                        "💾 変更を保存",
                        key=(
                            f"save_edit_"
                            f"{task_id}"
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
                                task_id,
                                edit_title.strip(),
                                edit_category,
                                edit_memo.strip(),
                            )

                            st.rerun()

                # -----------------------------------------
                # 削除
                # -----------------------------------------

                with st.expander(
                    "🗑️ 削除"
                ):
                    if st.button(
                        "このタスクを削除",
                        key=(
                            f"delete_"
                            f"{task_id}"
                        ),
                        use_container_width=True,
                    ):
                        delete_task(
                            data,
                            task_id,
                        )

                        st.rerun()


# =========================================================
# 完了・やらない履歴
# =========================================================

st.divider()

with st.expander(
    "📚 完了・やらない履歴"
):
    history_tasks = [
        task
        for task in tasks
        if task.get(
            "status"
        )
        in [
            "✅ 完了",
            "🗑 やらない",
        ]
    ]

    if not history_tasks:
        st.caption(
            "まだ履歴はありません。"
        )

    else:
        rows = []

        for task in history_tasks:
            rows.append(
                {
                    "状態": task.get(
                        "status",
                        "",
                    ),
                    "内容": task.get(
                        "title",
                        "",
                    ),
                    "カテゴリー": task.get(
                        "category",
                        "",
                    ),
                    "登録日": task.get(
                        "created_date",
                        "",
                    ),
                }
            )

        history_df = pd.DataFrame(
            rows
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
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
            f"later_box_backup_"
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
    "今やらなくていいことは、頭の外に置いていい。📦"
)
