import json
import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="頭の中ぜんぶ出す",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "brain_dump.json",
)

CATEGORIES = {
    "inbox": "📦 未整理",
    "today": "🔥 今日やる",
    "later": "📅 あとで",
    "idea": "💡 アイデア",
    "think": "🤔 考える",
    "released": "🗑️ 手放した",
    "done": "✅ 解決",
}

ACTIVE_CATEGORIES = [
    "today",
    "later",
    "idea",
    "think",
]

SORT_BUTTONS = [
    ("today", "🔥 今日やる"),
    ("later", "📅 あとでやる"),
    ("idea", "💡 アイデア"),
    ("think", "🤔 考える"),
    ("released", "🗑️ 手放す"),
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


def today_text():
    return str(date.today())


def parse_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def days_since(value):
    target = parse_date(value)

    return max(
        (date.today() - target).days,
        0,
    )


def create_empty_data():
    return {
        "items": [],
        "sessions": [],
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
            "items",
            [],
        )

        data.setdefault(
            "sessions",
            [],
        )

        for item in data["items"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "text",
                "",
            )

            item.setdefault(
                "category",
                "inbox",
            )

            item.setdefault(
                "session_id",
                "",
            )

            item.setdefault(
                "created_date",
                today_text(),
            )

            item.setdefault(
                "created_at",
                now_text(),
            )

            item.setdefault(
                "updated_at",
                item.get(
                    "created_at",
                    now_text(),
                ),
            )

            item.setdefault(
                "resolved_date",
                "",
            )

            item.setdefault(
                "favorite",
                False,
            )

        for session in data["sessions"]:
            session.setdefault(
                "id",
                create_id(),
            )

            session.setdefault(
                "created_date",
                today_text(),
            )

            session.setdefault(
                "created_at",
                now_text(),
            )

            session.setdefault(
                "item_count",
                0,
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
# データ操作
# =========================================================

def get_item(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["items"]
            if item.get(
                "id"
            ) == item_id
        ),
        None,
    )


def add_dump(
    data,
    lines,
):
    session_id = create_id()
    created_at = now_text()

    for line in lines:
        data["items"].append(
            {
                "id": create_id(),
                "text": line,
                "category": "inbox",
                "session_id": session_id,
                "created_date": today_text(),
                "created_at": created_at,
                "updated_at": created_at,
                "resolved_date": "",
                "favorite": False,
            }
        )

    data["sessions"].append(
        {
            "id": session_id,
            "created_date": today_text(),
            "created_at": created_at,
            "item_count": len(
                lines
            ),
        }
    )

    save_data(data)

    return session_id


def move_item(
    data,
    item_id,
    category,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["category"] = category
    item["updated_at"] = now_text()

    if category in [
        "done",
        "released",
    ]:
        item["resolved_date"] = (
            today_text()
        )

    else:
        item["resolved_date"] = ""

    save_data(data)


def update_item_text(
    data,
    item_id,
    text,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["text"] = text
    item["updated_at"] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["favorite"] = not (
        item.get(
            "favorite",
            False,
        )
    )

    item["updated_at"] = now_text()

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data["items"]
        if item.get(
            "id"
        ) != item_id
    ]

    save_data(data)


# =========================================================
# 集計関数
# =========================================================

def count_category(
    items,
    category,
):
    return len(
        [
            item
            for item in items
            if item.get(
                "category"
            ) == category
        ]
    )


def month_items(
    items,
):
    current_month = (
        date.today().strftime(
            "%Y-%m"
        )
    )

    return [
        item
        for item in items
        if item.get(
            "created_date",
            "",
        ).startswith(
            current_month
        )
    ]


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;
        background:
            rgba(100, 120, 255, 0.06);
        border:
            1px solid
            rgba(100, 120, 255, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 25px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 110, 255, 0.18),
                rgba(160, 100, 255, 0.08)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.82;
    }

    .brain-card {
        padding: 30px;
        border-radius: 24px;
        margin-top: 15px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 120, 255, 0.12),
                rgba(180, 100, 255, 0.07)
            );
    }

    .brain-text {
        font-size: 1.8rem;
        font-weight: 800;
        line-height: 1.5;
    }

    .complete-card {
        padding: 28px;
        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(70, 200, 130, 0.13),
                rgba(100, 180, 255, 0.08)
            );
    }

    .old-card {
        padding: 18px;
        border-radius: 18px;
        background:
            rgba(255, 180, 50, 0.08);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()
items = data["items"]

today = today_text()

today_items = [
    item
    for item in items
    if item.get(
        "created_date"
    ) == today
]

current_month_items = (
    month_items(
        items
    )
)

inbox_items = [
    item
    for item in items
    if item.get(
        "category"
    ) == "inbox"
]


# =========================================================
# Session State
# =========================================================

defaults = {
    "sorting_session_id": None,
    "show_sort_complete": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[
            key
        ] = value


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🧠 頭の中ぜんぶ出す</h1>

        <p>
            整理できなくていい。
            まず、頭の外へ。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_out = len(
    today_items
)

today_action = count_category(
    items,
    "today",
)

idea_count = count_category(
    items,
    "idea",
)

released_month = len(
    [
        item
        for item in items
        if item.get(
            "category"
        ) == "released"
        and item.get(
            "resolved_date",
            "",
        ).startswith(
            date.today().strftime(
                "%Y-%m"
            )
        )
    ]
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🧠 今日出した",
    f"{today_out}個",
)

col2.metric(
    "🔥 今日やる",
    f"{today_action}個",
)

col3.metric(
    "💡 アイデア",
    f"{idea_count}個",
)

col4.metric(
    "🗑️ 今月手放した",
    f"{released_month}個",
)


# =========================================================
# ブレインダンプ
# =========================================================

st.divider()

st.subheader(
    "🧠 今、頭にあること"
)

st.caption(
    "整理しなくてOK。"
    "やること、悩み、アイデア、"
    "気になること……全部そのまま書こう。"
)

with st.form(
    "brain_dump_form",
    clear_on_submit=True,
):
    dump_text = st.text_area(
        "1行に1個ずつ書いてみよう",
        height=260,
        placeholder=(
            "明日の仕事\n"
            "アプリ更新したい\n"
            "本を読みたい\n"
            "部屋を片付けたい\n"
            "あのメール返してない\n"
            "新しいアイデア\n"
            "なんか疲れた"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📦 ぜんぶ出した！",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        lines = [
            line.strip()
            for line in (
                dump_text.splitlines()
            )
            if line.strip()
        ]

        if not lines:
            st.warning(
                "頭にあることを"
                "1つ以上書いてみよう。"
            )

        else:
            session_id = add_dump(
                data,
                lines,
            )

            st.session_state[
                "sorting_session_id"
            ] = session_id

            st.session_state[
                "show_sort_complete"
            ] = False

            st.rerun()


# =========================================================
# 仕分けセッション
# =========================================================

sorting_session_id = (
    st.session_state[
        "sorting_session_id"
    ]
)

if sorting_session_id:
    session_items = [
        item
        for item in data["items"]
        if item.get(
            "session_id"
        ) == sorting_session_id
    ]

    unsorted_session = [
        item
        for item in session_items
        if item.get(
            "category"
        ) == "inbox"
    ]

    if unsorted_session:
        st.divider()

        st.subheader(
            "📦 ひとつずつ仕分ける"
        )

        remaining = len(
            unsorted_session
        )

        st.progress(
            (
                len(session_items)
                - remaining
            )
            / max(
                len(session_items),
                1,
            )
        )

        st.caption(
            f"あと {remaining}個"
        )

        current_item = sorted(
            unsorted_session,
            key=lambda item: (
                item.get(
                    "created_at",
                    "",
                )
            ),
        )[0]

        current_id = current_item.get(
            "id",
            "",
        )

        st.markdown(
            f"""
            <div class="brain-card">

                <div>
                    🧠 これはどうする？
                </div>

                <div class="brain-text">
                    {current_item.get("text", "")}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        row1 = st.columns(3)

        for index in range(3):
            category, label = (
                SORT_BUTTONS[
                    index
                ]
            )

            with row1[index]:
                if st.button(
                    label,
                    key=(
                        "sort_"
                        + category
                        + "_"
                        + current_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        current_id,
                        category,
                    )

                    st.rerun()

        row2 = st.columns(2)

        for index in range(
            3,
            5,
        ):
            category, label = (
                SORT_BUTTONS[
                    index
                ]
            )

            with row2[
                index - 3
            ]:
                if st.button(
                    label,
                    key=(
                        "sort_"
                        + category
                        + "_"
                        + current_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        current_id,
                        category,
                    )

                    st.rerun()

    elif session_items:
        if not st.session_state[
            "show_sort_complete"
        ]:
            st.session_state[
                "show_sort_complete"
            ] = True

        st.divider()

        today_count = count_category(
            session_items,
            "today",
        )

        later_count = count_category(
            session_items,
            "later",
        )

        idea_session_count = (
            count_category(
                session_items,
                "idea",
            )
        )

        think_count = count_category(
            session_items,
            "think",
        )

        released_count = (
            count_category(
                session_items,
                "released",
            )
        )

        st.markdown(
            f"""
            <div class="complete-card">

                <h2>
                    🎉 頭の整理完了！
                </h2>

                <p>
                    {len(session_items)}個の考えを
                    頭の外へ出しました。
                </p>

                <p>
                    🔥 今日やる　{today_count}個<br>
                    📅 あとで　{later_count}個<br>
                    💡 アイデア　{idea_session_count}個<br>
                    🤔 考える　{think_count}個<br>
                    🗑️ 手放した　{released_count}個
                </p>

                <strong>
                    🧠 少し余白ができました。
                </strong>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "✨ 整理を終える",
            type="primary",
            use_container_width=True,
        ):
            st.session_state[
                "sorting_session_id"
            ] = None

            st.session_state[
                "show_sort_complete"
            ] = False

            st.rerun()


# =========================================================
# 未整理ボックス
# =========================================================

if (
    inbox_items
    and not sorting_session_id
):
    st.divider()

    st.subheader(
        "📦 まだ整理していないもの"
    )

    st.caption(
        f"{len(inbox_items)}個あります。"
    )

    if st.button(
        "🧹 仕分けを再開する",
        type="primary",
    ):
        target = sorted(
            inbox_items,
            key=lambda item: (
                item.get(
                    "created_at",
                    "",
                )
            ),
        )[0]

        st.session_state[
            "sorting_session_id"
        ] = target.get(
            "session_id"
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
    item
    for item in data["items"]
    if item.get(
        "category"
    ) == "today"
]

if not today_tasks:
    st.info(
        "今のところ「今日やる」はありません。"
    )

else:
    for item in today_tasks:
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### 🔥 "
                f"{item.get('text', '')}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            with col1:
                if st.button(
                    "✅ できた",
                    key=(
                        "today_done_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        item_id,
                        "done",
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "📅 あとで",
                    key=(
                        "today_later_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        item_id,
                        "later",
                    )

                    st.rerun()

            with col3:
                if st.button(
                    "🗑️ 手放す",
                    key=(
                        "today_release_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        item_id,
                        "released",
                    )

                    st.rerun()


# =========================================================
# 各ボックス
# =========================================================

st.divider()

st.subheader(
    "📚 頭の外に置いたもの"
)

tabs = st.tabs(
    [
        "📅 あとで",
        "💡 アイデア",
        "🤔 考える",
        "⭐ お気に入り",
    ]
)


def show_item_box(
    box_items,
    prefix,
):
    if not box_items:
        st.caption(
            "まだありません。"
        )

        return

    for item in sorted(
        box_items,
        key=lambda value: (
            not value.get(
                "favorite",
                False,
            ),
            value.get(
                "created_at",
                "",
            ),
        ),
    ):
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [6, 1]
            )

            with col1:
                st.markdown(
                    f"### "
                    f"{item.get('text', '')}"
                )

            with col2:
                favorite_icon = (
                    "⭐"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    favorite_icon,
                    key=(
                        prefix
                        + "_fav_"
                        + item_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            st.caption(
                f"登録："
                f"{item.get('created_date', '')}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            with col1:
                if st.button(
                    "🔥 今日やる",
                    key=(
                        prefix
                        + "_today_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        item_id,
                        "today",
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "✅ 解決",
                    key=(
                        prefix
                        + "_done_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        item_id,
                        "done",
                    )

                    st.rerun()

            with col3:
                if st.button(
                    "🗑️ 手放す",
                    key=(
                        prefix
                        + "_release_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    move_item(
                        data,
                        item_id,
                        "released",
                    )

                    st.rerun()


with tabs[0]:
    later_items = [
        item
        for item in data["items"]
        if item.get(
            "category"
        ) == "later"
    ]

    show_item_box(
        later_items,
        "later",
    )


with tabs[1]:
    idea_items = [
        item
        for item in data["items"]
        if item.get(
            "category"
        ) == "idea"
    ]

    show_item_box(
        idea_items,
        "idea",
    )


with tabs[2]:
    think_items = [
        item
        for item in data["items"]
        if item.get(
            "category"
        ) == "think"
    ]

    show_item_box(
        think_items,
        "think",
    )


with tabs[3]:
    favorite_items = [
        item
        for item in data["items"]
        if item.get(
            "favorite",
            False,
        )
        and item.get(
            "category"
        ) in ACTIVE_CATEGORIES
    ]

    show_item_box(
        favorite_items,
        "favorite",
    )


# =========================================================
# 放置されている思考
# =========================================================

old_items = [
    item
    for item in data["items"]
    if item.get(
        "category"
    ) in [
        "later",
        "think",
    ]
    and days_since(
        item.get(
            "created_date"
        )
    ) >= 30
]

if old_items:
    st.divider()

    st.subheader(
        "👀 これ、まだ持っておく？"
    )

    st.caption(
        "30日以上「あとで」または"
        "「考える」にあるものです。"
    )

    for item in old_items:
        item_id = item.get(
            "id",
            "",
        )

        days = days_since(
            item.get(
                "created_date"
            )
        )

        st.markdown(
            f"""
            <div class="old-card">

                <strong>
                    {item.get("text", "")}
                </strong>

                <br><br>

                {days}日間ここにあります。

            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = (
            st.columns(3)
        )

        with col1:
            if st.button(
                "🔥 今日やる",
                key=(
                    "old_today_"
                    + item_id
                ),
                use_container_width=True,
            ):
                move_item(
                    data,
                    item_id,
                    "today",
                )

                st.rerun()

        with col2:
            if st.button(
                "📅 まだ持っておく",
                key=(
                    "old_keep_"
                    + item_id
                ),
                use_container_width=True,
            ):
                item["created_date"] = (
                    today_text()
                )

                item["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        with col3:
            if st.button(
                "🗑️ 手放す",
                key=(
                    "old_release_"
                    + item_id
                ),
                use_container_width=True,
            ):
                move_item(
                    data,
                    item_id,
                    "released",
                )

                st.rerun()


# =========================================================
# 今月の整理
# =========================================================

st.divider()

st.subheader(
    "📊 今月の頭の整理"
)

month_created = len(
    current_month_items
)

month_done = len(
    [
        item
        for item in data["items"]
        if item.get(
            "category"
        ) == "done"
        and item.get(
            "resolved_date",
            "",
        ).startswith(
            date.today().strftime(
                "%Y-%m"
            )
        )
    ]
)

month_released = len(
    [
        item
        for item in data["items"]
        if item.get(
            "category"
        ) == "released"
        and item.get(
            "resolved_date",
            "",
        ).startswith(
            date.today().strftime(
                "%Y-%m"
            )
        )
    ]
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "🧠 頭から出した",
    f"{month_created}個",
)

col2.metric(
    "✅ 解決した",
    f"{month_done}個",
)

col3.metric(
    "🗑️ 手放した",
    f"{month_released}個",
)


# =========================================================
# カテゴリーグラフ
# =========================================================

active_for_chart = [
    item
    for item in data["items"]
    if item.get(
        "category"
    ) in CATEGORIES
]

if active_for_chart:
    chart_rows = []

    for category_key, label in (
        CATEGORIES.items()
    ):
        count = count_category(
            data["items"],
            category_key,
        )

        if count > 0:
            chart_rows.append(
                {
                    "分類": label,
                    "個数": count,
                }
            )

    if chart_rows:
        chart_df = pd.DataFrame(
            chart_rows
        )

        st.bar_chart(
            chart_df.set_index(
                "分類"
            )
        )


# =========================================================
# 解決・手放した履歴
# =========================================================

st.divider()

st.subheader(
    "🗃️ 整理した履歴"
)

history_items = [
    item
    for item in data["items"]
    if item.get(
        "category"
    ) in [
        "done",
        "released",
    ]
]

if not history_items:
    st.info(
        "まだ整理した履歴はありません。"
    )

else:
    history_rows = []

    for item in sorted(
        history_items,
        key=lambda value: (
            value.get(
                "resolved_date",
                ""
            ),
            value.get(
                "updated_at",
                "",
            ),
        ),
        reverse=True,
    ):
        history_rows.append(
            {
                "日付": item.get(
                    "resolved_date",
                    "",
                ),
                "内容": item.get(
                    "text",
                    "",
                ),
                "結果": CATEGORIES.get(
                    item.get(
                        "category"
                    ),
                    "",
                ),
                "登録日": item.get(
                    "created_date",
                    "",
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            history_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 全データ管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ データを編集・削除"
):
    if not data["items"]:
        st.caption(
            "まだデータがありません。"
        )

    else:
        search_text = st.text_input(
            "🔎 検索",
            placeholder=(
                "頭から出した内容を検索"
            ),
        )

        filtered_items = []

        for item in data["items"]:
            if (
                search_text.strip()
                and search_text.lower()
                not in item.get(
                    "text",
                    "",
                ).lower()
            ):
                continue

            filtered_items.append(
                item
            )

        for item in sorted(
            filtered_items,
            key=lambda value: (
                value.get(
                    "created_at",
                    "",
                )
            ),
            reverse=True,
        ):
            item_id = item.get(
                "id",
                "",
            )

            with st.expander(
                (
                    CATEGORIES.get(
                        item.get(
                            "category",
                            "inbox",
                        ),
                        "📦",
                    )
                    + " "
                    + item.get(
                        "text",
                        "",
                    )
                )
            ):
                edit_text = st.text_area(
                    "内容",
                    value=item.get(
                        "text",
                        "",
                    ),
                    key=(
                        "edit_text_"
                        + item_id
                    ),
                )

                category_keys = list(
                    CATEGORIES.keys()
                )

                current_category = (
                    item.get(
                        "category",
                        "inbox",
                    )
                )

                if (
                    current_category
                    not in category_keys
                ):
                    current_category = (
                        "inbox"
                    )

                category_index = (
                    category_keys.index(
                        current_category
                    )
                )

                edit_category = st.selectbox(
                    "分類",
                    category_keys,
                    index=category_index,
                    format_func=lambda value: (
                        CATEGORIES[
                            value
                        ]
                    ),
                    key=(
                        "edit_category_"
                        + item_id
                    ),
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "💾 保存",
                        key=(
                            "edit_save_"
                            + item_id
                        ),
                        use_container_width=True,
                    ):
                        if not edit_text.strip():
                            st.warning(
                                "内容を入力してね。"
                            )

                        else:
                            update_item_text(
                                data,
                                item_id,
                                edit_text.strip(),
                            )

                            move_item(
                                data,
                                item_id,
                                edit_category,
                            )

                            st.rerun()

                with col2:
                    if st.button(
                        "🗑️ 完全削除",
                        key=(
                            "delete_item_"
                            + item_id
                        ),
                        use_container_width=True,
                    ):
                        delete_item(
                            data,
                            item_id,
                        )

                        st.rerun()


# =========================================================
# JSONバックアップ
# =========================================================

st.divider()

with st.expander(
    "💾 バックアップ"
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
            "brain_dump_"
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
    "整理できなくていい。"
    "まず、頭の外へ。🧠➡️📦"
)
