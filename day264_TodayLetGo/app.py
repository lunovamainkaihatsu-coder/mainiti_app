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
    page_title="今日やめたこと",
    page_icon="🌿",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "let_go.json",
)

CATEGORIES = [
    "📱 スマホ・SNS",
    "🛍️ 買い物",
    "🍩 食べ物",
    "💼 仕事",
    "⏰ 時間の使い方",
    "🧠 考えすぎ",
    "😣 無理すること",
    "🏠 モノ・片付け",
    "💰 お金",
    "✨ その他",
]

SPACE_TYPES = [
    "⏰ 時間",
    "💰 お金",
    "🧠 心",
    "💪 体力",
    "🏠 スペース",
    "🌙 睡眠",
    "✨ その他",
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
        "records": []
    }


def parse_date(text):
    try:
        return datetime.strptime(
            text,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def format_date(text):
    target = parse_date(text)

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

    return (
        f"{target.year}年"
        f"{target.month}月"
        f"{target.day}日"
        f"（{weekday}）"
    )


def month_key(target):
    return target.strftime(
        "%Y-%m"
    )


def level_stars(level):
    level = int(level)

    return (
        "★" * level
        + "☆" * (5 - level)
    )


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
            "records",
            [],
        )

        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "title",
                "",
            )

            record.setdefault(
                "category",
                "✨ その他",
            )

            record.setdefault(
                "level",
                3,
            )

            record.setdefault(
                "space_type",
                "🧠 心",
            )

            record.setdefault(
                "space_detail",
                "",
            )

            record.setdefault(
                "comment",
                "",
            )

            record.setdefault(
                "record_date",
                str(date.today()),
            )

            record.setdefault(
                "favorite",
                False,
            )

            record.setdefault(
                "created_at",
                now_text(),
            )

            record.setdefault(
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
# CRUD
# =========================================================

def get_record_by_id(
    data,
    record_id,
):
    return next(
        (
            record
            for record in data["records"]
            if record.get(
                "id"
            ) == record_id
        ),
        None,
    )


def add_record(
    data,
    title,
    category,
    level,
    space_type,
    space_detail,
    comment,
    record_date,
):
    data["records"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "level": int(level),
            "space_type": space_type,
            "space_detail": space_detail,
            "comment": comment,
            "record_date": str(
                record_date
            ),
            "favorite": False,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_record(
    data,
    record_id,
    title,
    category,
    level,
    space_type,
    space_detail,
    comment,
    record_date,
    favorite,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record["title"] = title
    record["category"] = category
    record["level"] = int(level)
    record["space_type"] = space_type
    record["space_detail"] = space_detail
    record["comment"] = comment

    record["record_date"] = str(
        record_date
    )

    record["favorite"] = bool(
        favorite
    )

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get(
            "id"
        ) != record_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    record_id,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record["favorite"] = not (
        record.get(
            "favorite",
            False,
        )
    )

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# 集計
# =========================================================

def records_for_month(
    records,
    target_month,
):
    return [
        record
        for record in records
        if record.get(
            "record_date",
            "",
        ).startswith(
            target_month
        )
    ]


def unique_days(records):
    return len(
        {
            record.get(
                "record_date"
            )
            for record in records
            if record.get(
                "record_date"
            )
        }
    )


def most_common_value(
    records,
    key,
):
    if not records:
        return None, 0

    counts = {}

    for record in records:
        value = record.get(
            key,
            "✨ その他",
        )

        counts[value] = (
            counts.get(
                value,
                0,
            )
            + 1
        )

    top_value = max(
        counts,
        key=counts.get,
    )

    return (
        top_value,
        counts[top_value],
    )


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
        padding: 15px;
        border-radius: 16px;
        background:
            rgba(80, 190, 130, 0.07);
        border:
            1px solid
            rgba(80, 190, 130, 0.16);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 190, 130, 0.18),
                rgba(120, 210, 190, 0.08)
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

    .letgo-box {
        padding: 20px;
        border-radius: 20px;
        margin-top: 10px;
        margin-bottom: 10px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 190, 130, 0.08),
                rgba(255, 220, 100, 0.05)
            );
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

records = data[
    "records"
]

today = date.today()

current_month = month_key(
    today
)

month_records = records_for_month(
    records,
    current_month,
)

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    ) == str(today)
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🌿 今日やめたこと</h1>

        <p>
            増やすだけが前進じゃない。
            やめたことで、生まれるものもある。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

