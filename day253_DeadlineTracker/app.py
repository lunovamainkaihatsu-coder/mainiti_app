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
    page_title="これ、いつまで？",
    page_icon="📅",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "deadlines.json",
)

CATEGORIES = [
    "💰 支払い",
    "📝 提出",
    "🔄 更新",
    "📦 返却",
    "💼 仕事",
    "🏠 生活",
    "📚 勉強",
    "🛒 買い物",
    "✨ その他",
]

PRIORITIES = [
    "低",
    "普通",
    "高",
]


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
        "deadlines": []
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
            "deadlines",
            [],
        )

        for item in data["deadlines"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "title",
                "",
            )

            item.setdefault(
                "category",
                "✨ その他",
            )

            item.setdefault(
                "deadline",
                str(date.today()),
            )

            item.setdefault(
                "priority",
                "普通",
            )

            item.setdefault(
                "memo",
                "",
            )

            item.setdefault(
                "completed",
                False,
            )

            item.setdefault(
                "completed_at",
                "",
            )

            item.setdefault(
                "created_at",
                "",
            )

            item.setdefault(
                "updated_at",
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

def parse_date(
    date_text,
):
    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

    except (
        ValueError,
        TypeError,
    ):
        return date.today()


def format_date(
    date_text,
):
    target = parse_date(
        date_text
    )

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


def days_left(
    deadline_text,
):
    deadline_date = parse_date(
        deadline_text
    )

    return (
        deadline_date
        - date.today()
    ).days


def deadline_status(
    deadline_text,
):
    remaining = days_left(
        deadline_text
    )

    if remaining < 0:
        return (
            "❌",
            f"{abs(remaining)}日超過",
        )

    if remaining == 0:
        return (
            "🔥",
            "今日まで",
        )

    if remaining == 1:
        return (
            "⚠️",
            "あと1日",
        )

    if remaining <= 7:
        return (
            "🟠",
            f"あと{remaining}日",
        )

    return (
        "🟢",
        f"あと{remaining}日",
    )


def get_item_by_id(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data[
                "deadlines"
            ]
            if item.get(
                "id"
            )
            == item_id
        ),
        None,
    )


# =========================================================
# CRUD
# =========================================================

