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
    page_title="今日のベスト1",
    page_icon="🏆",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "best_records.json",
)

CATEGORIES = [
    "👨‍👩‍👧 家族",
    "💻 AI・開発",
    "📚 勉強",
    "💼 仕事",
    "🎮 趣味・ゲーム",
    "🍽️ 食事",
    "🚶 お出かけ",
    "💪 健康・運動",
    "🌿 休息",
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


def month_label(month_text):
    try:
        target = datetime.strptime(
            month_text,
            "%Y-%m",
        )

        return (
            f"{target.year}年"
            f"{target.month}月"
        )

    except ValueError:
        return month_text


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
                "happiness",
                80,
            )

            record.setdefault(
                "reason",
                "",
            )

            record.setdefault(
                "keywords",
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


def get_record_by_date(
    data,
    target_date,
):
    target_text = str(
        target_date
    )

    return next(
        (
            record
            for record in data["records"]
            if record.get(
                "record_date"
            ) == target_text
        ),
        None,
    )


def add_record(
    data,
    title,
    category,
    happiness,
    reason,
    keywords,
    record_date,
):
    data["records"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "happiness": int(
                happiness
            ),
            "reason": reason,
            "keywords": keywords,
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
    happiness,
    reason,
    keywords,
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

    record["happiness"] = int(
        happiness
    )

    record["reason"] = reason
    record["keywords"] = keywords

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
# 集計関数
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


def average_happiness(records):
    if not records:
        return 0

    total = sum(
        int(
            record.get(
                "happiness",
                0,
            )
        )
        for record in records
    )

    return round(
        total / len(records),
        1,
    )


def most_common_category(records):
    if not records:
        return None, 0

    counts = {}

    for record in records:
        category = record.get(
            "category",
            "✨ その他",
        )

        counts[category] = (
            counts.get(
                category,
                0,
            )
            + 1
        )

    top_category = max(
        counts,
        key=counts.get,
    )

    return (
        top_category,
        counts[top_category],
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
            rgba(255, 190, 60, 0.08);
        border:
            1px solid
            rgba(255, 190, 60, 0.18);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 60, 0.20),
                rgba(255, 120, 170, 0.08)
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

    .best-box {
        padding: 25px;
        border-radius: 22px;
        margin-top: 10px;
        margin-bottom: 10px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 70, 0.13),
                rgba(255, 150, 100, 0.06)
            );
    }

    .big-score {
        font-size: 2.4rem;
        font-weight: 900;
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

today_record = get_record_by_date(
    data,
    today,
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🏆 今日のベスト1</h1>

        <p>
            どんな一日にも、
            今日のベストはきっとある。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今月のダッシュボード
# =========================================================

month_average = average_happiness(
    month_records
)

month_highest = max(
    [
        int(
            record.get(
                "happiness",
                0,
            )
        )
        for record in month_records
    ],
    default=0,
)

top_category, top_count = (
    most_common_category(
        month_records
    )
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🏆 今月のベスト",
    f"{len(month_records)}日分",
)

col2.metric(
    "😊 平均幸福度",
    (
        f"{month_average}%"
        if month_records
        else "-"
    ),
)

col3.metric(
    "🌟 最高幸福度",
    (
        f"{month_highest}%"
        if month_records
        else "-"
    ),
)

col4.metric(
    "❤️ 多いカテゴリー",
    (
        top_category
        if top_category
        else "-"
    ),
    (
        f"{top_count}日"
        if top_category
        else None
    ),
)


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "🏆 今日のベストを残す"
)

if today_record:
    with st.container(
        border=True
    ):
        st.markdown(
            f"### 🏆 "
            f"{today_record.get('title', '')}"
        )

        st.markdown(
            f"""
            <div class="big-score">
                😊 {today_record.get('happiness', 0)}%
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            today_record.get(
                "category",
                "✨ その他",
            )
        )

        if today_record.get(
            "reason",
            "",
        ):
            st.write(
                "**💬 なぜよかった？**"
            )

            st.write(
                today_record.get(
                    "reason",
                    "",
                )
            )

        if today_record.get(
            "keywords",
            "",
        ):
            st.caption(
                "📸 "
                + today_record.get(
                    "keywords",
                    "",
                )
            )

    st.info(
        "今日はすでにベスト1を"
        "記録しています。"
        "変更したい場合は編集欄から"
        "更新できます。"
    )

else:
    with st.form(
        "today_best_form"
    ):
        title = st.text_input(
            "今日、一番よかったことは？",
            placeholder=(
                "例：家族で一緒に笑った時間"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

        with col2:
            happiness = st.slider(
                "😊 幸福度",
                min_value=0,
                max_value=100,
                value=80,
                step=1,
            )

        reason = st.text_area(
            "💬 なぜよかった？",
            placeholder=(
                "例：何気ない時間だったけど"
                "楽しかった"
            ),
        )

        keywords = st.text_input(
            "📸 思い出キーワード",
            placeholder=(
                "例：夕食・笑顔・家族"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🏆 今日のベストにする",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "今日のベストを入力してね。"
                )

            else:
                add_record(
                    data,
                    title.strip(),
                    category,
                    happiness,
                    reason.strip(),
                    keywords.strip(),
                    today,
                )

                st.rerun()


# =========================================================
# ベスト・オブ・ベスト
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "👑 今月のベスト・オブ・ベスト"
    )

    best_record = max(
        month_records,
        key=lambda record: (
            int(
                record.get(
                    "happiness",
                    0,
                )
            ),
            record.get(
                "record_date",
                "",
            ),
        ),
    )

    with st.container(
        border=True
    ):
        st.caption(
            format_date(
                best_record.get(
                    "record_date",
                    "",
                )
            )
        )

        st.markdown(
            f"## 🏆 "
            f"{best_record.get('title', '')}"
        )

        st.markdown(
            f"""
            <div class="big-score">
                👑 {best_record.get('happiness', 0)}%
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            best_record.get(
                "category",
                "",
            )
        )

        if best_record.get(
            "reason",
            "",
        ):
            st.write(
                "**💬 なぜよかった？**"
            )

            st.write(
                best_record.get(
                    "reason",
                    "",
                )
            )

        if best_record.get(
            "keywords",
            "",
        ):
            st.caption(
                "📸 "
                + best_record.get(
                    "keywords",
                    "",
                )
            )


# =========================================================
# 幸福度推移
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "📈 今月の幸福度"
    )

    happiness_rows = []

    for record in month_records:
        happiness_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "幸福度": int(
                    record.get(
                        "happiness",
                        0,
                    )
                ),
            }
        )

    happiness_df = pd.DataFrame(
        happiness_rows
    )

    happiness_df = (
        happiness_df
        .sort_values(
            "日付"
        )
        .set_index(
            "日付"
        )
    )

    st.line_chart(
        happiness_df
    )