top_space, top_space_count = (
    most_common_value(
        month_records,
        "space_type",
    )
)

max_level = max(
    [
        int(
            record.get(
                "level",
                0,
            )
        )
        for record in month_records
    ],
    default=0,
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌿 今月やめたこと",
    f"{len(month_records)}個",
)

col2.metric(
    "🔥 大きな手放し",
    (
        level_stars(
            max_level
        )
        if max_level
        else "-"
    ),
)

col3.metric(
    "✨ よく生まれた余白",
    (
        top_space
        if top_space
        else "-"
    ),
    (
        f"{top_space_count}回"
        if top_space
        else None
    ),
)

col4.metric(
    "📅 記録日数",
    f"{unique_days(month_records)}日",
)


# =========================================================
# 新規記録
# =========================================================

st.divider()

st.subheader(
    "🌱 今日やめたことを記録"
)

with st.form(
    "new_record_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "やめたこと",
        placeholder=(
            "例：寝る前に動画を"
            "見続けるのをやめた"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        level = st.slider(
            "🌿 やめたレベル",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            help=(
                "自分にとってどれくらい"
                "大きな手放しだったか"
            ),
        )

    with col2:
        space_type = st.selectbox(
            "✨ 生まれた余白",
            SPACE_TYPES,
        )

        record_date = st.date_input(
            "日付",
            value=date.today(),
        )

    space_detail = st.text_area(
        "🌱 何が生まれた？",
        placeholder=(
            "例：30分早く寝られた"
        ),
    )

    comment = st.text_input(
        "💬 一言（任意）",
        placeholder=(
            "例：意外と見なくても平気だった"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🌿 記録する",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "やめたことを入力してね。"
            )

        else:
            add_record(
                data,
                title.strip(),
                category,
                level,
                space_type,
                space_detail.strip(),
                comment.strip(),
                record_date,
            )

            st.rerun()


# =========================================================
# 今日やめたこと
# =========================================================

st.divider()

st.subheader(
    "🌿 今日やめたこと"
)

if not today_records:
    st.info(
        "今日はまだ記録がありません。"
        "小さな「やめた」でも大丈夫。"
    )

else:
    today_records = sorted(
        today_records,
        key=lambda record: (
            record.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for record in today_records:
        record_id = record.get(
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
                    f"### 🌿 "
                    f"{record.get('title', '')}"
                )

            with col2:
                icon = (
                    "⭐"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    icon,
                    key=(
                        "today_favorite_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            st.write(
                record.get(
                    "category",
                    "✨ その他",
                )
            )

            st.write(
                "**手放しレベル：** "
                + level_stars(
                    record.get(
                        "level",
                        3,
                    )
                )
            )

            st.write(
                "**✨ 生まれた余白：** "
                + record.get(
                    "space_type",
                    "✨ その他",
                )
            )

            if record.get(
                "space_detail",
                "",
            ):
                st.success(
                    record.get(
                        "space_detail",
                        "",
                    )
                )

            if record.get(
                "comment",
                "",
            ):
                st.caption(
                    "💬 "
                    + record.get(
                        "comment",
                        "",
                    )
                )


# =========================================================
# 生まれた余白
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "🌱 今月生まれた余白"
    )

    space_rows = []

    for record in month_records:
        space_rows.append(
            {
                "余白": record.get(
                    "space_type",
                    "✨ その他",
                )
            }
        )

    space_df = pd.DataFrame(
        space_rows
    )

    space_count = (
        space_df[
            "余白"
        ]
        .value_counts()
        .rename_axis(
            "余白"
        )
        .reset_index(
            name="回数"
        )
    )

    st.bar_chart(
        space_count.set_index(
            "余白"
        )
    )

    st.caption(
        "やめたことで、"
        "どんな余白が生まれたかを"
        "集計しています。"
    )


# =========================================================
# カテゴリー分析
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "📊 今月やめたもの"
    )

    category_rows = []

    for record in month_records:
        category_rows.append(
            {
                "カテゴリー": (
                    record.get(
                        "category",
                        "✨ その他",
                    )
                )
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    category_count = (
        category_df[
            "カテゴリー"
        ]
        .value_counts()
        .rename_axis(
            "カテゴリー"
        )
        .reset_index(
            name="回数"
        )
    )

    st.bar_chart(
        category_count.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 月別推移
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📈 月別の手放し"
    )

    monthly_rows = []

    for record in records:
        record_date = record.get(
            "record_date",
            "",
        )

        if len(record_date) >= 7:
            monthly_rows.append(
                {
                    "月": record_date[:7]
                }
            )

    if monthly_rows:
        monthly_df = pd.DataFrame(
            monthly_rows
        )

        monthly_count = (
            monthly_df[
                "月"
            ]
            .value_counts()
            .rename_axis(
                "月"
            )
            .reset_index(
                name="記録数"
            )
            .sort_values(
                "月"
            )
        )

        st.line_chart(
            monthly_count.set_index(
                "月"
            )
        )


# =========================================================
# 過去の手放しを再発見
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🎲 過去の手放し"
    )

    if "random_letgo_id" not in (
        st.session_state
    ):
        st.session_state[
            "random_letgo_id"
        ] = None

    if st.button(
        "🌿 過去の記録を1つ見る",
        use_container_width=True,
    ):
        chosen = random.choice(
            records
        )

        st.session_state[
            "random_letgo_id"
        ] = chosen.get(
            "id"
        )

    random_id = st.session_state[
        "random_letgo_id"
    ]

    if random_id:
        random_record = (
            get_record_by_id(
                data,
                random_id,
            )
        )

        if random_record:
            with st.container(
                border=True
            ):
                st.caption(
                    format_date(
                        random_record.get(
                            "record_date",
                            "",
                        )
                    )
                )

                st.markdown(
                    f"### 🌿 "
                    f"{random_record.get('title', '')}"
                )

                st.write(
                    "**✨ 生まれた余白：** "
                    + random_record.get(
                        "space_type",
                        "✨ その他",
                    )
                )

                if random_record.get(
                    "space_detail",
                    "",
                ):
                    st.write(
                        random_record.get(
                            "space_detail",
                            "",
                        )
                    )

                if random_record.get(
                    "comment",
                    "",
                ):
                    st.caption(
                        "💬 "
                        + random_record.get(
                            "comment",
                            "",
                        )
                    )


# =========================================================
# お気に入り
# =========================================================

favorite_records = [
    record
    for record in records
    if record.get(
        "favorite",
        False,
    )
]

if favorite_records:
    st.divider()

    st.subheader(
        "⭐ 大切な手放し"
    )

    favorite_records = sorted(
        favorite_records,
        key=lambda record: (
            record.get(
                "record_date",
                "",
            )
        ),
        reverse=True,
    )

    for record in (
        favorite_records[:5]
    ):
        with st.container(
            border=True
        ):
            st.markdown(
                f"**🌿 "
                f"{record.get('title', '')}**"
            )

            st.caption(
                format_date(
                    record.get(
                        "record_date",
                        "",
                    )
                )
            )

            st.write(
                f"{record.get('space_type', '')} "
                f"→ "
                f"{record.get('space_detail', '')}"
            )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 手放し履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "やめたこと・余白・一言から検索"
    ),
)

month_options = sorted(
    {
        record.get(
            "record_date",
            "",
        )[:7]
        for record in records
        if record.get(
            "record_date"
        )
    },
    reverse=True,
)

filter_col1, filter_col2, filter_col3 = (
    st.columns(3)
)

with filter_col1:
    month_filter = st.selectbox(
        "月",
        ["すべて"] + month_options,
    )

with filter_col2:
    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="history_category",
    )

with filter_col3:
    display_filter = st.selectbox(
        "表示",
        [
            "すべて",
            "⭐ お気に入りのみ",
            "🔥 レベル5のみ",
        ],
    )


filtered_records = []

for record in records:
    if (
        month_filter != "すべて"
        and not record.get(
            "record_date",
            "",
        ).startswith(
            month_filter
        )
    ):
        continue

    if (
        category_filter != "すべて"
        and record.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        display_filter
        == "⭐ お気に入りのみ"
        and not record.get(
            "favorite",
            False,
        )
    ):
        continue

    if (
        display_filter
        == "🔥 レベル5のみ"
        and int(
            record.get(
                "level",
                0,
            )
        ) != 5
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                record.get(
                    "title",
                    "",
                ),
                record.get(
                    "space_detail",
                    "",
                ),
                record.get(
                    "comment",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text.lower()
            not in target
        ):
            continue

    filtered_records.append(
        record
    )


filtered_records = sorted(
    filtered_records,
    key=lambda record: (
        record.get(
            "record_date",
            "",
        ),
        record.get(
            "created_at",
            "",
        ),
    ),
    reverse=True,
)


if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    history_rows = []

    for record in filtered_records:
        history_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "やめたこと": (
                    record.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    record.get(
                        "category",
                        "",
                    )
                ),
                "レベル": (
                    level_stars(
                        record.get(
                            "level",
                            3,
                        )
                    )
                ),
                "生まれた余白": (
                    record.get(
                        "space_type",
                        "",
                    )
                ),
                "余白の内容": (
                    record.get(
                        "space_detail",
                        "",
                    )
                ),
                "⭐": (
                    "⭐"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else ""
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
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 記録を編集・削除"
):
    edit_records = sorted(
        records,
        key=lambda record: (
            record.get(
                "record_date",
                "",
            ),
            record.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    )

    if not edit_records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in edit_records:
        record_id = record.get(
            "id",
            "",
        )

        expander_title = (
            f"{record.get('record_date', '')}"
            f" ｜ "
            f"{record.get('title', '')[:30]}"
        )

        with st.expander(
            expander_title
        ):
            edit_title = st.text_input(
                "やめたこと",
                value=record.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + record_id
                ),
            )

            current_category = (
                record.get(
                    "category",
                    "✨ その他",
                )
            )

            category_index = (
                CATEGORIES.index(
                    current_category
                )
                if current_category
                in CATEGORIES
                else len(
                    CATEGORIES
                ) - 1
            )

            edit_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=category_index,
                    key=(
                        "edit_category_"
                        + record_id
                    ),
                )
            )

            edit_level = st.slider(
                "やめたレベル",
                1,
                5,
                int(
                    record.get(
                        "level",
                        3,
                    )
                ),
                key=(
                    "edit_level_"
                    + record_id
                ),
            )

            current_space = (
                record.get(
                    "space_type",
                    "🧠 心",
                )
            )

            space_index = (
                SPACE_TYPES.index(
                    current_space
                )
                if current_space
                in SPACE_TYPES
                else 0
            )

            edit_space = (
                st.selectbox(
                    "生まれた余白",
                    SPACE_TYPES,
                    index=space_index,
                    key=(
                        "edit_space_"
                        + record_id
                    ),
                )
            )

            edit_detail = st.text_area(
                "何が生まれた？",
                value=record.get(
                    "space_detail",
                    "",
                ),
                key=(
                    "edit_detail_"
                    + record_id
                ),
            )

            edit_comment = st.text_input(
                "一言",
                value=record.get(
                    "comment",
                    "",
                ),
                key=(
                    "edit_comment_"
                    + record_id
                ),
            )

            edit_date = st.date_input(
                "日付",
                value=parse_date(
                    record.get(
                        "record_date",
                        "",
                    )
                ),
                key=(
                    "edit_date_"
                    + record_id
                ),
            )

            edit_favorite = (
                st.checkbox(
                    "⭐ お気に入り",
                    value=record.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "edit_favorite_"
                        + record_id
                    ),
                )
            )

            button_col1, button_col2 = (
                st.columns(2)
            )

            with button_col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.warning(
                            "やめたことを"
                            "入力してね。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_title.strip(),
                            edit_category,
                            edit_level,
                            edit_space,
                            edit_detail.strip(),
                            edit_comment.strip(),
                            edit_date,
                            edit_favorite,
                        )

                        st.rerun()

            with button_col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    delete_record(
                        data,
                        record_id,
                    )

                    st.rerun()


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
            "let_go_backup_"
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
    "増やすだけが前進じゃない。"
    "やめたことで、生まれるものもある。🌿✨"
)
