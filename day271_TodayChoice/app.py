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
    page_title="今日、何を選んだ？",
    page_icon="🛤️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "choices.json",
)

CATEGORIES = [
    "🔥 挑戦",
    "🌿 休息",
    "📚 学び",
    "💼 仕事",
    "💰 お金",
    "👨‍👩‍👧 家族",
    "❤️ 人間関係",
    "💪 健康・運動",
    "🎨 創作",
    "🎮 趣味",
    "🏠 生活",
    "🧠 自分",
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


def stars(level):
    level = int(level)

    return (
        "★" * level
        + "☆" * (5 - level)
    )


def create_empty_data():
    return {
        "choices": [],
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
            "choices",
            [],
        )

        for choice in data["choices"]:
            choice.setdefault(
                "id",
                create_id(),
            )

            choice.setdefault(
                "title",
                "",
            )

            choice.setdefault(
                "chosen",
                "",
            )

            choice.setdefault(
                "not_chosen",
                "",
            )

            choice.setdefault(
                "category",
                "✨ その他",
            )

            choice.setdefault(
                "reason",
                "",
            )

            choice.setdefault(
                "satisfaction",
                3,
            )

            choice.setdefault(
                "memo",
                "",
            )

            choice.setdefault(
                "record_date",
                today_text(),
            )

            choice.setdefault(
                "favorite",
                False,
            )

            choice.setdefault(
                "created_at",
                now_text(),
            )

            choice.setdefault(
                "updated_at",
                choice.get(
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

def add_choice(
    data,
    title,
    chosen,
    not_chosen,
    category,
    reason,
    satisfaction,
    memo,
    record_date,
):
    data["choices"].append(
        {
            "id": create_id(),
            "title": title,
            "chosen": chosen,
            "not_chosen": not_chosen,
            "category": category,
            "reason": reason,
            "satisfaction": int(
                satisfaction
            ),
            "memo": memo,
            "record_date": str(
                record_date
            ),
            "favorite": False,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def get_choice(
    data,
    choice_id,
):
    return next(
        (
            choice
            for choice in data[
                "choices"
            ]
            if choice.get(
                "id"
            ) == choice_id
        ),
        None,
    )


def update_choice(
    data,
    choice_id,
    title,
    chosen,
    not_chosen,
    category,
    reason,
    satisfaction,
    memo,
    record_date,
):
    choice = get_choice(
        data,
        choice_id,
    )

    if not choice:
        return

    choice["title"] = title
    choice["chosen"] = chosen
    choice["not_chosen"] = (
        not_chosen
    )
    choice["category"] = category
    choice["reason"] = reason

    choice["satisfaction"] = int(
        satisfaction
    )

    choice["memo"] = memo

    choice["record_date"] = str(
        record_date
    )

    choice["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_choice(
    data,
    choice_id,
):
    data["choices"] = [
        choice
        for choice in data[
            "choices"
        ]
        if choice.get(
            "id"
        ) != choice_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    choice_id,
):
    choice = get_choice(
        data,
        choice_id,
    )

    if not choice:
        return

    choice["favorite"] = not (
        choice.get(
            "favorite",
            False,
        )
    )

    choice["updated_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# 集計関数
# =========================================================

def average_satisfaction(
    choices,
):
    if not choices:
        return 0

    return round(
        sum(
            int(
                choice.get(
                    "satisfaction",
                    0,
                )
            )
            for choice in choices
        )
        / len(choices),
        1,
    )


def current_streak(
    choices,
):
    if not choices:
        return 0

    dates = sorted(
        {
            parse_date(
                choice.get(
                    "record_date"
                )
            )
            for choice in choices
        },
        reverse=True,
    )

    if not dates:
        return 0

    today = date.today()

    if dates[0] not in [
        today,
        today - timedelta(
            days=1
        ),
    ]:
        return 0

    streak = 1
    current = dates[0]

    for value in dates[1:]:
        expected = (
            current
            - timedelta(
                days=1
            )
        )

        if value == expected:
            streak += 1
            current = value

        elif value < expected:
            break

    return streak


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
            rgba(90, 130, 220, 0.07);

        border:
            1px solid
            rgba(90, 130, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 120, 230, 0.18),
                rgba(160, 110, 230, 0.08)
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

    .choice-card {
        padding: 26px;
        border-radius: 22px;
        margin-bottom: 16px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 130, 230, 0.10),
                rgba(160, 120, 220, 0.05)
            );
    }

    .choice-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 14px;
    }

    .chosen {
        font-size: 1.15rem;
        font-weight: 700;
    }

    .memory-card {
        padding: 25px;
        border-radius: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(110, 140, 230, 0.10),
                rgba(180, 120, 210, 0.06)
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

choices = data[
    "choices"
]

today = date.today()

today_choices = [
    choice
    for choice in choices
    if choice.get(
        "record_date"
    ) == str(today)
]

current_month = (
    today.strftime(
        "%Y-%m"
    )
)

month_choices = [
    choice
    for choice in choices
    if choice.get(
        "record_date",
        "",
    ).startswith(
        current_month
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🛤️ 今日、何を選んだ？</h1>

        <p>
            人生は、大きな決断より
            小さな選択の積み重ね。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

streak = current_streak(
    choices
)

month_satisfaction = (
    average_satisfaction(
        month_choices
    )
)

favorite_count = len(
    [
        choice
        for choice in choices
        if choice.get(
            "favorite",
            False,
        )
    ]
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🛤️ 今日の選択",
    f"{len(today_choices)}回",
)

col2.metric(
    "📅 今月の選択",
    f"{len(month_choices)}回",
)

col3.metric(
    "✨ 平均納得度",
    (
        f"{month_satisfaction} / 5"
        if month_choices
        else "-"
    ),
)

col4.metric(
    "🔥 記録継続",
    f"{streak}日",
)


# =========================================================
# 新しい選択を記録
# =========================================================

st.divider()

st.subheader(
    "✍️ 今日の選択を残す"
)

st.caption(
    "大きな決断じゃなくてOK。"
    "今日、自分が選んだことをひとつ。"
)

with st.form(
    "new_choice_form",
    clear_on_submit=True,
):
    record_date = st.date_input(
        "📅 日付",
        value=date.today(),
    )

    title = st.text_input(
        "🛤️ どんな場面だった？",
        placeholder=(
            "例：夜の過ごし方"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        chosen = st.text_input(
            "✨ 選んだもの",
            placeholder=(
                "例：今日は休む"
            ),
        )

    with col2:
        not_chosen = st.text_input(
            "↔️ 選ばなかったもの",
            placeholder=(
                "例：勉強を続ける"
            ),
        )

    category = st.selectbox(
        "🏷️ カテゴリー",
        CATEGORIES,
    )

    reason = st.text_area(
        "💭 なぜ、それを選んだ？",
        placeholder=(
            "疲れていたので、"
            "今日は無理をしないことにした。"
        ),
    )

    satisfaction = st.slider(
        "😊 今の納得度",
        1,
        5,
        4,
    )

    st.caption(
        stars(
            satisfaction
        )
    )

    memo = st.text_area(
        "📝 一言メモ",
        placeholder=(
            "あとから振り返ったときに"
            "残しておきたいこと"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🛤️ この選択を残す",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not chosen.strip():
            st.warning(
                "「選んだもの」を"
                "入力してね。"
            )

        else:
            add_choice(
                data,
                title.strip(),
                chosen.strip(),
                not_chosen.strip(),
                category,
                reason.strip(),
                satisfaction,
                memo.strip(),
                record_date,
            )

            st.rerun()


# =========================================================
# 今日の選択
# =========================================================

if today_choices:
    st.divider()

    st.subheader(
        "🌱 今日、選んだこと"
    )

    for choice in sorted(
        today_choices,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        choice_id = choice.get(
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
                if choice.get(
                    "title"
                ):
                    st.markdown(
                        f"### 🛤️ "
                        f"{choice.get('title')}"
                    )

                else:
                    st.markdown(
                        "### 🛤️ 今日の選択"
                    )

            with col2:
                icon = (
                    "⭐"
                    if choice.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    icon,
                    key=(
                        "today_fav_"
                        + choice_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        choice_id,
                    )

                    st.rerun()

            st.success(
                "✨ 選んだ："
                + choice.get(
                    "chosen",
                    "",
                )
            )

            if choice.get(
                "not_chosen"
            ):
                st.caption(
                    "↔️ 選ばなかった："
                    + choice.get(
                        "not_chosen",
                        "",
                    )
                )

            st.write(
                choice.get(
                    "category",
                    ""
                )
            )

            st.write(
                "😊 納得度："
                + stars(
                    choice.get(
                        "satisfaction",
                        3,
                    )
                )
            )

            if choice.get(
                "reason"
            ):
                st.write(
                    "💭 "
                    + choice.get(
                        "reason",
                        "",
                    )
                )

            if choice.get(
                "memo"
            ):
                st.caption(
                    "📝 "
                    + choice.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 今月のカテゴリー分析
# =========================================================

st.divider()

st.subheader(
    "📊 今月、何を選んできた？"
)

if not month_choices:
    st.info(
        "今月の選択は"
        "まだ記録されていません。"
    )

else:
    category_rows = []

    for category in CATEGORIES:
        category_choices = [
            choice
            for choice in month_choices
            if choice.get(
                "category"
            ) == category
        ]

        if not category_choices:
            continue

        category_rows.append(
            {
                "カテゴリー": category,
                "選択回数": len(
                    category_choices
                ),
                "平均納得度": (
                    average_satisfaction(
                        category_choices
                    )
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "#### 🛤️ 選択回数"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )[
                ["選択回数"]
            ]
        )

    with col2:
        st.markdown(
            "#### 😊 平均納得度"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )[
                ["平均納得度"]
            ]
        )

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 日別推移
# =========================================================

if month_choices:
    st.divider()

    st.subheader(
        "📈 今月の選択の流れ"
    )

    daily_data = {}

    for choice in month_choices:
        record_date = choice.get(
            "record_date",
            "",
        )

        if record_date not in daily_data:
            daily_data[
                record_date
            ] = {
                "count": 0,
                "total": 0,
            }

        daily_data[
            record_date
        ]["count"] += 1

        daily_data[
            record_date
        ]["total"] += int(
            choice.get(
                "satisfaction",
                0,
            )
        )

    daily_rows = []

    for record_date in sorted(
        daily_data.keys()
    ):
        values = daily_data[
            record_date
        ]

        daily_rows.append(
            {
                "日付": record_date,
                "選択数": values[
                    "count"
                ],
                "平均納得度": round(
                    values[
                        "total"
                    ]
                    / values[
                        "count"
                    ],
                    1,
                ),
            }
        )

    daily_df = pd.DataFrame(
        daily_rows
    )

    st.line_chart(
        daily_df.set_index(
            "日付"
        )[
            ["平均納得度"]
        ]
    )


# =========================================================
# 過去の選択を再発見
# =========================================================

if choices:
    st.divider()

    st.subheader(
        "🔮 あの日、何を選んだ？"
    )

    st.caption(
        "過去の小さな分岐点を"
        "ランダムで振り返ります。"
    )

    if st.button(
        "🛤️ 過去の選択を見る",
        use_container_width=True,
    ):
        st.session_state[
            "random_choice_id"
        ] = random.choice(
            choices
        ).get(
            "id"
        )

    random_id = (
        st.session_state.get(
            "random_choice_id"
        )
    )

    if random_id:
        memory = get_choice(
            data,
            random_id,
        )

        if memory:
            memory_date = parse_date(
                memory.get(
                    "record_date"
                )
            )

            days_ago = (
                date.today()
                - memory_date
            ).days

            st.markdown(
                f"""
                <div class="memory-card">

                    <h3>
                        🕰️ {days_ago}日前の選択
                    </h3>

                    <div class="chosen">
                        ✨
                        {memory.get("chosen", "")}
                    </div>

                    <br>

                    <div>
                        {memory.get("category", "")}
                    </div>

                    <div>
                        納得度：
                        {stars(
                            memory.get(
                                "satisfaction",
                                3
                            )
                        )}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if memory.get(
                "not_chosen"
            ):
                st.caption(
                    "↔️ 選ばなかった："
                    + memory.get(
                        "not_chosen",
                        "",
                    )
                )

            if memory.get(
                "reason"
            ):
                st.write(
                    "💭 "
                    + memory.get(
                        "reason",
                        "",
                    )
                )


# =========================================================
# お気に入り
# =========================================================

favorite_choices = [
    choice
    for choice in choices
    if choice.get(
        "favorite",
        False,
    )
]

if favorite_choices:
    st.divider()

    st.subheader(
        "⭐ 残しておきたい選択"
    )

    for choice in sorted(
        favorite_choices,
        key=lambda item: (
            item.get(
                "record_date",
                "",
            )
        ),
        reverse=True,
    )[:10]:
        with st.container(
            border=True
        ):
            st.markdown(
                "### ✨ "
                + choice.get(
                    "chosen",
                    "",
                )
            )

            st.caption(
                choice.get(
                    "record_date",
                    ""
                )
                + " ｜ "
                + choice.get(
                    "category",
                    "",
                )
            )

            if choice.get(
                "reason"
            ):
                st.write(
                    choice.get(
                        "reason",
                        "",
                    )
                )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 選択の履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "選択・理由・メモから検索"
    ),
)

category_filter = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="history_category",
)

filtered_choices = []

for choice in choices:
    if (
        category_filter
        != "すべて"
        and choice.get(
            "category"
        )
        != category_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                choice.get(
                    "title",
                    "",
                ),
                choice.get(
                    "chosen",
                    "",
                ),
                choice.get(
                    "not_chosen",
                    "",
                ),
                choice.get(
                    "reason",
                    "",
                ),
                choice.get(
                    "memo",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text.lower()
            not in target
        ):
            continue

    filtered_choices.append(
        choice
    )


if not filtered_choices:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    rows = []

    for choice in sorted(
        filtered_choices,
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
    ):
        rows.append(
            {
                "日付": choice.get(
                    "record_date",
                    "",
                ),
                "選んだ": choice.get(
                    "chosen",
                    "",
                ),
                "選ばなかった": (
                    choice.get(
                        "not_chosen",
                        "",
                    )
                ),
                "カテゴリー": (
                    choice.get(
                        "category",
                        "",
                    )
                ),
                "納得度": stars(
                    choice.get(
                        "satisfaction",
                        3,
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            rows
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
    if not choices:
        st.caption(
            "まだ記録がありません。"
        )

    for choice in sorted(
        choices,
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
    ):
        choice_id = choice.get(
            "id",
            "",
        )

        label = (
            choice.get(
                "record_date",
                "",
            )
            + " ｜ "
            + choice.get(
                "chosen",
                "",
            )
        )

        with st.expander(
            label
        ):
            edit_date = st.date_input(
                "日付",
                value=parse_date(
                    choice.get(
                        "record_date"
                    )
                ),
                key=(
                    "edit_date_"
                    + choice_id
                ),
            )

            edit_title = st.text_input(
                "場面",
                value=choice.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + choice_id
                ),
            )

            edit_chosen = st.text_input(
                "選んだもの",
                value=choice.get(
                    "chosen",
                    "",
                ),
                key=(
                    "edit_chosen_"
                    + choice_id
                ),
            )

            edit_not_chosen = (
                st.text_input(
                    "選ばなかったもの",
                    value=choice.get(
                        "not_chosen",
                        "",
                    ),
                    key=(
                        "edit_not_chosen_"
                        + choice_id
                    ),
                )
            )

            current_category = (
                choice.get(
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
                        + choice_id
                    ),
                )
            )

            edit_reason = st.text_area(
                "理由",
                value=choice.get(
                    "reason",
                    "",
                ),
                key=(
                    "edit_reason_"
                    + choice_id
                ),
            )

            edit_satisfaction = (
                st.slider(
                    "納得度",
                    1,
                    5,
                    int(
                        choice.get(
                            "satisfaction",
                            3,
                        )
                    ),
                    key=(
                        "edit_sat_"
                        + choice_id
                    ),
                )
            )

            edit_memo = st.text_area(
                "メモ",
                value=choice.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + choice_id
                ),
            )

            edit_favorite = st.checkbox(
                "⭐ お気に入り",
                value=choice.get(
                    "favorite",
                    False,
                ),
                key=(
                    "edit_favorite_"
                    + choice_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + choice_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_chosen.strip()
                    ):
                        st.warning(
                            "選んだものを"
                            "入力してね。"
                        )

                    else:
                        update_choice(
                            data,
                            choice_id,
                            edit_title.strip(),
                            edit_chosen.strip(),
                            (
                                edit_not_chosen
                                .strip()
                            ),
                            edit_category,
                            edit_reason.strip(),
                            edit_satisfaction,
                            edit_memo.strip(),
                            edit_date,
                        )

                        updated = get_choice(
                            data,
                            choice_id,
                        )

                        if updated:
                            updated[
                                "favorite"
                            ] = (
                                edit_favorite
                            )

                            save_data(data)

                        st.rerun()

            with col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_"
                        + choice_id
                    ),
                    use_container_width=True,
                ):
                    delete_choice(
                        data,
                        choice_id,
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
            "today_choice_"
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
    "今日の小さな選択も、"
    "未来の自分をつくっている。🛤️✨"
)