# =========================================================
# カテゴリー別幸福度
# =========================================================

if records:
    st.divider()

    st.subheader(
        "❤️ 何をしていると幸せ？"
    )

    category_rows = []

    for record in records:
        category_rows.append(
            {
                "カテゴリー": (
                    record.get(
                        "category",
                        "✨ その他",
                    )
                ),
                "幸福度": int(
                    record.get(
                        "happiness",
                        0,
                    )
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    category_average = (
        category_df
        .groupby(
            "カテゴリー",
            as_index=False,
        )["幸福度"]
        .mean()
    )

    category_average[
        "幸福度"
    ] = (
        category_average[
            "幸福度"
        ].round(1)
    )

    category_average = (
        category_average
        .sort_values(
            "幸福度",
            ascending=False,
        )
    )

    st.bar_chart(
        category_average.set_index(
            "カテゴリー"
        )
    )

    if not category_average.empty:
        top_happy = (
            category_average.iloc[0]
        )

        st.success(
            "😊 平均幸福度が一番高いのは "
            f"「{top_happy['カテゴリー']}」"
            f"（{top_happy['幸福度']}%）"
        )


# =========================================================
# 月別平均幸福度
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🗓️ 月ごとの幸福度"
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
                    "月": record_date[:7],
                    "幸福度": int(
                        record.get(
                            "happiness",
                            0,
                        )
                    ),
                }
            )

    if monthly_rows:
        monthly_df = pd.DataFrame(
            monthly_rows
        )

        monthly_average = (
            monthly_df
            .groupby(
                "月",
                as_index=False,
            )["幸福度"]
            .mean()
        )

        monthly_average[
            "幸福度"
        ] = (
            monthly_average[
                "幸福度"
            ].round(1)
        )

        monthly_average = (
            monthly_average
            .sort_values(
                "月"
            )
        )

        st.line_chart(
            monthly_average.set_index(
                "月"
            )
        )


# =========================================================
# あの日のベスト
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🎲 あの日のベスト"
    )

    if (
        "random_best_id"
        not in st.session_state
    ):
        st.session_state[
            "random_best_id"
        ] = None

    if st.button(
        "✨ 過去のベストを1つ見る",
        use_container_width=True,
    ):
        chosen = random.choice(
            records
        )

        st.session_state[
            "random_best_id"
        ] = chosen.get(
            "id"
        )

    random_id = st.session_state[
        "random_best_id"
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
                    f"### 🏆 "
                    f"{random_record.get('title', '')}"
                )

                st.write(
                    f"😊 幸福度 "
                    f"{random_record.get('happiness', 0)}%"
                )

                st.write(
                    random_record.get(
                        "category",
                        "",
                    )
                )

                if random_record.get(
                    "reason",
                    "",
                ):
                    st.write(
                        random_record.get(
                            "reason",
                            "",
                        )
                    )

                if random_record.get(
                    "keywords",
                    "",
                ):
                    st.caption(
                        "📸 "
                        + random_record.get(
                            "keywords",
                            "",
                        )
                    )


