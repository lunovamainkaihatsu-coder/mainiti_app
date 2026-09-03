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
    page_title="250日できたこと図鑑",
    page_icon="📚",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "achievements.json",
)

CATEGORIES = [
    "📱 アプリ開発",
    "🤖 AI・プログラミング",
    "🎨 イラスト",
    "📚 勉強",
    "💼 仕事",
    "🏠 生活",
    "💪 運動",
    "🔥 挑戦",
    "✨ その他",
]

DIFFICULTIES = [
    "★☆☆☆☆",
    "★★☆☆☆",
    "★★★☆☆",
    "★★★★☆",
    "★★★★★",
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
        "achievements": []
    }


# =========================================================
# データ保存・読み込み
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
            "achievements",
            [],
        )

        for achievement in data[
            "achievements"
        ]:
            achievement.setdefault(
                "id",
                create_id(),
            )

            achievement.setdefault(
                "number",
                0,
            )

            achievement.setdefault(
                "title",
                "",
            )

            achievement.setdefault(
                "category",
                "✨ その他",
            )

            achievement.setdefault(
                "date",
                str(date.today()),
            )

            achievement.setdefault(
                "memo",
                "",
            )

            achievement.setdefault(
                "difficulty",
                "★★★☆☆",
            )

            achievement.setdefault(
                "favorite",
                False,
            )

            achievement.setdefault(
                "created_at",
                "",
            )

            achievement.setdefault(
                "updated_at",
                "",
            )

        repair_numbers(data)

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
# 番号処理
# =========================================================

def repair_numbers(data):
    achievements = data.get(
        "achievements",
        [],
    )

    sorted_items = sorted(
        achievements,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            ),
            item.get(
                "date",
                "",
            ),
        ),
    )

    changed = False

    for index, item in enumerate(
        sorted_items,
        start=1,
    ):
        if item.get(
            "number"
        ) != index:
            item[
                "number"
            ] = index

            changed = True

    if changed:
        save_data(data)


def next_number(data):
    achievements = data.get(
        "achievements",
        [],
    )

    if not achievements:
        return 1

    return max(
        int(
            item.get(
                "number",
                0,
            )
        )
        for item in achievements
    ) + 1


def format_number(
    number,
):
    return f"No.{int(number):03d}"


# =========================================================
# 補助関数
# =========================================================

