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
    page_title="1日1チャレンジ",
    page_icon="🚀",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "challenges.json",
)

CATEGORIES = [
    "🎨 創作",
    "📚 学び",
    "🚶 外出",
    "🍽️ 食事",
    "💻 技術",
    "💪 運動",
    "🌱 生活",
    "👨‍👩‍👧 家族",
    "🎮 趣味",
    "🧠 自分磨き",
    "✨ その他",
]

RESULTS = [
    "🎉 できた！",
    "😅 やってみたけど失敗",
    "💡 途中までやった",
]

FIRST_LEVELS = {
    1: "✨☆☆☆☆",
    2: "✨✨☆☆☆",
    3: "✨✨✨☆☆",
    4: "✨✨✨✨☆",
    5: "✨✨✨✨✨",
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
        "challenges": [],
        "history": [],
    }


def parse_date(text):
    try:
        return datetime.strptime(
            text,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def month_key(target):
    return target.strftime(
        "%Y-%m"
    )


def stars(level):
    level = int(level)

    return (
        "★" * level
        + "☆" * (5 - level)
    )


def first_stars(level):
    return FIRST_LEVELS.get(
        int(level),
        FIRST_LEVELS[1],
    )


def time_text(minutes):
    minutes = int(minutes)

    if minutes < 60:
        return f"約{minutes}分"

    hours = minutes / 60

    if hours.is_integer():
        return f"約{int(hours)}時間"

    return f"約{hours:.1f}時間"


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
            "challenges",
            [],
        )

        data.setdefault(
            "history",
            [],
        )

        for challenge in data["challenges"]:
            challenge.setdefault(
                "id",
                create_id(),
            )

            challenge.setdefault(
                "title",
                "",
            )

            challenge.setdefault(
                "category",
                "✨ その他",
            )

            challenge.setdefault(
                "difficulty",
                1,
            )

            challenge.setdefault(
                "minutes",
                10,
            )

            challenge.setdefault(
                "memo",
                "",
            )

            challenge.setdefault(
                "active",
                True,
            )

            challenge.setdefault(
                "favorite",
                False,
            )

            challenge.setdefault(
                "created_at",
                now_text(),
            )

        for item in data["history"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "challenge_id",
                "",
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
                "difficulty",
                1,
            )

            item.setdefault(
                "minutes",
                10,
            )

            item.setdefault(
                "result",
                "🎉 できた！",
            )

            item.setdefault(
                "satisfaction",
                80,
            )

            item.setdefault(
                "first_level",
                1,
            )

            item.setdefault(
                "comment",
                "",
            )

            item.setdefault(
                "again",
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

def get_challenge_by_id(
    data,
    challenge_id,
):
    return next(
        (
            challenge
            for challenge
            in data["challenges"]
            if challenge.get(
                "id"
            ) == challenge_id
        ),
        None,
    )


def add_challenge(
    data,
    title,
    category,
    difficulty,
    minutes,
    memo,
):
    data["challenges"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "difficulty": int(
                difficulty
            ),
            "minutes": int(
                minutes
            ),
            "memo": memo,
            "active": True,
            "favorite": False,
            "created_at": now_text(),
        }
    )

    save_data(data)


def update_challenge(
    data,
    challenge_id,
    title,
    category,
    difficulty,
    minutes,
    memo,
    active,
    favorite,
):
    challenge = get_challenge_by_id(
        data,
        challenge_id,
    )

    if not challenge:
        return

    challenge["title"] = title
    challenge["category"] = category
    challenge["difficulty"] = int(
        difficulty
    )
    challenge["minutes"] = int(
        minutes
    )
    challenge["memo"] = memo
    challenge["active"] = bool(
        active
    )
    challenge["favorite"] = bool(
        favorite
    )

    save_data(data)


def delete_challenge(
    data,
    challenge_id,
):
    data["challenges"] = [
        challenge
        for challenge
        in data["challenges"]
        if challenge.get(
            "id"
        ) != challenge_id
    ]

    save_data(data)


