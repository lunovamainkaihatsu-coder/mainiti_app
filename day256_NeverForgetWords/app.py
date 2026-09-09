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
    page_title="忘れたくない一言",
    page_icon="💬",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "words.json",
)

MAX_WORDS_PER_DAY = 3

CATEGORIES = [
    "🔥 気づき",
    "💡 アイデア",
    "❤️ 大事にしたい",
    "📚 学び",
    "💼 仕事",
    "🤖 AI・開発",
    "🎨 創作",
    "👨‍👩‍👧 家族",
    "🌱 自分へ",
    "✨ その他",
]

MOODS = [
    "😄 とても良い",
    "🙂 良い",
    "😌 穏やか",
    "😐 普通",
    "😕 モヤモヤ",
    "😢 落ち込み",
    "🔥 やる気",
    "🤔 考え中",
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
        "words": []
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
            "words",
            [],
        )

        for item in data["words"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "word",
                "",
            )

            item.setdefault(
                "category",
                "✨ その他",
            )

            item.setdefault(
                "mood",
                "😐 普通",
            )

            item.setdefault(
                "memo",
                "",
            )

            item.setdefault(
                "favorite",
                False,
            )

            item.setdefault(
                "record_date",
                str(date.today()),
            )

            item.setdefault(
                "created_at",
                now_text(),
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

def get_word_by_id(
    data,
    word_id,
):
    return next(
        (
            item
            for item in data["words"]
            if item.get("id") == word_id
        ),
        None,
    )


def parse_date(
    text,
):
    try:
        return datetime.strptime(
            text,
            "%Y-%m-%d",
        ).date()

    except (
        ValueError,
        TypeError,
    ):
        return date.today()


def format_date(
    text,
):
    target = parse_date(
        text
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


def format_datetime(
    text,
):
    try:
        target = datetime.fromisoformat(
            text
        )

        return target.strftime(
            "%Y/%m/%d %H:%M"
        )

    except (
        ValueError,
        TypeError,
    ):
        return ""


def days_ago_text(
    record_date,
):
    target = parse_date(
        record_date
    )

    difference = (
        date.today()
        - target
    ).days

    if difference == 0:
        return "今日の自分から"

    if difference == 1:
        return "昨日の自分から"

    if difference > 0:
        return f"{difference}日前の自分から"

    return "未来の日付の記録"


def calculate_streak(
    words,
):
    if not words:
        return 0

    recorded_dates = {
        parse_date(
            item.get(
                "record_date",
                "",
            )
        )
        for item in words
    }

    current = date.today()

    # 今日の記録がない場合は、
    # 昨日から連続しているかを見る
    if current not in recorded_dates:
        current -= timedelta(
            days=1
        )

    streak = 0

    while current in recorded_dates:
        streak += 1
        current -= timedelta(
            days=1
        )

    return streak


# =========================================================
# CRUD
# =========================================================

def add_word(
    data,
    word,
    category,
    mood,
    memo,
    favorite,
    record_date,
):
    data[
        "words"
    ].append(
        {
            "id": create_id(),
            "word": word,
            "category": category,
            "mood": mood,
            "memo": memo,
            "favorite": favorite,
            "record_date": str(
                record_date
            ),
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_word(
    data,
    word_id,
    word,
    category,
    mood,
    memo,
    favorite,
    record_date,
):
    item = get_word_by_id(
        data,
        word_id,
    )

    if not item:
        return

    item[
        "word"
    ] = word

    item[
        "category"
    ] = category

    item[
        "mood"
    ] = mood

    item[
        "memo"
    ] = memo

    item[
        "favorite"
    ] = favorite

    item[
        "record_date"
    ] = str(
        record_date
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    word_id,
):
    item = get_word_by_id(
        data,
        word_id,
    )

    if not item:
        return

    item[
        "favorite"
    ] = not item.get(
        "favorite",
        False,
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_word(
    data,
    word_id,
):
    data[
        "words"
    ] = [
        item
        for item in data[
            "words"
        ]
        if item.get(
            "id"
        )
        != word_id
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
        background: rgba(120, 130, 255, 0.07);
        border: 1px solid rgba(120, 130, 255, 0.15);
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
                rgba(110, 130, 255, 0.16),
                rgba(255, 170, 180, 0.10)
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

    .random-box {
        padding: 30px;
        border-radius: 24px;
        margin-top: 15px;
        margin-bottom: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(110, 130, 255, 0.12),
                rgba(255, 190, 100, 0.10)
            );

        text-align: center;
    }

    .random-label {
        font-size: 0.95rem;
        opacity: 0.68;
        font-weight: 700;
    }

    .random-word {
        font-size: 1.7rem;
        font-weight: 900;
        margin-top: 14px;
        margin-bottom: 14px;
        line-height: 1.6;
    }

    .today-count {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

words = data[
    "words"
]

today_text = str(
    date.today()
)

today_words = [
    item
    for item in words
    if item.get(
        "record_date"
    )
    == today_text
]

current_month = date.today().strftime(
    "%Y-%m"
)

month_words = [
    item
    for item in words
    if item.get(
        "record_date",
        "",
    ).startswith(
        current_month
    )
]

favorite_words = [
    item
    for item in words
    if item.get(
        "favorite",
        False,
    )
]

streak = calculate_streak(
    words
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>💬 忘れたくない一言</h1>

        <p>
            その瞬間の言葉を、
            未来の自分が拾える場所。
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
    "💬 今日",
    f"{len(today_words)}/{MAX_WORDS_PER_DAY}",
)

col2.metric(
    "📅 今月",
    f"{len(month_words)}個",
)

col3.metric(
    "🔥 連続記録",
    f"{streak}日",
)

col4.metric(
    "⭐ お気に入り",
    f"{len(favorite_words)}個",
)


# =========================================================
# 昔の一言をひろう
# =========================================================

st.divider()

st.subheader(
    "🎲 昔の一言をひろう"
)

past_words = [
    item
    for item in words
    if item.get(
        "record_date"
    )
    < today_text
]

if not past_words:
    st.info(
        "過去の一言が増えると、"
        "ここからランダムで再会できます。"
    )

else:
    if st.button(
        "🎲 昔の一言をひろう",
        use_container_width=True,
        type="primary",
    ):
        selected = random.choice(
            past_words
        )

        st.session_state[
            "random_word_id"
        ] = selected.get(
            "id"
        )

        st.rerun()


random_word_id = st.session_state.get(
    "random_word_id"
)

if random_word_id:
    random_item = get_word_by_id(
        data,
        random_word_id,
    )

    if random_item:
        st.markdown(
            f"""
            <div class="random-box">

                <div class="random-label">
                    📜 {days_ago_text(random_item.get('record_date', ''))}
                </div>

                <div class="random-word">
                    「{random_item.get('word', '')}」
                </div>

                <div>
                    {random_item.get('category', '')}
                    ｜ {random_item.get('mood', '')}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if random_item.get(
            "memo",
            "",
        ):
            st.write(
                "💭 "
                + random_item.get(
                    "memo",
                    "",
                )
            )

        col1, col2 = st.columns(
            2
        )

        with col1:
            if st.button(
                "🔄 別の一言",
                use_container_width=True,
            ):
                candidates = [
                    item
                    for item in past_words
                    if item.get(
                        "id"
                    )
                    != random_word_id
                ]

                if candidates:
                    selected = random.choice(
                        candidates
                    )

                    st.session_state[
                        "random_word_id"
                    ] = selected.get(
                        "id"
                    )

                st.rerun()

        with col2:
            if st.button(
                "✖ 閉じる",
                use_container_width=True,
            ):
                st.session_state.pop(
                    "random_word_id",
                    None,
                )

                st.rerun()


# =========================================================
# 今日の一言を登録
# =========================================================

st.divider()

st.subheader(
    "✍️ 今日の一言"
)

remaining_today = (
    MAX_WORDS_PER_DAY
    - len(today_words)
)

if remaining_today <= 0:
    st.success(
        "今日は3つ残せた！✨ "
        "また明日、新しい言葉を残そう。"
    )

else:
    st.caption(
        f"今日はあと "
        f"{remaining_today}個 "
        f"残せます。"
    )

    with st.form(
        "add_word_form"
    ):
        word = st.text_area(
            "忘れたくない一言",
            placeholder=(
                "例：完璧じゃなくても、進めばいい。"
            ),
            height=110,
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
            mood = st.selectbox(
                "今の気分",
                MOODS,
            )

        memo = st.text_area(
            "補足メモ",
            placeholder=(
                "この言葉を残した理由や、"
                "そのときの出来事など"
            ),
            height=90,
        )

        favorite = st.checkbox(
            "⭐ お気に入りにする"
        )

        submitted = st.form_submit_button(
            "💬 一言を残す",
            use_container_width=True,
        )

        if submitted:
            if not word.strip():
                st.error(
                    "一言を入力してください。"
                )

            elif len(
                today_words
            ) >= MAX_WORDS_PER_DAY:
                st.error(
                    "今日の登録は3件までです。"
                )

            else:
                add_word(
                    data,
                    word.strip(),
                    category,
                    mood,
                    memo.strip(),
                    favorite,
                    date.today(),
                )

                st.rerun()


# =========================================================
# 今日の記録
# =========================================================

if today_words:
    st.divider()

    st.subheader(
        "🌱 今日残した言葉"
    )

    sorted_today = sorted(
        today_words,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    for item in sorted_today:
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True,
        ):
            favorite_mark = (
                "⭐"
                if item.get(
                    "favorite",
                    False,
                )
                else "💬"
            )

            st.markdown(
                f"### {favorite_mark} "
                f"「{item.get('word', '')}」"
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('mood', '')}"
            )

            if item.get(
                "memo",
                "",
            ):
                st.write(
                    item.get(
                        "memo",
                        "",
                    )
                )

            col1, col2 = st.columns(
                2
            )

            with col1:
                favorite_text = (
                    "⭐ お気に入り解除"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    favorite_text,
                    key=(
                        "today_favorite_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            with col2:
                st.caption(
                    format_datetime(
                        item.get(
                            "created_at",
                            "",
                        )
                    )
                )


# =========================================================
# 検索・履歴
# =========================================================

st.divider()

st.subheader(
    "📚 一言の図書館"
)

search_text = st.text_input(
    "🔎 言葉やメモを検索",
    placeholder=(
        "例：挑戦、AI、焦らない..."
    ),
)

filter_col1, filter_col2 = st.columns(
    2
)

with filter_col1:
    category_filter = st.selectbox(
        "カテゴリー",
        [
            "すべて",
            *CATEGORIES,
        ],
        key="history_category",
    )

with filter_col2:
    favorite_only = st.checkbox(
        "⭐ お気に入りだけ",
    )


filtered_words = words.copy()

if search_text.strip():
    keyword = search_text.strip().lower()

    filtered_words = [
        item
        for item in filtered_words
        if (
            keyword
            in item.get(
                "word",
                "",
            ).lower()
            or keyword
            in item.get(
                "memo",
                "",
            ).lower()
        )
    ]

if category_filter != "すべて":
    filtered_words = [
        item
        for item in filtered_words
        if item.get(
            "category"
        )
        == category_filter
    ]

if favorite_only:
    filtered_words = [
        item
        for item in filtered_words
        if item.get(
            "favorite",
            False,
        )
    ]


filtered_words = sorted(
    filtered_words,
    key=lambda item: (
        item.get(
            "record_date",
            "",
        ),
        item.get(
            "created_at",
            "",
        ),
    ),
    reverse=True,
)


if not filtered_words:
    st.info(
        "条件に合う一言はありません。"
    )

else:
    for item in filtered_words:
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True,
        ):
            favorite_mark = (
                "⭐ "
                if item.get(
                    "favorite",
                    False,
                )
                else ""
            )

            st.markdown(
                f"### {favorite_mark}"
                f"「{item.get('word', '')}」"
            )

            st.caption(
                f"{format_date(item.get('record_date', ''))}"
                f" ｜ "
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('mood', '')}"
            )

            if item.get(
                "memo",
                "",
            ):
                st.write(
                    f"💭 {item.get('memo', '')}"
                )

            if st.button(
                (
                    "⭐ お気に入り解除"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                ),
                key=(
                    "history_favorite_"
                    + item_id
                ),
            ):
                toggle_favorite(
                    data,
                    item_id,
                )

                st.rerun()


# =========================================================
# 月別記録グラフ
# =========================================================

if words:
    st.divider()

    st.subheader(
        "📊 月ごとの記録"
    )

    month_counts = {}

    for item in words:
        month = item.get(
            "record_date",
            "",
        )[:7]

        if month:
            month_counts[
                month
            ] = (
                month_counts.get(
                    month,
                    0,
                )
                + 1
            )

    chart_rows = [
        {
            "月": month,
            "一言の数": count,
        }
        for month, count
        in sorted(
            month_counts.items()
        )
    ]

    chart_df = pd.DataFrame(
        chart_rows
    )

    if not chart_df.empty:
        chart_df = chart_df.set_index(
            "月"
        )

        st.bar_chart(
            chart_df
        )


# =========================================================
# カテゴリー別集計
# =========================================================

if words:
    st.divider()

    st.subheader(
        "🗂️ カテゴリー別"
    )

    category_counts = {}

    for item in words:
        category = item.get(
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

    category_df = pd.DataFrame(
        [
            {
                "カテゴリー": category,
                "件数": count,
            }
            for category, count
            in category_counts.items()
        ]
    ).sort_values(
        "件数",
        ascending=False,
    )

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 一言を編集・削除"
):
    if not words:
        st.caption(
            "まだ一言がありません。"
        )

    else:
        edit_items = sorted(
            words,
            key=lambda item: (
                item.get(
                    "record_date",
                    "",
                ),
                item.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        for item in edit_items:
            item_id = item.get(
                "id",
                "",
            )

            st.markdown(
                f"### 「{item.get('word', '')}」"
            )

            st.caption(
                format_date(
                    item.get(
                        "record_date",
                        "",
                    )
                )
            )

            with st.expander(
                "✏️ 編集"
            ):
                edit_word = st.text_area(
                    "一言",
                    value=item.get(
                        "word",
                        "",
                    ),
                    key=(
                        "edit_word_"
                        + item_id
                    ),
                )

                current_category = item.get(
                    "category",
                    "✨ その他",
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
                        else len(
                            CATEGORIES
                        ) - 1
                    ),
                    key=(
                        "edit_category_"
                        + item_id
                    ),
                )

                current_mood = item.get(
                    "mood",
                    "😐 普通",
                )

                edit_mood = st.selectbox(
                    "気分",
                    MOODS,
                    index=(
                        MOODS.index(
                            current_mood
                        )
                        if current_mood
                        in MOODS
                        else 3
                    ),
                    key=(
                        "edit_mood_"
                        + item_id
                    ),
                )

                edit_memo = st.text_area(
                    "補足メモ",
                    value=item.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + item_id
                    ),
                )

                edit_date = st.date_input(
                    "日付",
                    value=parse_date(
                        item.get(
                            "record_date",
                            "",
                        )
                    ),
                    key=(
                        "edit_date_"
                        + item_id
                    ),
                )

                edit_favorite = st.checkbox(
                    "⭐ お気に入り",
                    value=item.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "edit_favorite_"
                        + item_id
                    ),
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_word.strip():
                        st.error(
                            "一言を入力してください。"
                        )

                    else:
                        # 日付変更時の3件制限チェック
                        same_day_other_items = [
                            other
                            for other in words
                            if (
                                other.get(
                                    "id"
                                )
                                != item_id
                                and other.get(
                                    "record_date"
                                )
                                == str(
                                    edit_date
                                )
                            )
                        ]

                        if len(
                            same_day_other_items
                        ) >= MAX_WORDS_PER_DAY:
                            st.error(
                                "その日はすでに3件登録されています。"
                            )

                        else:
                            update_word(
                                data,
                                item_id,
                                edit_word.strip(),
                                edit_category,
                                edit_mood,
                                edit_memo.strip(),
                                edit_favorite,
                                edit_date,
                            )

                            st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この一言を削除",
                    key=(
                        "delete_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    delete_word(
                        data,
                        item_id,
                    )

                    if (
                        st.session_state.get(
                            "random_word_id"
                        )
                        == item_id
                    ):
                        st.session_state.pop(
                            "random_word_id",
                            None,
                        )

                    st.rerun()

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
            "never_forget_words_"
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
    "その瞬間の言葉を、未来の自分が拾える場所。💬✨"
)