# =========================================================
# 思い出アルバム
# =========================================================

st.divider()

st.subheader(
    "📖 思い出アルバム"
)

search_text = st.text_input(
    "🔎 思い出を検索",
    placeholder=(
        "ベスト・理由・キーワードから検索"
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
        key="album_category",
    )

with filter_col3:
    display_filter = st.selectbox(
        "表示",
        [
            "すべて",
            "⭐ お気に入りのみ",
            "😊 90%以上",
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
        == "😊 90%以上"
        and int(
            record.get(
                "happiness",
                0,
            )
        ) < 90
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
                    "reason",
                    "",
                ),
                record.get(
                    "keywords",
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
        )
    ),
    reverse=True,
)


if not filtered_records:
    st.info(
        "条件に合う思い出はありません。"
    )

else:
    for record in filtered_records:
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
                st.caption(
                    format_date(
                        record.get(
                            "record_date",
                            "",
                        )
                    )
                )

                st.markdown(
                    f"### 🏆 "
                    f"{record.get('title', '')}"
                )

            with col2:
                favorite_icon = (
                    "⭐"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    favorite_icon,
                    key=(
                        "album_fav_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            info_col1, info_col2 = (
                st.columns(2)
            )

            info_col1.write(
                record.get(
                    "category",
                    "",
                )
            )

            info_col2.write(
                f"😊 "
                f"{record.get('happiness', 0)}%"
            )

            if record.get(
                "reason",
                "",
            ):
                st.write(
                    "**💬 なぜよかった？**"
                )

                st.write(
                    record.get(
                        "reason",
                        "",
                    )
                )

            if record.get(
                "keywords",
                "",
            ):
                st.caption(
                    "📸 "
                    + record.get(
                        "keywords",
                        "",
                    )
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
            )
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
                "今日のベスト",
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

            edit_happiness = (
                st.slider(
                    "😊 幸福度",
                    0,
                    100,
                    int(
                        record.get(
                            "happiness",
                            80,
                        )
                    ),
                    1,
                    key=(
                        "edit_happiness_"
                        + record_id
                    ),
                )
            )

            edit_reason = st.text_area(
                "なぜよかった？",
                value=record.get(
                    "reason",
                    "",
                ),
                key=(
                    "edit_reason_"
                    + record_id
                ),
            )

            edit_keywords = st.text_input(
                "思い出キーワード",
                value=record.get(
                    "keywords",
                    "",
                ),
                key=(
                    "edit_keywords_"
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
                    existing = (
                        get_record_by_date(
                            data,
                            edit_date,
                        )
                    )

                    if not edit_title.strip():
                        st.warning(
                            "今日のベストを入力してね。"
                        )

                    elif (
                        existing
                        and existing.get(
                            "id"
                        ) != record_id
                    ):
                        st.warning(
                            "その日にはすでに"
                            "ベスト1があります。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_title.strip(),
                            edit_category,
                            edit_happiness,
                            edit_reason.strip(),
                            edit_keywords.strip(),
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

                    if (
                        st.session_state.get(
                            "random_best_id"
                        )
                        == record_id
                    ):
                        st.session_state[
                            "random_best_id"
                        ] = None

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
            "today_best_"
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
    "どんな一日にも、"
    "今日のベストはきっとある。🏆🌙✨"
)