def add_history(
    data,
    challenge,
    result,
    satisfaction,
    first_level,
    comment,
    again,
):
    data["history"].append(
        {
            "id": create_id(),
            "challenge_id": (
                challenge.get(
                    "id",
                    "",
                )
            ),
            "title": challenge.get(
                "title",
                "",
            ),
            "category": challenge.get(
                "category",
                "✨ その他",
            ),
            "difficulty": int(
                challenge.get(
                    "difficulty",
                    1,
                )
            ),
            "minutes": int(
                challenge.get(
                    "minutes",
                    10,
                )
            ),
            "result": result,
            "satisfaction": int(
                satisfaction
            ),
            "first_level": int(
                first_level
            ),
            "comment": comment,
            "again": bool(
                again
            ),
            "record_date": str(
                date.today()
            ),
            "created_at": now_text(),
        }
    )

    save_data(data)


def delete_history(
    data,
    history_id,
):
    data["history"] = [
        item
        for item in data["history"]
        if item.get(
            "id"
        ) != history_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    challenge_id,
):
    challenge = get_challenge_by_id(
        data,
        challenge_id,
    )

    if not challenge:
        return

    challenge["favorite"] = not (
        challenge.get(
            "favorite",
            False,
        )
    )

    save_data(data)


# =========================================================
# 連続挑戦日数
# =========================================================

def calculate_streak(history):
    if not history:
        return 0

    days = sorted(
        {
            parse_date(
                item.get(
                    "record_date"
                )
            )
            for item in history
        },
        reverse=True,
    )

    if not days:
        return 0

    today_value = date.today()
    yesterday = (
        today_value
        - timedelta(days=1)
    )

    if days[0] not in [
        today_value,
        yesterday,
    ]:
        return 0

    streak = 1
    current = days[0]

    for day_value in days[1:]:
        expected = (
            current
            - timedelta(days=1)
        )

        if day_value == expected:
            streak += 1
            current = day_value

        elif day_value < expected:
            break

    return streak


# =========================================================
# マンネリ防止抽選
# =========================================================

