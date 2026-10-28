import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="未来の楽しみリスト",
    page_icon="🎁",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "joys.json",
)

CATEGORIES = [
    "✈️ 旅行",
    "🎮 趣味",
    "🍴 食事",
    "🛍️ 買い物",
    "🎬 エンタメ",
    "👨‍👩‍👧 家族",
    "👫 人と会う",
    "🏠 暮らし",
    "💼 仕事",
    "🚀 挑戦",
    "🎁 その他",
]

STATUS_WAITING = "🌈 楽しみにしてる"
STATUS_MEMORY = "📸 思い出になった"
STATUS_CANCELLED = "🫧 今回はやめた"

STATUSES = [
    STATUS_WAITING,
    STATUS_MEMORY,
    STATUS_CANCELLED,
]

REPEAT_OPTIONS = [
    "◎ またやりたい",
    "△ どちらでも",
    "× もういいかな",
]


# =========================================================
# HELPERS
# =========================================================

def new_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return None


def format_date(value):
    d = parse_date(value)

    if not d:
        return "未定"

    return d.strftime("%Y/%m/%d")


def stars(value):
    if value is None:
        return "-"

    try:
        value = int(value)
    except (ValueError, TypeError):
        return "-"

    value = max(
        0,
        min(value, 5),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def days_until(joy):
    event_date = parse_date(
        joy.get("event_date")
    )

    if not event_date:
        return None

    return (
        event_date
        - date.today()
    ).days


def waiting_days(joy):
    created_at = joy.get(
        "created_at"
    )

    event_date = parse_date(
        joy.get("event_date")
    )

    if (
        not created_at
        or not event_date
    ):
        return None

    try:
        created_date = (
            datetime.fromisoformat(
                created_at
            ).date()
        )
    except (
        ValueError,
        TypeError,
    ):
        return None

    return max(
        0,
        (
            event_date
            - created_date
        ).days,
    )


def joy_label(joy):
    return (
        f"{joy.get('title', '')}"
        f" [{joy.get('id', '')[:6]}]"
    )


def status_display(joy):
    if (
        joy.get("status")
        == STATUS_WAITING
    ):
        days = days_until(joy)

        if days == 0:
            return "🎉 今日！"

    return joy.get(
        "status",
        STATUS_WAITING,
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "joys": [],
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    temp_file = (
        DATA_FILE + ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temp_file,
        DATA_FILE,
    )


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(
            data,
            dict,
        ):
            data = default_data()

        data.setdefault(
            "joys",
            [],
        )

        for joy in data["joys"]:
            joy.setdefault(
                "id",
                new_id(),
            )

            joy.setdefault(
                "title",
                "",
            )

            joy.setdefault(
                "category",
                "🎁 その他",
            )

            joy.setdefault(
                "event_date",
                None,
            )

            joy.setdefault(
                "date_unknown",
                (
                    joy.get(
                        "event_date"
                    )
                    is None
                ),
            )

            joy.setdefault(
                "expectation",
                3,
            )

            joy.setdefault(
                "before_note",
                "",
            )

            joy.setdefault(
                "status",
                STATUS_WAITING,
            )

            joy.setdefault(
                "actual_rating",
                None,
            )

            joy.setdefault(
                "after_note",
                "",
            )

            joy.setdefault(
                "repeat",
                None,
            )

            joy.setdefault(
                "favorite",
                False,
            )

            joy.setdefault(
                "created_at",
                now_text(),
            )

            joy.setdefault(
                "completed_at",
                None,
            )

            joy.setdefault(
                "updated_at",
                joy.get(
                    "created_at",
                    now_text(),
                ),
            )

        return data

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS
# =========================================================

def get_joy(
    data,
    joy_id,
):
    return next(
        (
            joy
            for joy
            in data["joys"]
            if joy.get("id")
            == joy_id
        ),
        None,
    )


def waiting_joys(data):
    return [
        joy
        for joy
        in data["joys"]
        if joy.get("status")
        == STATUS_WAITING
    ]


def memory_joys(data):
    return [
        joy
        for joy
        in data["joys"]
        if joy.get("status")
        == STATUS_MEMORY
    ]


# =========================================================
# CRUD
# =========================================================

def add_joy(
    data,
    title,
    category,
    event_date,
    date_unknown,
    expectation,
    before_note,
    favorite=False,
):
    joy = {
        "id": new_id(),
        "title": title,
        "category": category,
        "event_date": (
            None
            if date_unknown
            else str(event_date)
        ),
        "date_unknown": (
            date_unknown
        ),
        "expectation": int(
            expectation
        ),
        "before_note": (
            before_note
        ),
        "status": (
            STATUS_WAITING
        ),
        "actual_rating": None,
        "after_note": "",
        "repeat": None,
        "favorite": favorite,
        "created_at": now_text(),
        "completed_at": None,
        "updated_at": now_text(),
    }

    data["joys"].append(
        joy
    )

    save_data(data)


def complete_joy(
    data,
    joy_id,
    actual_rating,
    after_note,
    repeat,
):
    joy = get_joy(
        data,
        joy_id,
    )

    if not joy:
        return

    joy["status"] = (
        STATUS_MEMORY
    )

    joy[
        "actual_rating"
    ] = int(actual_rating)

    joy[
        "after_note"
    ] = after_note

    joy["repeat"] = repeat

    joy[
        "completed_at"
    ] = now_text()

    joy[
        "updated_at"
    ] = now_text()

    save_data(data)


def cancel_joy(
    data,
    joy_id,
):
    joy = get_joy(
        data,
        joy_id,
    )

    if not joy:
        return

    joy["status"] = (
        STATUS_CANCELLED
    )

    joy[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    joy_id,
):
    joy = get_joy(
        data,
        joy_id,
    )

    if not joy:
        return

    joy[
        "favorite"
    ] = not joy.get(
        "favorite",
        False,
    )

    joy[
        "updated_at"
    ] = now_text()

    save_data(data)


def repeat_as_future(
    data,
    joy,
):
    new_joy = {
        "id": new_id(),
        "title": joy.get(
            "title",
            "",
        ),
        "category": joy.get(
            "category",
            "🎁 その他",
        ),
        "event_date": None,
        "date_unknown": True,
        "expectation": (
            joy.get(
                "actual_rating"
            )
            or joy.get(
                "expectation",
                3,
            )
        ),
        "before_note": (
            "もう一度やりたい 🌈"
        ),
        "status": (
            STATUS_WAITING
        ),
        "actual_rating": None,
        "after_note": "",
        "repeat": None,
        "favorite": False,
        "created_at": now_text(),
        "completed_at": None,
        "updated_at": now_text(),
    }

    data["joys"].append(
        new_joy
    )

    save_data(data)


def delete_joy(
    data,
    joy_id,
):
    data["joys"] = [
        joy
        for joy
        in data["joys"]
        if joy.get("id")
        != joy_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero {
        text-align: center;
        padding: 40px 25px;
        margin-bottom: 25px;
        border-radius: 28px;
        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 80, .13),
                rgba(120, 180, 255, .12),
                rgba(230, 140, 220, .08)
            );
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(120, 180, 255, .05);
        border:
            1px solid
            rgba(120, 180, 255, .14);
    }

    .next-joy {
        text-align: center;
        padding: 30px;
        border-radius: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 80, .10),
                rgba(220, 130, 210, .08)
            );
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        padding: 30px;
        border-radius: 25px;
        margin-top: 30px;
        background:
            rgba(120, 180, 255, .05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()

joys = data["joys"]

today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>🎁 DAY 304 / 365</div>
        <h1>未来の楽しみリスト</h1>
        <p>
            「やらなきゃ」ではなく、
            これから待っている楽しみを集めよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

(
    tab_home,
    tab_add,
    tab_memory,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🌈 未来",
        "➕ 楽しみ追加",
        "📸 思い出",
        "📊 分析",
        "📚 楽しみ図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    future_joys = (
        waiting_joys(data)
    )

    dated_future = [
        joy
        for joy in future_joys
        if parse_date(
            joy.get(
                "event_date"
            )
        )
        is not None
    ]

    unknown_future = [
        joy
        for joy in future_joys
        if joy.get(
            "date_unknown"
        )
        or not joy.get(
            "event_date"
        )
    ]

    dated_future.sort(
        key=lambda joy: (
            joy.get(
                "event_date",
                ""
            )
        )
    )

    # -----------------------------------------------------
    # BALANCE
    # -----------------------------------------------------

    st.subheader(
        "🌈 楽しみ残高"
    )

    this_month = 0
    next_month = 0
    later = 0

    if today.month == 12:
        next_year = (
            today.year + 1
        )
        next_month_number = 1
    else:
        next_year = today.year
        next_month_number = (
            today.month + 1
        )

    for joy in dated_future:
        d = parse_date(
            joy.get(
                "event_date"
            )
        )

        if not d:
            continue

        if (
            d.year == today.year
            and d.month
            == today.month
            and d >= today
        ):
            this_month += 1

        elif (
            d.year == next_year
            and d.month
            == next_month_number
        ):
            next_month += 1

        elif d > today:
            later += 1

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "🌈 待っている楽しみ",
        f"{len(future_joys)}個",
    )

    c2.metric(
        "📅 今月",
        f"{this_month}個",
    )

    c3.metric(
        "➡️ 来月",
        f"{next_month}個",
    )

    c4.metric(
        "✨ いつか",
        f"{len(unknown_future)}個",
    )

    if future_joys:
        st.success(
            f"🌈 あなたの未来には "
            f"**{len(future_joys)}個** "
            "楽しみが待っています。"
        )

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    todays_joys = [
        joy
        for joy in dated_future
        if parse_date(
            joy.get(
                "event_date"
            )
        ) == today
    ]

    if todays_joys:
        st.divider()

        st.subheader(
            "🎉 今日だ！"
        )

        for joy in todays_joys:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### 🎉 "
                    f"{joy.get('title')}"
                )

                st.write(
                    joy.get(
                        "category"
                    )
                )

                st.write(
                    "楽しみ度 "
                    + stars(
                        joy.get(
                            "expectation"
                        )
                    )
                )

                if joy.get(
                    "before_note"
                ):
                    st.info(
                        joy.get(
                            "before_note"
                        )
                    )

                st.success(
                    "今日はその日！"
                    "楽しんできて！ 🌈"
                )

    # -----------------------------------------------------
    # OVERDUE
    # -----------------------------------------------------

    overdue = [
        joy
        for joy in dated_future
        if (
            parse_date(
                joy.get(
                    "event_date"
                )
            )
            and parse_date(
                joy.get(
                    "event_date"
                )
            ) < today
        )
    ]

    if overdue:
        st.divider()

        st.subheader(
            "🌤️ 楽しみにしてたこれ、どうだった？"
        )

        for joy in overdue[:5]:
            days_ago = abs(
                days_until(joy)
            )

            with st.container(
                border=True
            ):
                st.write(
                    f"**{joy.get('title')}**"
                )

                st.caption(
                    f"{days_ago}日前の予定"
                    f" ｜ "
                    f"{joy.get('category')}"
                )

                st.write(
                    "期待 "
                    + stars(
                        joy.get(
                            "expectation"
                        )
                    )
                )

    # -----------------------------------------------------
    # NEXT
    # -----------------------------------------------------

    future_only = [
        joy
        for joy in dated_future
        if (
            parse_date(
                joy.get(
                    "event_date"
                )
            )
            and parse_date(
                joy.get(
                    "event_date"
                )
            ) >= today
        )
    ]

    if future_only:
        st.divider()

        st.subheader(
            "🎁 次の楽しみ"
        )

        next_joy = (
            future_only[0]
        )

        days = days_until(
            next_joy
        )

        if days == 0:
            countdown = (
                "🎉 今日！"
            )
        elif days == 1:
            countdown = (
                "明日！"
            )
        else:
            countdown = (
                f"あと{days}日"
            )

        st.markdown(
            f"""
            <div class="next-joy">
                <div>
                    {next_joy.get("category")}
                </div>
                <h2>
                    {next_joy.get("title")}
                </h2>
                <h3>
                    {countdown}
                </h3>
                <p>
                    楽しみ度
                    {stars(next_joy.get("expectation"))}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for joy in future_only[
            1:6
        ]:
            days = days_until(joy)

            with st.container(
                border=True
            ):
                st.write(
                    f"**{joy.get('category')} "
                    f"{joy.get('title')}**"
                )

                st.caption(
                    f"{format_date(joy.get('event_date'))}"
                    f" ｜ あと{days}日"
                    f" ｜ "
                    f"{stars(joy.get('expectation'))}"
                )

    # -----------------------------------------------------
    # SOMEDAY
    # -----------------------------------------------------

    if unknown_future:
        st.divider()

        st.subheader(
            "✨ いつかやりたい"
        )

        for joy in (
            unknown_future[:8]
        ):
            with st.container(
                border=True
            ):
                st.write(
                    f"**{joy.get('category')} "
                    f"{joy.get('title')}**"
                )

                st.caption(
                    "日付はまだ未定"
                    f" ｜ "
                    f"{stars(joy.get('expectation'))}"
                )


# =========================================================
# ADD
# =========================================================

with tab_add:

    st.subheader(
        "➕ 未来に楽しみを置く"
    )

    with st.form(
        "add_joy",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "🎁 何を楽しみにしてる？",
            placeholder=(
                "例：新しい街を探索する"
            ),
        )

        category = (
            st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )
        )

        date_unknown = (
            st.checkbox(
                "📅 日付はまだ決まっていない"
            )
        )

        event_date = (
            st.date_input(
                "いつ？",
                value=today,
                min_value=today,
                disabled=date_unknown,
            )
        )

        expectation = (
            st.slider(
                "楽しみ度",
                1,
                5,
                4,
            )
        )

        before_note = (
            st.text_area(
                "ひとこと",
                placeholder=(
                    "どんな店があるか"
                    "歩いてみたい"
                ),
            )
        )

        favorite = st.checkbox(
            "⭐ 特別な楽しみ"
        )

        if st.form_submit_button(
            "🌈 楽しみを追加",
            type="primary",
            use_container_width=True,
        ):
            if not title.strip():
                st.warning(
                    "楽しみを入力してね。"
                )

            else:
                add_joy(
                    data=data,
                    title=title.strip(),
                    category=category,
                    event_date=event_date,
                    date_unknown=(
                        date_unknown
                    ),
                    expectation=(
                        expectation
                    ),
                    before_note=(
                        before_note.strip()
                    ),
                    favorite=favorite,
                )

                st.rerun()

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "📸 楽しみを思い出にする"
    )

    future_joys = (
        waiting_joys(data)
    )

    if not future_joys:
        st.caption(
            "振り返る楽しみは"
            "まだありません。"
        )

    else:
        options = {
            joy_label(joy):
            joy.get("id")
            for joy in future_joys
        }

        selected_label = (
            st.selectbox(
                "どの楽しみ？",
                list(
                    options.keys()
                ),
                key="complete_select",
            )
        )

        selected_id = (
            options[
                selected_label
            ]
        )

        selected = get_joy(
            data,
            selected_id,
        )

        st.write(
            f"**期待：** "
            f"{stars(selected.get('expectation'))}"
        )

        with st.form(
            "complete_joy"
        ):
            actual_rating = (
                st.slider(
                    "実際どうだった？",
                    1,
                    5,
                    4,
                )
            )

            after_note = (
                st.text_area(
                    "思い出・感想",
                    placeholder=(
                        "めちゃくちゃ"
                        "楽しかった！"
                    ),
                )
            )

            repeat = st.radio(
                "またやりたい？",
                REPEAT_OPTIONS,
            )

            if st.form_submit_button(
                "📸 思い出にする",
                type="primary",
                use_container_width=True,
            ):
                complete_joy(
                    data=data,
                    joy_id=selected_id,
                    actual_rating=(
                        actual_rating
                    ),
                    after_note=(
                        after_note.strip()
                    ),
                    repeat=repeat,
                )

                st.rerun()


# =========================================================
# MEMORIES
# =========================================================

with tab_memory:

    st.subheader(
        "📸 楽しみだった日々"
    )

    memories = (
        memory_joys(data)
    )

    memories.sort(
        key=lambda joy: (
            joy.get(
                "completed_at",
                ""
            )
        ),
        reverse=True,
    )

    if not memories:
        st.info(
            "未来の楽しみを体験したら、"
            "ここに思い出が増えていきます。"
        )

    else:
        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        ratings = [
            int(
                joy.get(
                    "actual_rating"
                )
            )
            for joy in memories
            if joy.get(
                "actual_rating"
            )
            is not None
        ]

        repeat_count = sum(
            1
            for joy in memories
            if joy.get(
                "repeat"
            )
            == "◎ またやりたい"
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        c1.metric(
            "📸 思い出",
            f"{len(memories)}個",
        )

        c2.metric(
            "⭐ 平均満足度",
            (
                f"{sum(ratings) / len(ratings):.1f}/5"
                if ratings
                else "-"
            ),
        )

        c3.metric(
            "💖 またやりたい",
            f"{repeat_count}個",
        )

        # -------------------------------------------------
        # CARDS
        # -------------------------------------------------

        for joy in memories:
            with st.container(
                border=True
            ):
                col1, col2 = (
                    st.columns(
                        [8, 1]
                    )
                )

                with col1:
                    st.markdown(
                        f"### "
                        f"{joy.get('category')} "
                        f"{joy.get('title')}"
                    )

                    st.write(
                        f"期待 "
                        f"{stars(joy.get('expectation'))}"
                        f" → 実際 "
                        f"{stars(joy.get('actual_rating'))}"
                    )

                    st.write(
                        joy.get(
                            "repeat",
                            "-"
                        )
                    )

                    if joy.get(
                        "after_note"
                    ):
                        st.info(
                            joy.get(
                                "after_note"
                            )
                        )

                with col2:
                    if st.button(
                        (
                            "⭐"
                            if joy.get(
                                "favorite",
                                False,
                            )
                            else "☆"
                        ),
                        key=(
                            "memory_fav_"
                            + joy.get(
                                "id"
                            )
                        ),
                    ):
                        toggle_favorite(
                            data,
                            joy.get(
                                "id"
                            ),
                        )

                        st.rerun()

                if (
                    joy.get("repeat")
                    == "◎ またやりたい"
                ):
                    if st.button(
                        "🎁 もう一度、未来の楽しみに入れる",
                        key=(
                            "repeat_"
                            + joy.get(
                                "id"
                            )
                        ),
                        use_container_width=True,
                    ):
                        repeat_as_future(
                            data,
                            joy,
                        )

                        st.rerun()

        # -------------------------------------------------
        # RANDOM REDISCOVERY
        # -------------------------------------------------

        repeatable = [
            joy
            for joy in memories
            if joy.get(
                "repeat"
            )
            == "◎ またやりたい"
        ]

        if repeatable:
            st.divider()

            st.subheader(
                "🎲 これ、またどう？"
            )

            ids = [
                joy.get("id")
                for joy in repeatable
            ]

            random_id = (
                st.session_state.get(
                    "random_memory"
                )
            )

            if random_id not in ids:
                random_id = (
                    random.choice(
                        ids
                    )
                )

                st.session_state[
                    "random_memory"
                ] = random_id

            random_joy = get_joy(
                data,
                random_id,
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### "
                    f"{random_joy.get('category')} "
                    f"{random_joy.get('title')}"
                )

                st.write(
                    "満足度 "
                    + stars(
                        random_joy.get(
                            "actual_rating"
                        )
                    )
                )

                if random_joy.get(
                    "after_note"
                ):
                    st.write(
                        "💭 "
                        + random_joy.get(
                            "after_note"
                        )
                    )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "🎲 別の思い出",
                    use_container_width=True,
                ):
                    alternatives = [
                        joy_id
                        for joy_id
                        in ids
                        if joy_id
                        != random_id
                    ]

                    if alternatives:
                        st.session_state[
                            "random_memory"
                        ] = (
                            random.choice(
                                alternatives
                            )
                        )

                    st.rerun()

            with col2:
                if st.button(
                    "🌈 また楽しみに追加",
                    use_container_width=True,
                ):
                    repeat_as_future(
                        data,
                        random_joy,
                    )

                    st.rerun()


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 楽しみ分析"
    )

    if not joys:
        st.info(
            "楽しみを登録すると"
            "分析が始まります。"
        )

    else:
        memories = (
            memory_joys(data)
        )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        st.markdown(
            "### 🌈 何を楽しみにしてる？"
        )

        category_counter = (
            Counter(
                joy.get(
                    "category"
                )
                for joy in joys
            )
        )

        category_df = (
            pd.DataFrame(
                [
                    {
                        "カテゴリー": (
                            category
                        ),
                        "件数": count,
                    }
                    for category, count
                    in category_counter
                    .most_common()
                ]
            )
            .set_index(
                "カテゴリー"
            )
        )

        st.bar_chart(
            category_df
        )

        # -------------------------------------------------
        # CATEGORY SATISFACTION
        # -------------------------------------------------

        if memories:
            st.divider()

            st.markdown(
                "### ⭐ カテゴリー別満足度"
            )

            category_ratings = (
                defaultdict(list)
            )

            for joy in memories:
                rating = joy.get(
                    "actual_rating"
                )

                if rating is not None:
                    category_ratings[
                        joy.get(
                            "category"
                        )
                    ].append(
                        int(rating)
                    )

            rating_rows = []

            for category, values in (
                category_ratings.items()
            ):
                rating_rows.append(
                    {
                        "カテゴリー": (
                            category
                        ),
                        "平均満足度": (
                            sum(values)
                            / len(values)
                        ),
                        "体験数": (
                            len(values)
                        ),
                    }
                )

            if rating_rows:
                rating_df = (
                    pd.DataFrame(
                        rating_rows
                    )
                    .sort_values(
                        "平均満足度",
                        ascending=False,
                    )
                )

                st.dataframe(
                    rating_df,
                    hide_index=True,
                    use_container_width=True,
                )

        # -------------------------------------------------
        # EXPECTATION VS ACTUAL
        # -------------------------------------------------

        if memories:
            st.divider()

            st.markdown(
                "### 😲 期待以上だった！"
            )

            differences = []

            for joy in memories:
                actual = joy.get(
                    "actual_rating"
                )

                if actual is None:
                    continue

                diff = (
                    int(actual)
                    - int(
                        joy.get(
                            "expectation",
                            3,
                        )
                    )
                )

                differences.append(
                    (
                        diff,
                        joy,
                    )
                )

            differences.sort(
                key=lambda row: (
                    row[0]
                ),
                reverse=True,
            )

            positive = [
                row
                for row
                in differences
                if row[0] > 0
            ]

            if not positive:
                st.caption(
                    "期待を超えた記録は"
                    "まだありません。"
                )

            else:
                for index, (
                    diff,
                    joy,
                ) in enumerate(
                    positive[:10],
                    start=1,
                ):
                    st.write(
                        f"**{index}. "
                        f"{joy.get('title')}**"
                    )

                    st.caption(
                        f"期待 "
                        f"{stars(joy.get('expectation'))}"
                        f" → 実際 "
                        f"{stars(joy.get('actual_rating'))}"
                        f" ｜ +{diff}"
                    )

        # -------------------------------------------------
        # LONGEST ANTICIPATION
        # -------------------------------------------------

        waitable = []

        for joy in joys:
            days = waiting_days(
                joy
            )

            if days is not None:
                waitable.append(
                    (
                        days,
                        joy,
                    )
                )

        if waitable:
            st.divider()

            st.markdown(
                "### 🗓️ 長く楽しみにしていた"
            )

            waitable.sort(
                key=lambda row: (
                    row[0]
                ),
                reverse=True,
            )

            for index, (
                days,
                joy,
            ) in enumerate(
                waitable[:10],
                start=1,
            ):
                st.write(
                    f"**{index}. "
                    f"{joy.get('title')}** "
                    f"— {days}日前から"
                )

        # -------------------------------------------------
        # MONTHLY
        # -------------------------------------------------

        dated = []

        for joy in joys:
            d = parse_date(
                joy.get(
                    "event_date"
                )
            )

            if d:
                dated.append(
                    {
                        "月": (
                            d.strftime(
                                "%Y-%m"
                            )
                        ),
                        "件数": 1,
                    }
                )

        if dated:
            st.divider()

            st.markdown(
                "### 📅 月別の楽しみ"
            )

            monthly_df = (
                pd.DataFrame(
                    dated
                )
                .groupby(
                    "月",
                    as_index=True,
                )["件数"]
                .sum()
            )

            st.bar_chart(
                monthly_df
            )


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 楽しみ図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        category_filter = (
            st.selectbox(
                "カテゴリー",
                ["すべて"]
                + CATEGORIES,
                key=(
                    "library_category"
                ),
            )
        )

    with col2:
        status_filter = (
            st.selectbox(
                "状態",
                [
                    "すべて",
                    STATUS_WAITING,
                    "🎉 今日！",
                    STATUS_MEMORY,
                    STATUS_CANCELLED,
                ],
                key=(
                    "library_status"
                ),
            )
        )

    minimum_rating = (
        st.select_slider(
            "最低楽しみ度",
            options=[
                1,
                2,
                3,
                4,
                5,
            ],
            value=1,
        )
    )

    favorite_only = (
        st.checkbox(
            "⭐ お気に入りだけ"
        )
    )

    rows = []

    for joy in joys:
        display_status = (
            status_display(joy)
        )

        if (
            category_filter
            != "すべて"
            and joy.get(
                "category"
            )
            != category_filter
        ):
            continue

        if (
            status_filter
            != "すべて"
            and display_status
            != status_filter
        ):
            continue

        if (
            int(
                joy.get(
                    "expectation",
                    1,
                )
            )
            < minimum_rating
        ):
            continue

        if (
            favorite_only
            and not joy.get(
                "favorite",
                False,
            )
        ):
            continue

        searchable = " ".join(
            [
                joy.get(
                    "title",
                    "",
                ),
                joy.get(
                    "category",
                    "",
                ),
                joy.get(
                    "before_note",
                    "",
                ),
                joy.get(
                    "after_note",
                    "",
                ),
            ]
        ).lower()

        if (
            search.strip()
            and search
            .strip()
            .lower()
            not in searchable
        ):
            continue

        days = days_until(
            joy
        )

        if (
            joy.get("status")
            == STATUS_WAITING
            and days is not None
            and days >= 0
        ):
            countdown = (
                "今日"
                if days == 0
                else f"{days}日"
            )
        else:
            countdown = "-"

        rows.append(
            {
                "楽しみ": (
                    joy.get("title")
                ),
                "カテゴリー": (
                    joy.get(
                        "category"
                    )
                ),
                "日付": (
                    format_date(
                        joy.get(
                            "event_date"
                        )
                    )
                ),
                "あと": (
                    countdown
                ),
                "期待": (
                    stars(
                        joy.get(
                            "expectation"
                        )
                    )
                ),
                "状態": (
                    display_status
                ),
                "実際": (
                    stars(
                        joy.get(
                            "actual_rating"
                        )
                    )
                ),
                "⭐": (
                    "⭐"
                    if joy.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    if rows:
        st.dataframe(
            pd.DataFrame(
                rows
            ),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "条件に合う楽しみは"
            "ありません。"
        )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 楽しみを編集"
    )

    if not joys:
        st.info(
            "まだ楽しみがありません。"
        )

    else:
        options = {
            joy_label(joy):
            joy.get("id")
            for joy in joys
        }

        selected_label = (
            st.selectbox(
                "編集する楽しみ",
                list(
                    options.keys()
                ),
                key="manage_select",
            )
        )

        selected_id = (
            options[
                selected_label
            ]
        )

        joy = get_joy(
            data,
            selected_id,
        )

        edit_title = (
            st.text_input(
                "楽しみ",
                value=joy.get(
                    "title",
                    "",
                ),
            )
        )

        old_category = joy.get(
            "category",
            "🎁 その他",
        )

        category_index = (
            CATEGORIES.index(
                old_category
            )
            if old_category
            in CATEGORIES
            else len(
                CATEGORIES
            ) - 1
        )

        edit_category = (
            st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=(
                    category_index
                ),
                key=(
                    "manage_category"
                ),
            )
        )

        edit_unknown = (
            st.checkbox(
                "日付未定",
                value=joy.get(
                    "date_unknown",
                    False,
                ),
            )
        )

        current_date = (
            parse_date(
                joy.get(
                    "event_date"
                )
            )
            or today
        )

        edit_event_date = (
            st.date_input(
                "日付",
                value=current_date,
                disabled=(
                    edit_unknown
                ),
                key=(
                    "manage_date"
                ),
            )
        )

        edit_expectation = (
            st.slider(
                "楽しみ度",
                1,
                5,
                int(
                    joy.get(
                        "expectation",
                        3,
                    )
                ),
            )
        )

        edit_before = (
            st.text_area(
                "楽しみにしていた時のひとこと",
                value=joy.get(
                    "before_note",
                    "",
                ),
            )
        )

        if st.button(
            "💾 基本情報を保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "楽しみを入力してね。"
                )

            else:
                joy[
                    "title"
                ] = edit_title.strip()

                joy[
                    "category"
                ] = edit_category

                joy[
                    "date_unknown"
                ] = edit_unknown

                joy[
                    "event_date"
                ] = (
                    None
                    if edit_unknown
                    else str(
                        edit_event_date
                    )
                )

                joy[
                    "expectation"
                ] = int(
                    edit_expectation
                )

                joy[
                    "before_note"
                ] = (
                    edit_before.strip()
                )

                joy[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

        # -------------------------------------------------
        # MEMORY EDIT
        # -------------------------------------------------

        if (
            joy.get("status")
            == STATUS_MEMORY
        ):
            st.divider()

            st.subheader(
                "📸 思い出を編集"
            )

            edit_actual = (
                st.slider(
                    "実際の満足度",
                    1,
                    5,
                    int(
                        joy.get(
                            "actual_rating",
                            3,
                        )
                    ),
                    key=(
                        "manage_actual"
                    ),
                )
            )

            edit_after = (
                st.text_area(
                    "感想",
                    value=joy.get(
                        "after_note",
                        "",
                    ),
                    key=(
                        "manage_after"
                    ),
                )
            )

            current_repeat = (
                joy.get(
                    "repeat"
                )
            )

            repeat_index = (
                REPEAT_OPTIONS.index(
                    current_repeat
                )
                if current_repeat
                in REPEAT_OPTIONS
                else 1
            )

            edit_repeat = (
                st.selectbox(
                    "またやりたい？",
                    REPEAT_OPTIONS,
                    index=(
                        repeat_index
                    ),
                    key=(
                        "manage_repeat"
                    ),
                )
            )

            if st.button(
                "💾 思い出を保存",
                use_container_width=True,
            ):
                joy[
                    "actual_rating"
                ] = int(
                    edit_actual
                )

                joy[
                    "after_note"
                ] = (
                    edit_after.strip()
                )

                joy[
                    "repeat"
                ] = edit_repeat

                joy[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

        # -------------------------------------------------
        # ACTIONS
        # -------------------------------------------------

        st.divider()

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            if st.button(
                (
                    "⭐ お気に入りから外す"
                    if joy.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入りにする"
                ),
                use_container_width=True,
            ):
                toggle_favorite(
                    data,
                    selected_id,
                )

                st.rerun()

        with col2:
            if (
                joy.get("status")
                == STATUS_WAITING
            ):
                if st.button(
                    "🫧 今回はやめる",
                    use_container_width=True,
                ):
                    cancel_joy(
                        data,
                        selected_id,
                    )

                    st.rerun()

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        st.divider()

        delete_confirm = (
            st.checkbox(
                "この記録を削除する",
                key=(
                    "delete_confirm_"
                    + selected_id
                ),
            )
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=(
                not delete_confirm
            ),
            key=(
                "delete_"
                + selected_id
            ),
            use_container_width=True,
        ):
            delete_joy(
                data,
                selected_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    backup_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=backup_text,
        file_name=(
            "future_joys_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <p>
            🌈 <b>
            未来に楽しみがある。
            </b>
        </p>

        <p>
            それだけで、
            今日が少し違って見える。
        </p>

        <p>
            楽しみに待っていた時間も、
            きっと思い出の一部になる。
        </p>

        <br>

        <b>DAY 304 / 365 — COMPLETE 🔥</b>
    </div>
    """,
    unsafe_allow_html=True,
)