def get_achievement_by_id(
    data,
    achievement_id,
):
    return next(
        (
            item
            for item in data[
                "achievements"
            ]
            if item.get(
                "id"
            )
            == achievement_id
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


# =========================================================
# CRUD
# =========================================================

def add_achievement(
    data,
    title,
    category,
    achieved_date,
    memo,
    difficulty,
    favorite,
):
    data[
        "achievements"
    ].append(
        {
            "id": create_id(),
            "number": next_number(
                data
            ),
            "title": title,
            "category": category,
            "date": str(
                achieved_date
            ),
            "memo": memo,
            "difficulty": difficulty,
            "favorite": favorite,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_achievement(
    data,
    achievement_id,
    title,
    category,
    achieved_date,
    memo,
    difficulty,
    favorite,
):
    achievement = (
        get_achievement_by_id(
            data,
            achievement_id,
        )
    )

    if not achievement:
        return

    achievement[
        "title"
    ] = title

    achievement[
        "category"
    ] = category

    achievement[
        "date"
    ] = str(
        achieved_date
    )

    achievement[
        "memo"
    ] = memo

    achievement[
        "difficulty"
    ] = difficulty

    achievement[
        "favorite"
    ] = favorite

    achievement[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    achievement_id,
):
    achievement = (
        get_achievement_by_id(
            data,
            achievement_id,
        )
    )

    if not achievement:
        return

    achievement[
        "favorite"
    ] = not achievement.get(
        "favorite",
        False,
    )

    achievement[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_achievement(
    data,
    achievement_id,
):
    data[
        "achievements"
    ] = [
        item
        for item in data[
            "achievements"
        ]
        if item.get(
            "id"
        )
        != achievement_id
    ]

    repair_numbers(
        data
    )

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
                rgba(120, 130, 255, 0.18),
                rgba(255, 190, 90, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.78;
    }

    .achievement-card {
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(120, 130, 255, 0.15);
        margin-bottom: 12px;
        min-height: 210px;
    }

    .achievement-number {
        font-size: 0.9rem;
        opacity: 0.65;
        font-weight: 700;
    }

    .achievement-title {
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .random-box {
        padding: 28px;
        border-radius: 22px;
        text-align: center;
        background: rgba(120, 130, 255, 0.07);
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .random-number {
        font-size: 1rem;
        opacity: 0.65;
        font-weight: 700;
    }

    .random-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 10px;
    }

    .milestone-box {
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        background: rgba(255, 190, 90, 0.08);
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .milestone-number {
        font-size: 2rem;
        font-weight: 900;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

achievements = data[
    "achievements"
]

current_month = date.today().strftime(
    "%Y-%m"
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>📚 250日できたこと図鑑</h1>

        <p>
            小さな「できた」も、
            集めれば立派な自分の歴史になる。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

monthly_count = len(
    [
        item
        for item in achievements
        if item.get(
            "date",
            "",
        ).startswith(
            current_month
        )
    ]
)

favorite_count = len(
    [
        item
        for item in achievements
        if item.get(
            "favorite",
            False,
        )
    ]
)

category_count = len(
    {
        item.get(
            "category"
        )
        for item in achievements
        if item.get(
            "category"
        )
    }
)


columns = st.columns(
    4
)

columns[0].metric(
    "📚 登録数",
    f"{len(achievements)}個",
)

columns[1].metric(
    "🔥 今月",
    f"{monthly_count}個",
)

columns[2].metric(
    "⭐ お気に入り",
    f"{favorite_count}個",
)

columns[3].metric(
    "🏆 カテゴリー",
    f"{category_count}種類",
)


if achievements:
    st.markdown(
        f"""
        <div class="milestone-box">

            <div class="milestone-number">
                ✨ {len(achievements)}個
            </div>

            <div>
                の「できた」が図鑑に集まりました。
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい「できた」を登録"
)

with st.form(
    "add_achievement_form"
):
    title = st.text_input(
        "何ができた？",
        placeholder=(
            "例：初めてStreamlitアプリを完成させた"
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
        achieved_date = (
            st.date_input(
                "できた日",
                value=date.today(),
            )
        )

    difficulty = st.select_slider(
        "難易度",
        options=DIFFICULTIES,
        value="★★★☆☆",
    )

    memo = st.text_area(
        "ひとこと",
        placeholder=(
            "例：最初は難しかったけど、"
            "最後まで動かせた！"
        ),
        height=100,
    )

    favorite = st.checkbox(
        "⭐ お気に入りにする"
    )

    submitted = (
        st.form_submit_button(
            "📚 図鑑に登録",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.error(
                "できたことを入力してください。"
            )

        else:
            add_achievement(
                data,
                title.strip(),
                category,
                achieved_date,
                memo.strip(),
                difficulty,
                favorite,
            )

            st.success(
                "図鑑に新しい1ページが増えました！"
            )

            st.rerun()


# =========================================================
# ランダム発掘
# =========================================================

if achievements:
    st.divider()

    st.subheader(
        "🎲 過去の自分を発掘"
    )

    valid_ids = {
        item.get(
            "id"
        )
        for item in achievements
    }

    if (
        "random_achievement_id"
        not in st.session_state
        or st.session_state[
            "random_achievement_id"
        ]
        not in valid_ids
    ):
        st.session_state[
            "random_achievement_id"
        ] = random.choice(
            achievements
        ).get(
            "id"
        )

    random_item = (
        get_achievement_by_id(
            data,
            st.session_state[
                "random_achievement_id"
            ],
        )
    )

    if random_item:
        favorite_mark = (
            "⭐"
            if random_item.get(
                "favorite",
                False,
            )
            else ""
        )

        st.markdown(
            f"""
            <div class="random-box">

                <div class="random-number">
                    {format_number(random_item.get('number', 0))}
                </div>

                <div class="random-title">
                    {favorite_mark}
                    {random_item.get('title', '')}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"{random_item.get('category', '')}"
            f" ／ "
            f"{format_date(random_item.get('date', ''))}"
            f" ／ "
            f"{random_item.get('difficulty', '')}"
        )

        if random_item.get(
            "memo",
            "",
        ):
            st.write(
                f"💬 "
                f"{random_item.get('memo', '')}"
            )

    if st.button(
        "🎲 別の記録を発掘",
        use_container_width=True,
    ):
        if len(
            achievements
        ) > 1:
            candidates = [
                item
                for item in achievements
                if item.get(
                    "id"
                )
                != st.session_state.get(
                    "random_achievement_id"
                )
            ]

            st.session_state[
                "random_achievement_id"
            ] = random.choice(
                candidates
            ).get(
                "id"
            )

        st.rerun()


# =========================================================
# 検索・絞り込み
# =========================================================

st.divider()

st.subheader(
    "🔍 できたこと図鑑"
)

search_text = st.text_input(
    "検索",
    placeholder=(
        "タイトルやメモから検索"
    ),
)

filter_col1, filter_col2, filter_col3 = (
    st.columns(
        3
    )
)

with filter_col1:
    category_filter = st.selectbox(
        "カテゴリー",
        [
            "すべて",
            *CATEGORIES,
        ],
    )

with filter_col2:
    favorite_filter = st.selectbox(
        "お気に入り",
        [
            "すべて",
            "⭐ お気に入りのみ",
            "お気に入り以外",
        ],
    )

with filter_col3:
    sort_mode = st.selectbox(
        "並び順",
        [
            "新しい順",
            "古い順",
            "図鑑番号順",
            "難易度が高い順",
        ],
    )


filtered = achievements.copy()


# 検索
if search_text.strip():
    keyword = search_text.strip().lower()

    filtered = [
        item
        for item in filtered
        if keyword
        in (
            item.get(
                "title",
                ""
            )
            + " "
            + item.get(
                "memo",
                ""
            )
        ).lower()
    ]


# カテゴリー
if category_filter != "すべて":
    filtered = [
        item
        for item in filtered
        if item.get(
            "category"
        )
        == category_filter
    ]


# お気に入り
if (
    favorite_filter
    == "⭐ お気に入りのみ"
):
    filtered = [
        item
        for item in filtered
        if item.get(
            "favorite",
            False,
        )
    ]

elif (
    favorite_filter
    == "お気に入り以外"
):
    filtered = [
        item
        for item in filtered
        if not item.get(
            "favorite",
            False,
        )
    ]


# ソート
if sort_mode == "新しい順":
    filtered = sorted(
        filtered,
        key=lambda item: (
            item.get(
                "date",
                ""
            ),
            item.get(
                "created_at",
                ""
            ),
        ),
        reverse=True,
    )

elif sort_mode == "古い順":
    filtered = sorted(
        filtered,
        key=lambda item: (
            item.get(
                "date",
                ""
            ),
            item.get(
                "created_at",
                ""
            ),
        ),
    )

elif sort_mode == "図鑑番号順":
    filtered = sorted(
        filtered,
        key=lambda item: int(
            item.get(
                "number",
                0,
            )
        ),
    )

elif (
    sort_mode
    == "難易度が高い順"
):
    filtered = sorted(
        filtered,
        key=lambda item: (
            DIFFICULTIES.index(
                item.get(
                    "difficulty",
                    "★★★☆☆",
                )
            )
            if item.get(
                "difficulty",
                "★★★☆☆",
            )
            in DIFFICULTIES
            else 0
        ),
        reverse=True,
    )


st.caption(
    f"{len(filtered)}件表示中"
)


# =========================================================
# 図鑑カード表示
# =========================================================

if not filtered:
    st.info(
        "条件に合う記録がありません。"
    )

else:
    for start in range(
        0,
        len(filtered),
        3,
    ):
        cols = st.columns(
            3
        )

        row_items = filtered[
            start:start + 3
        ]

        for col, item in zip(
            cols,
            row_items,
        ):
            achievement_id = (
                item.get(
                    "id",
                    "",
                )
            )

            favorite_mark = (
                "⭐"
                if item.get(
                    "favorite",
                    False,
                )
                else ""
            )

            with col:
                with st.container(
                    border=True,
                ):
                    st.caption(
                        format_number(
                            item.get(
                                "number",
                                0,
                            )
                        )
                    )

                    st.markdown(
                        f"### "
                        f"{favorite_mark}"
                        f"{item.get('title', '')}"
                    )

                    st.caption(
                        item.get(
                            "category",
                            "",
                        )
                    )

                    st.write(
                        f"📅 "
                        f"{format_date(item.get('date', ''))}"
                    )

                    st.write(
                        f"🎯 "
                        f"{item.get('difficulty', '')}"
                    )

                    if item.get(
                        "memo",
                        "",
                    ):
                        preview = item.get(
                            "memo",
                            "",
                        )

                        if len(
                            preview
                        ) > 100:
                            preview = (
                                preview[:100]
                                + "…"
                            )

                        st.write(
                            f"💬 {preview}"
                        )

                    if st.button(
                        (
                            "☆ お気に入り"
                            if not item.get(
                                "favorite",
                                False,
                            )
                            else "⭐ 登録済み"
                        ),
                        key=(
                            "favorite_"
                            + achievement_id
                        ),
                        use_container_width=True,
                    ):
                        toggle_favorite(
                            data,
                            achievement_id,
                        )

                        st.rerun()


# =========================================================
# カテゴリー別グラフ
# =========================================================

if achievements:
    st.divider()

    st.subheader(
        "📊 積み上げの内訳"
    )

    category_rows = []

    for category_name in CATEGORIES:
        count = len(
            [
                item
                for item in achievements
                if item.get(
                    "category"
                )
                == category_name
            ]
        )

        if count > 0:
            category_rows.append(
                {
                    "カテゴリー": (
                        category_name
                    ),
                    "できた数": count,
                }
            )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        ).sort_values(
            "できた数",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# お気に入り一覧
# =========================================================

favorite_items = [
    item
    for item in achievements
    if item.get(
        "favorite",
        False,
    )
]

if favorite_items:
    st.divider()

    with st.expander(
        "⭐ お気に入り図鑑"
    ):
        favorite_items = sorted(
            favorite_items,
            key=lambda item: (
                item.get(
                    "number",
                    0,
                )
            ),
        )

        for item in favorite_items:
            st.markdown(
                f"**{format_number(item.get('number', 0))} "
                f"⭐ {item.get('title', '')}**"
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ／ "
                f"{item.get('date', '')}"
            )

            st.divider()


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 図鑑を編集・管理"
):
    if not achievements:
        st.info(
            "まだ登録がありません。"
        )

    else:
        sorted_items = sorted(
            achievements,
            key=lambda item: (
                item.get(
                    "number",
                    0,
                )
            ),
            reverse=True,
        )

        for item in sorted_items:
            achievement_id = (
                item.get(
                    "id",
                    "",
                )
            )

            st.markdown(
                f"### "
                f"{format_number(item.get('number', 0))} "
                f"{item.get('title', '')}"
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ／ "
                f"{item.get('date', '')}"
            )

            with st.expander(
                "✏️ 編集",
            ):
                edit_title = st.text_input(
                    "できたこと",
                    value=item.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + achievement_id
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
                            else 0
                        ),
                        key=(
                            "edit_category_"
                            + achievement_id
                        ),
                    )
                )

                try:
                    current_date = (
                        datetime.strptime(
                            item.get(
                                "date",
                                str(
                                    date.today()
                                ),
                            ),
                            "%Y-%m-%d",
                        ).date()
                    )

                except ValueError:
                    current_date = (
                        date.today()
                    )

                edit_date = st.date_input(
                    "できた日",
                    value=current_date,
                    key=(
                        "edit_date_"
                        + achievement_id
                    ),
                )

                current_difficulty = (
                    item.get(
                        "difficulty",
                        "★★★☆☆",
                    )
                )

                edit_difficulty = (
                    st.select_slider(
                        "難易度",
                        options=DIFFICULTIES,
                        value=(
                            current_difficulty
                            if current_difficulty
                            in DIFFICULTIES
                            else "★★★☆☆"
                        ),
                        key=(
                            "edit_difficulty_"
                            + achievement_id
                        ),
                    )
                )

                edit_memo = st.text_area(
                    "ひとこと",
                    value=item.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + achievement_id
                    ),
                )

                edit_favorite = (
                    st.checkbox(
                        "⭐ お気に入り",
                        value=item.get(
                            "favorite",
                            False,
                        ),
                        key=(
                            "edit_favorite_"
                            + achievement_id
                        ),
                    )
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + achievement_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.error(
                            "できたことを入力してください。"
                        )

                    else:
                        update_achievement(
                            data,
                            achievement_id,
                            edit_title.strip(),
                            edit_category,
                            edit_date,
                            edit_memo.strip(),
                            edit_difficulty,
                            edit_favorite,
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                st.warning(
                    "削除すると図鑑番号は詰め直されます。"
                )

                if st.button(
                    "この記録を削除",
                    key=(
                        "delete_"
                        + achievement_id
                    ),
                    use_container_width=True,
                ):
                    delete_achievement(
                        data,
                        achievement_id,
                    )

                    if (
                        st.session_state.get(
                            "random_achievement_id"
                        )
                        == achievement_id
                    ):
                        st.session_state.pop(
                            "random_achievement_id",
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
            "achievement_encyclopedia_"
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
    "250日は、250回前に進んだ証拠。📚✨"
)