def choose_challenge(
    challenges,
    history,
    exclude_id=None,
):
    active = [
        challenge
        for challenge in challenges
        if challenge.get(
            "active",
            True,
        )
        and challenge.get(
            "id"
        ) != exclude_id
    ]

    if not active:
        return None

    last_dates = {}
    counts = {}

    for item in history:
        challenge_id = item.get(
            "challenge_id",
            "",
        )

        counts[
            challenge_id
        ] = (
            counts.get(
                challenge_id,
                0,
            )
            + 1
        )

        record_date = parse_date(
            item.get(
                "record_date"
            )
        )

        if (
            challenge_id
            not in last_dates
            or record_date
            > last_dates[
                challenge_id
            ]
        ):
            last_dates[
                challenge_id
            ] = record_date

    weights = []

    for challenge in active:
        challenge_id = (
            challenge.get(
                "id",
                "",
            )
        )

        count = counts.get(
            challenge_id,
            0,
        )

        if count == 0:
            weight = 6

        else:
            last_date = last_dates.get(
                challenge_id,
                date.today(),
            )

            days_ago = (
                date.today()
                - last_date
            ).days

            if days_ago >= 30:
                weight = 5

            elif days_ago >= 14:
                weight = 4

            elif days_ago >= 7:
                weight = 3

            elif days_ago >= 3:
                weight = 2

            else:
                weight = 1

        if challenge.get(
            "favorite",
            False,
        ):
            weight += 1

        weights.append(
            weight
        )

    return random.choices(
        active,
        weights=weights,
        k=1,
    )[0]


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
            rgba(255, 130, 70, 0.07);
        border:
            1px solid
            rgba(255, 130, 70, 0.15);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 100, 80, 0.18),
                rgba(255, 200, 70, 0.08)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.8;
    }

    .challenge-box {
        padding: 30px;
        border-radius: 24px;
        margin-top: 15px;
        margin-bottom: 15px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 110, 70, 0.14),
                rgba(255, 210, 60, 0.08)
            );
    }

    .challenge-title {
        font-size: 2rem;
        font-weight: 800;
    }

    .complete-box {
        padding: 22px;
        border-radius: 20px;
        background:
            rgba(80, 200, 120, 0.10);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

challenges = data[
    "challenges"
]

history = data[
    "history"
]

today = date.today()

current_month = month_key(
    today
)

today_history = [
    item
    for item in history
    if item.get(
        "record_date"
    ) == str(today)
]

month_history = [
    item
    for item in history
    if item.get(
        "record_date",
        "",
    ).startswith(
        current_month
    )
]

active_challenges = [
    challenge
    for challenge in challenges
    if challenge.get(
        "active",
        True,
    )
]


# =========================================================
# Session State
# =========================================================

defaults = {
    "drawn_challenge_id": None,
    "doing_challenge_id": None,
    "show_complete": False,
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

        <h1>🚀 1日1チャレンジ</h1>

        <p>
            昨日と少し違うことを、
            ひとつだけ。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

streak = calculate_streak(
    history
)

first_max_count = len(
    [
        item
        for item in month_history
        if int(
            item.get(
                "first_level",
                1,
            )
        ) == 5
    ]
)

average_satisfaction = 0

if month_history:
    average_satisfaction = round(
        sum(
            int(
                item.get(
                    "satisfaction",
                    0,
                )
            )
            for item in month_history
        )
        / len(
            month_history
        ),
        1,
    )

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🚀 今月挑戦",
    f"{len(month_history)}回",
)

col2.metric(
    "🔥 連続挑戦",
    f"{streak}日",
)

col3.metric(
    "✨ 初めて度MAX",
    f"{first_max_count}回",
)

col4.metric(
    "😊 平均満足度",
    (
        f"{average_satisfaction}%"
        if month_history
        else "-"
    ),
)


# =========================================================
# 今日のチャレンジ
# =========================================================

st.divider()

st.subheader(
    "🎯 今日のチャレンジ"
)

if not active_challenges:
    st.info(
        "まずは下の「チャレンジ候補を追加」から"
        "小さな挑戦を登録してみよう！"
    )

else:
    if (
        st.session_state[
            "drawn_challenge_id"
        ] is None
        and st.session_state[
            "doing_challenge_id"
        ] is None
    ):
        if st.button(
            "🎲 今日のチャレンジを引く！",
            type="primary",
            use_container_width=True,
        ):
            selected = choose_challenge(
                challenges,
                history,
            )

            if selected:
                st.session_state[
                    "drawn_challenge_id"
                ] = selected.get(
                    "id"
                )

                st.rerun()


# =========================================================
# 抽選結果
# =========================================================

drawn_id = st.session_state[
    "drawn_challenge_id"
]

if drawn_id:
    challenge = get_challenge_by_id(
        data,
        drawn_id,
    )

    if challenge:
        st.markdown(
            f"""
            <div class="challenge-box">

                <div>
                    🚀 今日のチャレンジ
                </div>

                <div class="challenge-title">
                    {challenge.get("title", "")}
                </div>

                <br>

                <div>
                    {challenge.get("category", "")}
                </div>

                <div>
                    難易度
                    {stars(
                        challenge.get(
                            "difficulty",
                            1
                        )
                    )}
                </div>

                <div>
                    ⏱️
                    {time_text(
                        challenge.get(
                            "minutes",
                            10
                        )
                    )}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if challenge.get(
            "memo",
            "",
        ):
            st.caption(
                "💬 "
                + challenge.get(
                    "memo",
                    "",
                )
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🔥 挑戦する！",
                type="primary",
                use_container_width=True,
            ):
                st.session_state[
                    "doing_challenge_id"
                ] = drawn_id

                st.session_state[
                    "drawn_challenge_id"
                ] = None

                st.session_state[
                    "show_complete"
                ] = False

                st.rerun()

        with col2:
            if st.button(
                "🎲 別の挑戦",
                use_container_width=True,
            ):
                selected = choose_challenge(
                    challenges,
                    history,
                    exclude_id=drawn_id,
                )

                if selected:
                    st.session_state[
                        "drawn_challenge_id"
                    ] = selected.get(
                        "id"
                    )

                    st.rerun()

                else:
                    st.info(
                        "ほかの候補がありません。"
                    )


# =========================================================
# 挑戦中
# =========================================================

doing_id = st.session_state[
    "doing_challenge_id"
]

if doing_id:
    challenge = get_challenge_by_id(
        data,
        doing_id,
    )

    if challenge:
        st.divider()

        st.subheader(
            "🔥 今日の挑戦中"
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"## 🚀 "
                f"{challenge.get('title', '')}"
            )

            st.write(
                challenge.get(
                    "category",
                    "",
                )
            )

            st.caption(
                f"難易度 "
                f"{stars(challenge.get('difficulty', 1))}"
                f" ｜ ⏱️ "
                f"{time_text(challenge.get('minutes', 10))}"
            )

            st.info(
                "今日のどこかでできればOK！"
                "完璧に成功しなくても、"
                "挑戦したこと自体を記録できます。"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "🎉 結果を記録",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state[
                        "show_complete"
                    ] = True

            with col2:
                if st.button(
                    "↩️ 今回はやめる",
                    use_container_width=True,
                ):
                    st.session_state[
                        "doing_challenge_id"
                    ] = None

                    st.session_state[
                        "show_complete"
                    ] = False

                    st.rerun()


# =========================================================
# 結果記録
# =========================================================

if (
    doing_id
    and st.session_state[
        "show_complete"
    ]
):
    challenge = get_challenge_by_id(
        data,
        doing_id,
    )

    if challenge:
        st.markdown(
            """
            <div class="complete-box">

                <h2>🎉 Challenge Result!</h2>

                <strong>
                    やってみた時点で、
                    今日の挑戦は前進。
                </strong>

            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(
            "complete_form"
        ):
            result = st.radio(
                "結果",
                RESULTS,
            )

            satisfaction = st.slider(
                "😊 満足度",
                0,
                100,
                80,
            )

            first_level = st.slider(
                "✨ 初めて度",
                1,
                5,
                3,
            )

            st.caption(
                first_stars(
                    first_level
                )
            )

            comment = st.text_area(
                "💬 一言",
                placeholder=(
                    "やってみてどうだった？"
                ),
            )

            again = st.checkbox(
                "🔁 またやりたい",
                value=True,
            )

            completed = (
                st.form_submit_button(
                    "🏆 記録する",
                    type="primary",
                    use_container_width=True,
                )
            )

            if completed:
                add_history(
                    data,
                    challenge,
                    result,
                    satisfaction,
                    first_level,
                    comment.strip(),
                    again,
                )

                st.session_state[
                    "doing_challenge_id"
                ] = None

                st.session_state[
                    "show_complete"
                ] = False

                st.rerun()


# =========================================================
# 今日の結果
# =========================================================

if today_history:
    st.divider()

    st.subheader(
        "🎉 今日のチャレンジ"
    )

    for item in sorted(
        today_history,
        key=lambda value: (
            value.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{item.get('result', '')} "
                f"{item.get('title', '')}"
            )

            st.write(
                item.get(
                    "category",
                    "",
                )
            )

            st.caption(
                f"😊 満足度 "
                f"{item.get('satisfaction', 0)}%"
                f" ｜ "
                f"{first_stars(item.get('first_level', 1))}"
            )

            if item.get(
                "comment",
                "",
            ):
                st.write(
                    "💬 "
                    + item.get(
                        "comment",
                        "",
                    )
                )

    if streak >= 2:
        st.success(
            f"🔥 {streak}日連続チャレンジ！"
        )


# =========================================================
# チャレンジ候補追加
# =========================================================

st.divider()

st.subheader(
    "➕ チャレンジ候補を追加"
)

with st.expander(
    "🚀 新しいチャレンジ"
):
    with st.form(
        "new_challenge_form",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "チャレンジ",
            placeholder=(
                "例：いつもと違う道を歩く"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            difficulty = st.slider(
                "難易度",
                1,
                5,
                1,
            )

        with col2:
            minutes = st.number_input(
                "所要時間（分）",
                min_value=1,
                max_value=1440,
                value=10,
                step=5,
            )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "ルールや補足があれば"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🚀 候補に追加",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "チャレンジを入力してね。"
                )

            else:
                add_challenge(
                    data,
                    title.strip(),
                    category,
                    difficulty,
                    minutes,
                    memo.strip(),
                )

                st.rerun()


# =========================================================
# チャレンジ図鑑
# =========================================================

if history:
    st.divider()

    st.subheader(
        "📖 チャレンジ図鑑"
    )

    encyclopedia = {}

    for item in history:
        challenge_id = item.get(
            "challenge_id",
            "",
        )

        key = (
            challenge_id
            if challenge_id
            else item.get(
                "title",
                "",
            )
        )

        if key not in encyclopedia:
            encyclopedia[key] = {
                "title": item.get(
                    "title",
                    "",
                ),
                "category": item.get(
                    "category",
                    "",
                ),
                "count": 0,
                "satisfaction_total": 0,
                "max_first": 0,
            }

        encyclopedia[
            key
        ]["count"] += 1

        encyclopedia[
            key
        ]["satisfaction_total"] += int(
            item.get(
                "satisfaction",
                0,
            )
        )

        encyclopedia[
            key
        ]["max_first"] = max(
            encyclopedia[
                key
            ]["max_first"],
            int(
                item.get(
                    "first_level",
                    1,
                )
            ),
        )

    encyclopedia_rows = []

    for value in encyclopedia.values():
        average = round(
            value[
                "satisfaction_total"
            ]
            / value[
                "count"
            ],
            1,
        )

        encyclopedia_rows.append(
            {
                "チャレンジ": value[
                    "title"
                ],
                "カテゴリー": value[
                    "category"
                ],
                "挑戦回数": value[
                    "count"
                ],
                "平均満足度": (
                    f"{average}%"
                ),
                "最大初めて度": (
                    first_stars(
                        value[
                            "max_first"
                        ]
                    )
                ),
            }
        )

    encyclopedia_df = pd.DataFrame(
        encyclopedia_rows
    )

    st.dataframe(
        encyclopedia_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# カテゴリー分析
# =========================================================

if history:
    st.divider()

    st.subheader(
        "📊 どんな挑戦をしてる？"
    )

    category_df = pd.DataFrame(
        [
            {
                "カテゴリー": item.get(
                    "category",
                    "✨ その他",
                )
            }
            for item in history
        ]
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
            name="挑戦回数"
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

if history:
    st.divider()

    st.subheader(
        "📈 月別チャレンジ"
    )

    monthly_rows = []

    for item in history:
        record_date = item.get(
            "record_date",
            "",
        )

        if len(
            record_date
        ) >= 7:
            monthly_rows.append(
                {
                    "月": (
                        record_date[:7]
                    )
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
                name="挑戦回数"
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
# 候補一覧
# =========================================================

st.divider()

st.subheader(
    "🎯 チャレンジ候補"
)

search_text = st.text_input(
    "🔎 候補を検索",
    placeholder=(
        "チャレンジ・メモから検索"
    ),
)

category_filter = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="candidate_category",
)

filtered_challenges = []

for challenge in challenges:
    if (
        category_filter
        != "すべて"
        and challenge.get(
            "category"
        )
        != category_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                challenge.get(
                    "title",
                    "",
                ),
                challenge.get(
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

    filtered_challenges.append(
        challenge
    )


filtered_challenges = sorted(
    filtered_challenges,
    key=lambda item: (
        not item.get(
            "active",
            True,
        ),
        not item.get(
            "favorite",
            False,
        ),
        item.get(
            "title",
            "",
        ),
    ),
)


if not filtered_challenges:
    st.info(
        "条件に合う候補はありません。"
    )

else:
    for challenge in filtered_challenges:
        challenge_id = challenge.get(
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
                    f"### 🚀 "
                    f"{challenge.get('title', '')}"
                )

            with col2:
                icon = (
                    "⭐"
                    if challenge.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    icon,
                    key=(
                        "fav_"
                        + challenge_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        challenge_id,
                    )

                    st.rerun()

            st.write(
                challenge.get(
                    "category",
                    "",
                )
            )

            st.caption(
                f"難易度 "
                f"{stars(challenge.get('difficulty', 1))}"
                f" ｜ ⏱️ "
                f"{time_text(challenge.get('minutes', 10))}"
            )

            if not challenge.get(
                "active",
                True,
            ):
                st.caption(
                    "⏸️ 現在は抽選対象外"
                )

            if challenge.get(
                "memo",
                "",
            ):
                st.write(
                    challenge.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 候補を編集・削除"
):
    if not challenges:
        st.caption(
            "まだ候補がありません。"
        )

    for challenge in challenges:
        challenge_id = challenge.get(
            "id",
            "",
        )

        with st.expander(
            challenge.get(
                "title",
                "",
            )
        ):
            edit_title = st.text_input(
                "チャレンジ",
                value=challenge.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + challenge_id
                ),
            )

            current_category = (
                challenge.get(
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

            edit_category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=category_index,
                key=(
                    "edit_category_"
                    + challenge_id
                ),
            )

            edit_difficulty = st.slider(
                "難易度",
                1,
                5,
                int(
                    challenge.get(
                        "difficulty",
                        1,
                    )
                ),
                key=(
                    "edit_difficulty_"
                    + challenge_id
                ),
            )

            edit_minutes = st.number_input(
                "所要時間（分）",
                min_value=1,
                max_value=1440,
                value=int(
                    challenge.get(
                        "minutes",
                        10,
                    )
                ),
                key=(
                    "edit_minutes_"
                    + challenge_id
                ),
            )

            edit_memo = st.text_area(
                "メモ",
                value=challenge.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + challenge_id
                ),
            )

            edit_active = st.checkbox(
                "🎲 抽選対象にする",
                value=challenge.get(
                    "active",
                    True,
                ),
                key=(
                    "edit_active_"
                    + challenge_id
                ),
            )

            edit_favorite = st.checkbox(
                "⭐ お気に入り",
                value=challenge.get(
                    "favorite",
                    False,
                ),
                key=(
                    "edit_favorite_"
                    + challenge_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + challenge_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.warning(
                            "チャレンジ名を入力してね。"
                        )

                    else:
                        update_challenge(
                            data,
                            challenge_id,
                            edit_title.strip(),
                            edit_category,
                            edit_difficulty,
                            edit_minutes,
                            edit_memo.strip(),
                            edit_active,
                            edit_favorite,
                        )

                        st.rerun()

            with col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_"
                        + challenge_id
                    ),
                    use_container_width=True,
                ):
                    delete_challenge(
                        data,
                        challenge_id,
                    )

                    if (
                        st.session_state[
                            "drawn_challenge_id"
                        ]
                        == challenge_id
                    ):
                        st.session_state[
                            "drawn_challenge_id"
                        ] = None

                    if (
                        st.session_state[
                            "doing_challenge_id"
                        ]
                        == challenge_id
                    ):
                        st.session_state[
                            "doing_challenge_id"
                        ] = None

                    st.rerun()


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 チャレンジ履歴"
)

if not history:
    st.info(
        "まだチャレンジ履歴がありません。"
    )

else:
    history_rows = []

    for item in sorted(
        history,
        key=lambda value: (
            value.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        history_rows.append(
            {
                "日付": item.get(
                    "record_date",
                    "",
                ),
                "チャレンジ": item.get(
                    "title",
                    "",
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "結果": item.get(
                    "result",
                    "",
                ),
                "満足度": (
                    f"{item.get('satisfaction', 0)}%"
                ),
                "初めて度": (
                    first_stars(
                        item.get(
                            "first_level",
                            1,
                        )
                    )
                ),
                "またやりたい": (
                    "🔁"
                    if item.get(
                        "again",
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
# 履歴削除
# =========================================================

with st.expander(
    "🗑️ 履歴を削除"
):
    if not history:
        st.caption(
            "削除できる履歴はありません。"
        )

    else:
        history_sorted = sorted(
            history,
            key=lambda value: (
                value.get(
                    "created_at",
                    "",
                )
            ),
            reverse=True,
        )

        delete_options = {
            (
                f"{item.get('record_date', '')}"
                f" ｜ "
                f"{item.get('title', '')}"
                f" ｜ "
                f"{item.get('result', '')}"
            ): item.get(
                "id"
            )
            for item in history_sorted
        }

        selected_history = st.selectbox(
            "削除する履歴",
            list(
                delete_options.keys()
            ),
        )

        if st.button(
            "🗑️ この履歴を削除",
            use_container_width=True,
        ):
            delete_history(
                data,
                delete_options[
                    selected_history
                ],
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
            "one_day_challenge_"
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
    "昨日と少し違うことを、"
    "ひとつだけ。🚀✨"
)
