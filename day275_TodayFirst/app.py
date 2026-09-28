import json
import os
import random
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の初めて",
    page_icon="🌱",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "firsts.json")

CATEGORIES = [
    "🍜 食べ物",
    "📍 場所",
    "💻 技術",
    "📚 学び",
    "🎨 創作",
    "🎮 趣味",
    "👥 人",
    "💪 挑戦",
    "🏠 生活",
    "✨ その他",
]

LEVELS = {
    1: "🌱 小さな初めて",
    2: "✨ ちょっと新しい",
    3: "🚀 挑戦",
    4: "🔥 大きな挑戦",
    5: "🌍 人生級",
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


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


def stars(value):
    value = max(1, min(int(value), 5))

    return "★" * value + "☆" * (5 - value)


def create_empty_data():
    return {
        "records": []
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

    if not os.path.exists(DATA_FILE):
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

        if not isinstance(data, dict):
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
                1,
            )

            record.setdefault(
                "satisfaction",
                3,
            )

            record.setdefault(
                "again",
                True,
            )

            record.setdefault(
                "memo",
                "",
            )

            record.setdefault(
                "favorite",
                False,
            )

            record.setdefault(
                "record_date",
                today_text(),
            )

            record.setdefault(
                "created_at",
                now_text(),
            )

            record.setdefault(
                "updated_at",
                record.get(
                    "created_at",
                    now_text(),
                ),
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

def get_record(data, record_id):
    return next(
        (
            record
            for record in data["records"]
            if record.get("id") == record_id
        ),
        None,
    )


def add_record(
    data,
    title,
    category,
    level,
    satisfaction,
    again,
    memo,
    record_date,
):
    data["records"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "level": int(level),
            "satisfaction": int(satisfaction),
            "again": bool(again),
            "memo": memo,
            "favorite": False,
            "record_date": str(record_date),
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def update_record(
    data,
    record_id,
    title,
    category,
    level,
    satisfaction,
    again,
    memo,
    record_date,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["title"] = title
    record["category"] = category
    record["level"] = int(level)
    record["satisfaction"] = int(
        satisfaction
    )
    record["again"] = bool(again)
    record["memo"] = memo
    record["record_date"] = str(
        record_date
    )
    record["updated_at"] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    record_id,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["favorite"] = not record.get(
        "favorite",
        False,
    )

    record["updated_at"] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get("id") != record_id
    ]

    save_data(data)


# =========================================================
# 分析
# =========================================================

def calculate_streak(records):
    recorded_dates = {
        parse_date(
            record.get("record_date")
        )
        for record in records
    }

    if not recorded_dates:
        return 0

    today = date.today()
    yesterday = today - timedelta(days=1)

    if today in recorded_dates:
        current = today

    elif yesterday in recorded_dates:
        current = yesterday

    else:
        return 0

    streak = 0

    while current in recorded_dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


def average(values):
    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


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
            rgba(80, 180, 120, 0.07);

        border:
            1px solid
            rgba(80, 180, 120, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 190, 120, 0.18),
                rgba(120, 190, 230, 0.08)
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

    .memory-card {
        padding: 28px;
        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 190, 130, 0.12),
                rgba(130, 170, 230, 0.06)
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

records = data["records"]

today = date.today()

year_text = str(today.year)

month_text = today.strftime("%Y-%m")

year_records = [
    record
    for record in records
    if (
        record.get(
            "record_date",
            "",
        )
        or ""
    ).startswith(year_text)
]

month_records = [
    record
    for record in records
    if (
        record.get(
            "record_date",
            "",
        )
        or ""
    ).startswith(month_text)
]

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    ) == today_text()
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            🌱 今日の初めて
        </h1>

        <p>
            人生には、
            まだまだ「初めて」がある。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

streak = calculate_streak(
    records
)

if year_records:
    category_counts = {}

    for record in year_records:
        category = record.get(
            "category",
            "✨ その他",
        )

        category_counts[
            category
        ] = (
            category_counts.get(
                category,
                0,
            )
            + 1
        )

    top_category = max(
        category_counts,
        key=category_counts.get,
    )

else:
    top_category = "-"


col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌱 今年の初めて",
    f"{len(year_records)}個",
)

col2.metric(
    "📅 今月",
    f"{len(month_records)}個",
)

col3.metric(
    "🔥 初めてストリーク",
    f"{streak}日",
)

col4.metric(
    "🏆 一番多いカテゴリー",
    top_category,
)


# =========================================================
# 今日の初めてを追加
# =========================================================

st.divider()

st.subheader(
    "🌱 今日の初めて"
)

st.caption(
    "大きな挑戦じゃなくてOK。"
    "小さな「初めて」を残そう。"
)

with st.form(
    "new_first_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "✨ 今日、初めてやったことは？",
        placeholder=(
            "例：初めてこの店に入った"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        satisfaction = st.slider(
            "😊 満足度",
            1,
            5,
            4,
        )

        st.caption(
            stars(satisfaction)
        )

    with col2:
        level = st.slider(
            "🌱 初めてレベル",
            1,
            5,
            2,
        )

        st.info(
            LEVELS[level]
        )

        again = st.checkbox(
            "🔁 またやりたい",
            value=True,
        )

    memo = st.text_area(
        "📝 一言",
        placeholder=(
            "思ったより楽しかった！"
        ),
    )

    record_date = st.date_input(
        "📅 日付",
        value=date.today(),
    )

    submitted = (
        st.form_submit_button(
            "🌱 初めてを記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "今日の初めてを入力してね。"
            )

        else:
            add_record(
                data,
                title.strip(),
                category,
                level,
                satisfaction,
                again,
                memo.strip(),
                record_date,
            )

            st.rerun()


# =========================================================
# 今日の記録
# =========================================================

if today_records:
    st.divider()

    st.subheader(
        "✨ 今日見つけた初めて"
    )

    for record in reversed(
        today_records
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [7, 1]
            )

            with col1:
                st.markdown(
                    "### "
                    + record.get(
                        "category",
                        "",
                    )
                    + " "
                    + record.get(
                        "title",
                        "",
                    )
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
                "🌱 "
                + LEVELS.get(
                    int(
                        record.get(
                            "level",
                            1,
                        )
                    ),
                    "",
                )
            )

            st.write(
                "😊 "
                + stars(
                    record.get(
                        "satisfaction",
                        3,
                    )
                )
            )

            st.write(
                "🔁 またやりたい："
                + (
                    "YES"
                    if record.get(
                        "again",
                        False,
                    )
                    else "NO"
                )
            )

            if record.get("memo"):
                st.caption(
                    "📝 "
                    + record.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 今月の初めてレベル
# =========================================================

st.divider()

st.subheader(
    "🌱 今月の初めてレベル"
)

if not month_records:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    level_rows = []

    for level_number in range(
        1,
        6,
    ):
        count = len(
            [
                record
                for record in month_records
                if int(
                    record.get(
                        "level",
                        1,
                    )
                )
                == level_number
            ]
        )

        level_rows.append(
            {
                "レベル": LEVELS[
                    level_number
                ],
                "件数": count,
            }
        )

    level_df = pd.DataFrame(
        level_rows
    )

    st.bar_chart(
        level_df.set_index(
            "レベル"
        )
    )


# =========================================================
# 初めて図鑑
# =========================================================

st.divider()

st.subheader(
    "📖 初めて図鑑"
)

if not records:
    st.info(
        "まだ図鑑には何もありません。"
    )

else:
    category_rows = []

    for category in CATEGORIES:
        category_records = [
            record
            for record in records
            if record.get(
                "category"
            )
            == category
        ]

        if not category_records:
            continue

        category_rows.append(
            {
                "カテゴリー": category,
                "初めて": len(
                    category_records
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )

    selected_category = (
        st.selectbox(
            "📚 図鑑を見る",
            ["すべて"] + CATEGORIES,
        )
    )

    encyclopedia_records = [
        record
        for record in records
        if (
            selected_category
            == "すべて"
            or record.get(
                "category"
            )
            == selected_category
        )
    ]

    for record in sorted(
        encyclopedia_records,
        key=lambda item: (
            item.get(
                "record_date",
                ""
            )
        ),
        reverse=True,
    )[:30]:
        st.write(
            f"🌱 **{record.get('title', '')}**"
        )

        st.caption(
            f"{record.get('record_date', '')}"
            f" ｜ "
            f"{record.get('category', '')}"
            f" ｜ "
            f"{LEVELS.get(int(record.get('level', 1)), '')}"
        )


# =========================================================
# 過去の初めて再発見
# =========================================================

past_records = [
    record
    for record in records
    if parse_date(
        record.get(
            "record_date"
        )
    ) < today
]

if past_records:
    st.divider()

    st.subheader(
        "🎲 あの初めて、覚えてる？"
    )

    if (
        "memory_record_id"
        not in st.session_state
        or not get_record(
            data,
            st.session_state.get(
                "memory_record_id"
            ),
        )
    ):
        st.session_state[
            "memory_record_id"
        ] = random.choice(
            past_records
        ).get(
            "id"
        )

    memory_record = get_record(
        data,
        st.session_state[
            "memory_record_id"
        ],
    )

    if memory_record:
        memory_date = parse_date(
            memory_record.get(
                "record_date"
            )
        )

        days_ago = max(
            (
                today
                - memory_date
            ).days,
            0,
        )

        st.markdown(
            f"""
            <div class="memory-card">

                <div>
                    🎲 {days_ago}日前の初めて
                </div>

                <h3>
                    {memory_record.get("title", "")}
                </h3>

                <div>
                    {memory_record.get("category", "")}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            "🌱 "
            + LEVELS.get(
                int(
                    memory_record.get(
                        "level",
                        1,
                    )
                ),
                "",
            )
        )

        st.write(
            "😊 "
            + stars(
                memory_record.get(
                    "satisfaction",
                    3,
                )
            )
        )

        if memory_record.get(
            "memo"
        ):
            st.info(
                "📝 "
                + memory_record.get(
                    "memo",
                    "",
                )
            )

        st.write(
            "🔁 またやりたい："
            + (
                "YES"
                if memory_record.get(
                    "again",
                    False,
                )
                else "NO"
            )
        )

        if st.button(
            "🎲 別の初めてを見る",
            use_container_width=True,
        ):
            alternatives = [
                record
                for record in past_records
                if record.get(
                    "id"
                )
                != memory_record.get(
                    "id"
                )
            ]

            if alternatives:
                st.session_state[
                    "memory_record_id"
                ] = random.choice(
                    alternatives
                ).get(
                    "id"
                )

            st.rerun()


# =========================================================
# 年間分析
# =========================================================

st.divider()

st.subheader(
    f"🏆 {today.year}年の初めて"
)

if not year_records:
    st.info(
        "今年の記録はまだありません。"
    )

else:
    avg_satisfaction = average(
        [
            int(
                record.get(
                    "satisfaction",
                    0,
                )
            )
            for record in year_records
        ]
    )

    again_count = len(
        [
            record
            for record in year_records
            if record.get(
                "again",
                False,
            )
        ]
    )

    again_rate = round(
        again_count
        / len(year_records)
        * 100
    )

    level_total = sum(
        int(
            record.get(
                "level",
                1,
            )
        )
        for record in year_records
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "🌱 初めて",
        f"{len(year_records)}個",
    )

    col2.metric(
        "😊 平均満足度",
        f"{avg_satisfaction} / 5",
    )

    col3.metric(
        "🔁 またやりたい",
        f"{again_rate}%",
    )

    col4.metric(
        "🚀 初めてポイント",
        level_total,
    )

    # 月別集計
    month_rows = []

    for month in range(1, 13):
        month_key = (
            f"{today.year}-"
            f"{month:02d}"
        )

        count = len(
            [
                record
                for record in year_records
                if (
                    record.get(
                        "record_date",
                        ""
                    )
                    or ""
                ).startswith(
                    month_key
                )
            ]
        )

        month_rows.append(
            {
                "月": f"{month}月",
                "初めて": count,
            }
        )

    month_df = pd.DataFrame(
        month_rows
    )

    st.markdown(
        "#### 📅 月別"
    )

    st.bar_chart(
        month_df.set_index(
            "月"
        )
    )

    # カテゴリー別
    year_category_rows = []

    for category in CATEGORIES:
        count = len(
            [
                record
                for record in year_records
                if record.get(
                    "category"
                )
                == category
            ]
        )

        if count:
            year_category_rows.append(
                {
                    "カテゴリー": category,
                    "件数": count,
                }
            )

    if year_category_rows:
        year_category_df = (
            pd.DataFrame(
                year_category_rows
            )
        )

        st.markdown(
            "#### 📖 カテゴリー別"
        )

        st.bar_chart(
            year_category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# BEST初めて
# =========================================================

favorites = [
    record
    for record in records
    if record.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "🏆 BEST初めて"
    )

    favorite_records = sorted(
        favorites,
        key=lambda item: (
            int(
                item.get(
                    "level",
                    1,
                )
            ),
            int(
                item.get(
                    "satisfaction",
                    1,
                )
            ),
        ),
        reverse=True,
    )

    for record in favorite_records:
        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.markdown(
                "### ⭐ "
                + record.get(
                    "title",
                    "",
                )
            )

            st.caption(
                record.get(
                    "category",
                    "",
                )
                + " ｜ "
                + record.get(
                    "record_date",
                    "",
                )
            )

            st.write(
                "🌱 "
                + LEVELS.get(
                    int(
                        record.get(
                            "level",
                            1,
                        )
                    ),
                    "",
                )
            )

            st.write(
                "😊 "
                + stars(
                    record.get(
                        "satisfaction",
                        3,
                    )
                )
            )

            if record.get("memo"):
                st.write(
                    "📝 "
                    + record.get(
                        "memo",
                        "",
                    )
                )

            if st.button(
                "⭐ BESTから外す",
                key=(
                    "best_remove_"
                    + record_id
                ),
            ):
                toggle_favorite(
                    data,
                    record_id,
                )

                st.rerun()


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 初めて履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "Python、ラーメン、旅行……"
    ),
)

history_category = (
    st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="history_category",
    )
)

filtered_records = []

for record in records:
    if (
        history_category
        != "すべて"
        and record.get(
            "category"
        )
        != history_category
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
                    "memo",
                    "",
                ),
                record.get(
                    "category",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text
            .strip()
            .lower()
            not in target
        ):
            continue

    filtered_records.append(
        record
    )


if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    history_rows = []

    for record in sorted(
        filtered_records,
        key=lambda item: (
            item.get(
                "record_date",
                ""
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        history_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "初めて": record.get(
                    "title",
                    "",
                ),
                "カテゴリー": record.get(
                    "category",
                    "",
                ),
                "レベル": LEVELS.get(
                    int(
                        record.get(
                            "level",
                            1,
                        )
                    ),
                    "",
                ),
                "満足度": stars(
                    record.get(
                        "satisfaction",
                        3,
                    )
                ),
                "また": (
                    "YES"
                    if record.get(
                        "again",
                        False,
                    )
                    else "NO"
                ),
                "BEST": (
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
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
        key=lambda item: (
            item.get(
                "record_date",
                ""
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.expander(
            record.get(
                "record_date",
                "",
            )
            + " ｜ "
            + record.get(
                "title",
                "",
            )
        ):
            edit_title = st.text_input(
                "初めて",
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
                else len(CATEGORIES) - 1
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
                "初めてレベル",
                1,
                5,
                int(
                    record.get(
                        "level",
                        1,
                    )
                ),
                key=(
                    "edit_level_"
                    + record_id
                ),
            )

            edit_satisfaction = (
                st.slider(
                    "満足度",
                    1,
                    5,
                    int(
                        record.get(
                            "satisfaction",
                            3,
                        )
                    ),
                    key=(
                        "edit_satisfaction_"
                        + record_id
                    ),
                )
            )

            edit_again = st.checkbox(
                "またやりたい",
                value=record.get(
                    "again",
                    False,
                ),
                key=(
                    "edit_again_"
                    + record_id
                ),
            )

            edit_memo = st.text_area(
                "一言",
                value=record.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + record_id
                ),
            )

            edit_date = st.date_input(
                "日付",
                value=parse_date(
                    record.get(
                        "record_date"
                    )
                ),
                key=(
                    "edit_date_"
                    + record_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "初めてを入力してね。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_title.strip(),
                            edit_category,
                            edit_level,
                            edit_satisfaction,
                            edit_again,
                            edit_memo.strip(),
                            edit_date,
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ BESTから外す"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆ BESTに追加"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "favorite_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            if st.button(
                "🗑️ 完全削除",
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
                        "memory_record_id"
                    )
                    == record_id
                ):
                    st.session_state.pop(
                        "memory_record_id",
                        None,
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
            "today_first_"
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
    "大きな冒険じゃなくていい。"
    "今日の小さな「初めて」を集めよう。🌱✨"
)