def add_deadline(
    data,
    title,
    category,
    deadline,
    priority,
    memo,
):
    data[
        "deadlines"
    ].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "deadline": str(
                deadline
            ),
            "priority": priority,
            "memo": memo,
            "completed": False,
            "completed_at": "",
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_deadline(
    data,
    item_id,
    title,
    category,
    deadline,
    priority,
    memo,
):
    item = get_item_by_id(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "title"
    ] = title

    item[
        "category"
    ] = category

    item[
        "deadline"
    ] = str(
        deadline
    )

    item[
        "priority"
    ] = priority

    item[
        "memo"
    ] = memo

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_complete(
    data,
    item_id,
):
    item = get_item_by_id(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "completed"
    ] = not item.get(
        "completed",
        False,
    )

    if item[
        "completed"
    ]:
        item[
            "completed_at"
        ] = now_text()

    else:
        item[
            "completed_at"
        ] = ""

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_deadline(
    data,
    item_id,
):
    data[
        "deadlines"
    ] = [
        item
        for item in data[
            "deadlines"
        ]
        if item.get(
            "id"
        )
        != item_id
    ]

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
        background: rgba(120, 140, 255, 0.07);
        border: 1px solid rgba(120, 140, 255, 0.15);
        border-radius: 16px;
        padding: 15px;
    }

    .hero {
        padding: 28px;
        border-radius: 24px;
        margin-bottom: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(110, 140, 255, 0.18),
                rgba(255, 170, 80, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.78;
    }

    .deadline-card {
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(120, 140, 255, 0.15);
        margin-bottom: 12px;
    }

    .deadline-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 6px;
        margin-bottom: 8px;
    }

    .deadline-status {
        font-size: 1.15rem;
        font-weight: 800;
    }

    .overdue {
        background: rgba(255, 80, 80, 0.08);
    }

    .today {
        background: rgba(255, 150, 50, 0.10);
    }

    .soon {
        background: rgba(255, 190, 80, 0.08);
    }

    .safe {
        background: rgba(90, 200, 120, 0.06);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

deadlines = data[
    "deadlines"
]

active_items = [
    item
    for item in deadlines
    if not item.get(
        "completed",
        False,
    )
]

completed_items = [
    item
    for item in deadlines
    if item.get(
        "completed",
        False,
    )
]


# =========================================================
# ダッシュボード集計
# =========================================================

overdue_count = len(
    [
        item
        for item in active_items
        if days_left(
            item.get(
                "deadline",
                "",
            )
        ) < 0
    ]
)

week_count = len(
    [
        item
        for item in active_items
        if 0
        <= days_left(
            item.get(
                "deadline",
                "",
            )
        )
        <= 7
    ]
)

current_month = date.today().strftime(
    "%Y-%m"
)

month_count = len(
    [
        item
        for item in active_items
        if item.get(
            "deadline",
            "",
        ).startswith(
            current_month
        )
    ]
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>📅 これ、いつまで？</h1>

        <p>
            期限のあることをまとめて、
            「今なにが危ない？」をすぐ確認。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

col1.metric(
    "❌ 期限切れ",
    f"{overdue_count}件",
)

col2.metric(
    "⚠️ 7日以内",
    f"{week_count}件",
)

col3.metric(
    "📅 今月",
    f"{month_count}件",
)

col4.metric(
    "✅ 完了",
    f"{len(completed_items)}件",
)


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい期限を登録"
)

with st.form(
    "add_deadline_form"
):
    title = st.text_input(
        "何の期限？",
        placeholder=(
            "例：クレジットカードの支払い"
        ),
    )

    col1, col2 = st.columns(
        2
    )

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

    with col2:
        deadline = st.date_input(
            "期限日",
            value=date.today()
            + timedelta(
                days=7
            ),
        )

    priority = st.select_slider(
        "重要度",
        options=PRIORITIES,
        value="普通",
    )

    memo = st.text_area(
        "メモ",
        placeholder=(
            "例：コンビニ支払い"
        ),
        height=90,
    )

    submitted = (
        st.form_submit_button(
            "📅 期限を登録",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.error(
                "期限の内容を入力してください。"
            )

        else:
            add_deadline(
                data,
                title.strip(),
                category,
                deadline,
                priority,
                memo.strip(),
            )

            st.rerun()


# =========================================================
# フィルター
# =========================================================

st.divider()

st.subheader(
    "🚨 これからの期限"
)

filter_col1, filter_col2 = st.columns(
    2
)

with filter_col1:
    category_filter = st.selectbox(
        "カテゴリーで絞る",
        [
            "すべて",
            *CATEGORIES,
        ],
        key="category_filter",
    )

with filter_col2:
    priority_filter = st.selectbox(
        "重要度で絞る",
        [
            "すべて",
            *PRIORITIES,
        ],
        key="priority_filter",
    )


filtered_items = active_items.copy()

if category_filter != "すべて":
    filtered_items = [
        item
        for item in filtered_items
        if item.get(
            "category"
        )
        == category_filter
    ]

if priority_filter != "すべて":
    filtered_items = [
        item
        for item in filtered_items
        if item.get(
            "priority"
        )
        == priority_filter
    ]


priority_order = {
    "高": 0,
    "普通": 1,
    "低": 2,
}

filtered_items = sorted(
    filtered_items,
    key=lambda item: (
        days_left(
            item.get(
                "deadline",
                "",
            )
        ),
        priority_order.get(
            item.get(
                "priority",
                "普通",
            ),
            1,
        ),
    ),
)


# =========================================================
# 期限カード
# =========================================================

if not filtered_items:
    st.success(
        "現在、表示する期限はありません！"
    )

else:
    for item in filtered_items:
        item_id = item.get(
            "id",
            "",
        )

        remaining = days_left(
            item.get(
                "deadline",
                "",
            )
        )

        icon, status_text = (
            deadline_status(
                item.get(
                    "deadline",
                    "",
                )
            )
        )

        if remaining < 0:
            css_class = "overdue"

        elif remaining == 0:
            css_class = "today"

        elif remaining <= 7:
            css_class = "soon"

        else:
            css_class = "safe"

        with st.container(
            border=True,
        ):
            st.markdown(
                f"""
                <div class="deadline-card {css_class}">

                    <div class="deadline-status">
                        {icon} {status_text}
                    </div>

                    <div class="deadline-title">
                        {item.get('title', '')}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ／ "
                f"重要度：{item.get('priority', '普通')}"
            )

            st.write(
                f"📅 "
                f"{format_date(item.get('deadline', ''))}"
            )

            if item.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{item.get('memo', '')}"
                )

            if st.button(
                "✅ 完了にする",
                key=(
                    "complete_"
                    + item_id
                ),
                use_container_width=True,
            ):
                toggle_complete(
                    data,
                    item_id,
                )

                st.rerun()


# =========================================================
# 近い期限一覧
# =========================================================

if active_items:
    st.divider()

    st.subheader(
        "📊 期限一覧"
    )

    table_rows = []

    sorted_active = sorted(
        active_items,
        key=lambda item: days_left(
            item.get(
                "deadline",
                "",
            )
        ),
    )

    for item in sorted_active:
        icon, status_text = (
            deadline_status(
                item.get(
                    "deadline",
                    "",
                )
            )
        )

        table_rows.append(
            {
                "期限": item.get(
                    "deadline",
                    "",
                ),
                "内容": item.get(
                    "title",
                    "",
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "重要度": item.get(
                    "priority",
                    "",
                ),
                "残り": (
                    f"{icon} {status_text}"
                ),
            }
        )

    deadline_df = pd.DataFrame(
        table_rows
    )

    st.dataframe(
        deadline_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 期限を編集・削除"
):
    if not deadlines:
        st.caption(
            "まだ登録がありません。"
        )

    else:
        sorted_items = sorted(
            deadlines,
            key=lambda item: (
                item.get(
                    "completed",
                    False,
                ),
                item.get(
                    "deadline",
                    "",
                ),
            ),
        )

        for item in sorted_items:
            item_id = item.get(
                "id",
                "",
            )

            completed_mark = (
                "✅"
                if item.get(
                    "completed",
                    False,
                )
                else "📅"
            )

            st.markdown(
                f"### {completed_mark} "
                f"{item.get('title', '')}"
            )

            st.caption(
                f"{format_date(item.get('deadline', ''))}"
                f" ／ "
                f"{item.get('category', '')}"
            )

            with st.expander(
                "✏️ 編集"
            ):
                edit_title = st.text_input(
                    "内容",
                    value=item.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + item_id
                    ),
                )

                current_category = (
                    item.get(
                        "category",
                        "✨ その他",
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
                            else len(
                                CATEGORIES
                            ) - 1
                        ),
                        key=(
                            "edit_category_"
                            + item_id
                        ),
                    )
                )

                edit_deadline = (
                    st.date_input(
                        "期限日",
                        value=parse_date(
                            item.get(
                                "deadline",
                                "",
                            )
                        ),
                        key=(
                            "edit_deadline_"
                            + item_id
                        ),
                    )
                )

                current_priority = (
                    item.get(
                        "priority",
                        "普通",
                    )
                )

                edit_priority = (
                    st.select_slider(
                        "重要度",
                        options=PRIORITIES,
                        value=(
                            current_priority
                            if current_priority
                            in PRIORITIES
                            else "普通"
                        ),
                        key=(
                            "edit_priority_"
                            + item_id
                        ),
                    )
                )

                edit_memo = (
                    st.text_area(
                        "メモ",
                        value=item.get(
                            "memo",
                            "",
                        ),
                        key=(
                            "edit_memo_"
                            + item_id
                        ),
                    )
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.error(
                            "内容を入力してください。"
                        )

                    else:
                        update_deadline(
                            data,
                            item_id,
                            edit_title.strip(),
                            edit_category,
                            edit_deadline,
                            edit_priority,
                            edit_memo.strip(),
                        )

                        st.rerun()

            if item.get(
                "completed",
                False,
            ):
                if st.button(
                    "↩ 未完了に戻す",
                    key=(
                        "restore_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_complete(
                        data,
                        item_id,
                    )

                    st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この期限を削除",
                    key=(
                        "delete_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    delete_deadline(
                        data,
                        item_id,
                    )

                    st.rerun()

            st.divider()


# =========================================================
# 完了履歴
# =========================================================

st.divider()

with st.expander(
    "✅ 完了履歴"
):
    if not completed_items:
        st.caption(
            "完了した期限はまだありません。"
        )

    else:
        sorted_completed = sorted(
            completed_items,
            key=lambda item: (
                item.get(
                    "completed_at",
                    ""
                )
            ),
            reverse=True,
        )

        for item in sorted_completed:
            st.markdown(
                f"**✅ {item.get('title', '')}**"
            )

            st.caption(
                f"期限："
                f"{format_date(item.get('deadline', ''))}"
            )

            if item.get(
                "completed_at",
                "",
            ):
                try:
                    completed_datetime = (
                        datetime.fromisoformat(
                            item.get(
                                "completed_at",
                                "",
                            )
                        )
                    )

                    st.caption(
                        "完了："
                        + completed_datetime.strftime(
                            "%Y/%m/%d %H:%M"
                        )
                    )

                except ValueError:
                    pass

            st.divider()


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
            "deadline_tracker_"
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
    "忘れる前に登録。迫る前に片付ける。📅✨"
)
