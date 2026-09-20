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
    page_title="未来の予定ガチャ",
    page_icon="🎲",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "future_plans.json",
)

CATEGORIES = [
    "🎨 趣味",
    "🍽️ 食べる",
    "👨‍👩‍👧 家族",
    "📚 学び",
    "🚶 お出かけ",
    "🎮 遊び",
    "💻 AI・開発",
    "💪 運動",
    "🌿 リラックス",
    "✨ その他",
]

LOCATIONS = [
    "🏠 家",
    "🚶 外出",
    "🌏 どちらでも",
]

TIME_OPTIONS = {
    "30分": 30,
    "1時間": 60,
    "2時間": 120,
    "半日": 300,
    "1日": 720,
}

BUDGET_OPTIONS = {
    "0円": 0,
    "1,000円": 1000,
    "3,000円": 3000,
    "5,000円": 5000,
    "10,000円": 10000,
    "制限なし": 999999999,
}

PASS_REASONS = [
    "😐 今は気分じゃない",
    "⏱️ 時間が足りない",
    "💰 お金を使いたくない",
    "☔ 天気・外出",
    "💤 疲れている",
    "📅 また今度",
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
        "plans": [],
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

    return (
        f"{target.year}年"
        f"{target.month}月"
        f"{target.day}日"
        f"（{weekdays[target.weekday()]}）"
    )


def month_key(target):
    return target.strftime(
        "%Y-%m"
    )


def time_label(minutes):
    minutes = int(minutes)

    if minutes < 60:
        return f"{minutes}分"

    if minutes == 60:
        return "1時間"

    if minutes < 300:
        hours = minutes / 60

        if hours.is_integer():
            return f"{int(hours)}時間"

        return f"{hours:.1f}時間"

    if minutes <= 360:
        return "半日"

    return "1日"


def money_text(value):
    return f"¥{int(value):,}"


def interest_stars(level):
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
            "plans",
            [],
        )

        data.setdefault(
            "history",
            [],
        )

        for plan in data["plans"]:
            plan.setdefault(
                "id",
                create_id(),
            )

            plan.setdefault(
                "title",
                "",
            )

            plan.setdefault(
                "category",
                "✨ その他",
            )

            plan.setdefault(
                "minutes",
                60,
            )

            plan.setdefault(
                "budget",
                0,
            )

            plan.setdefault(
                "location",
                "🌏 どちらでも",
            )

            plan.setdefault(
                "interest",
                3,
            )

            plan.setdefault(
                "memo",
                "",
            )

            plan.setdefault(
                "status",
                "waiting",
            )

            plan.setdefault(
                "pass_count",
                0,
            )

            plan.setdefault(
                "last_pass_reason",
                "",
            )

            plan.setdefault(
                "favorite",
                False,
            )

            plan.setdefault(
                "created_at",
                now_text(),
            )

            plan.setdefault(
                "started_at",
                "",
            )

        for item in data["history"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "plan_id",
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
                "satisfaction",
                0,
            )

            item.setdefault(
                "comment",
                "",
            )

            item.setdefault(
                "first_time",
                False,
            )

            item.setdefault(
                "minutes",
                0,
            )

            item.setdefault(
                "budget",
                0,
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

def get_plan_by_id(
    data,
    plan_id,
):
    return next(
        (
            plan
            for plan in data["plans"]
            if plan.get(
                "id"
            ) == plan_id
        ),
        None,
    )


def add_plan(
    data,
    title,
    category,
    minutes,
    budget,
    location,
    interest,
    memo,
):
    data["plans"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "minutes": int(
                minutes
            ),
            "budget": int(
                budget
            ),
            "location": location,
            "interest": int(
                interest
            ),
            "memo": memo,
            "status": "waiting",
            "pass_count": 0,
            "last_pass_reason": "",
            "favorite": False,
            "created_at": now_text(),
            "started_at": "",
        }
    )

    save_data(data)


def update_plan(
    data,
    plan_id,
    title,
    category,
    minutes,
    budget,
    location,
    interest,
    memo,
    favorite,
):
    plan = get_plan_by_id(
        data,
        plan_id,
    )

    if not plan:
        return

    plan["title"] = title
    plan["category"] = category
    plan["minutes"] = int(
        minutes
    )
    plan["budget"] = int(
        budget
    )
    plan["location"] = location
    plan["interest"] = int(
        interest
    )
    plan["memo"] = memo
    plan["favorite"] = bool(
        favorite
    )

    save_data(data)


def delete_plan(
    data,
    plan_id,
):
    data["plans"] = [
        plan
        for plan in data["plans"]
        if plan.get(
            "id"
        ) != plan_id
    ]

    save_data(data)


def start_plan(
    data,
    plan_id,
):
    plan = get_plan_by_id(
        data,
        plan_id,
    )

    if not plan:
        return

    plan["status"] = "doing"
    plan["started_at"] = (
        now_text()
    )

    save_data(data)


def pass_plan(
    data,
    plan_id,
    reason,
):
    plan = get_plan_by_id(
        data,
        plan_id,
    )

    if not plan:
        return

    plan["pass_count"] = int(
        plan.get(
            "pass_count",
            0,
        )
    ) + 1

    plan["last_pass_reason"] = (
        reason
    )

    save_data(data)


def return_to_waiting(
    data,
    plan_id,
):
    plan = get_plan_by_id(
        data,
        plan_id,
    )

    if not plan:
        return

    plan["status"] = "waiting"
    plan["started_at"] = ""

    save_data(data)


def complete_plan(
    data,
    plan_id,
    satisfaction,
    comment,
    first_time,
    return_to_gacha,
):
    plan = get_plan_by_id(
        data,
        plan_id,
    )

    if not plan:
        return

    data["history"].append(
        {
            "id": create_id(),
            "plan_id": plan_id,
            "title": plan.get(
                "title",
                "",
            ),
            "category": plan.get(
                "category",
                "✨ その他",
            ),
            "satisfaction": int(
                satisfaction
            ),
            "comment": comment,
            "first_time": bool(
                first_time
            ),
            "minutes": int(
                plan.get(
                    "minutes",
                    0,
                )
            ),
            "budget": int(
                plan.get(
                    "budget",
                    0,
                )
            ),
            "record_date": str(
                date.today()
            ),
            "created_at": now_text(),
        }
    )

    if return_to_gacha:
        plan["status"] = "waiting"
        plan["started_at"] = ""

    else:
        plan["status"] = "completed"
        plan["started_at"] = ""

    save_data(data)


def toggle_favorite(
    data,
    plan_id,
):
    plan = get_plan_by_id(
        data,
        plan_id,
    )

    if not plan:
        return

    plan["favorite"] = not (
        plan.get(
            "favorite",
            False,
        )
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


# =========================================================
# ガチャ候補
# =========================================================

def find_candidates(
    plans,
    max_minutes,
    max_budget,
    place_condition,
):
    candidates = []

    for plan in plans:
        if plan.get(
            "status",
            "waiting",
        ) != "waiting":
            continue

        if int(
            plan.get(
                "minutes",
                0,
            )
        ) > max_minutes:
            continue

        if int(
            plan.get(
                "budget",
                0,
            )
        ) > max_budget:
            continue

        plan_location = plan.get(
            "location",
            "🌏 どちらでも",
        )

        if place_condition == "🏠 家":
            if plan_location not in [
                "🏠 家",
                "🌏 どちらでも",
            ]:
                continue

        elif place_condition == "🚶 外出":
            if plan_location not in [
                "🚶 外出",
                "🌏 どちらでも",
            ]:
                continue

        candidates.append(
            plan
        )

    return candidates


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
            rgba(130, 100, 255, 0.07);
        border:
            1px solid
            rgba(130, 100, 255, 0.15);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(130, 100, 255, 0.18),
                rgba(255, 100, 180, 0.08)
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

    .gacha-box {
        padding: 30px;
        border-radius: 24px;
        margin-top: 15px;
        margin-bottom: 15px;

        background:
            linear-gradient(
                135deg,
                rgba(120, 90, 255, 0.14),
                rgba(255, 180, 60, 0.08)
            );
    }

    .gacha-title {
        font-size: 2rem;
        font-weight: 800;
    }

    .warning-box {
        padding: 18px;
        border-radius: 18px;
        background:
            rgba(255, 180, 60, 0.10);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

plans = data[
    "plans"
]

history = data[
    "history"
]

today = date.today()

current_month = month_key(
    today
)

waiting_plans = [
    plan
    for plan in plans
    if plan.get(
        "status"
    ) == "waiting"
]

doing_plans = [
    plan
    for plan in plans
    if plan.get(
        "status"
    ) == "doing"
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


# =========================================================
# Session State
# =========================================================

defaults = {
    "gacha_plan_id": None,
    "gacha_time": 60,
    "gacha_budget": 3000,
    "gacha_place": "🌏 どちらでも",
    "pass_mode": False,
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

        <h1>🎲 未来の予定ガチャ</h1>

        <p>
            「いつかやりたい」を、
            今日やってみる。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

first_time_count = len(
    [
        item
        for item in month_history
        if item.get(
            "first_time",
            False,
        )
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
    "🎲 ガチャ候補",
    f"{len(waiting_plans)}個",
)

col2.metric(
    "🚀 今月やった",
    f"{len(month_history)}個",
)

col3.metric(
    "✨ 初体験",
    f"{first_time_count}個",
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
# 今日のガチャ
# =========================================================

st.divider()

st.subheader(
    "🎰 今日なにする？"
)

col1, col2, col3 = (
    st.columns(3)
)

with col1:
    time_name = st.selectbox(
        "⏱️ 使える時間",
        list(
            TIME_OPTIONS.keys()
        ),
        index=1,
    )

with col2:
    budget_name = st.selectbox(
        "💰 予算",
        list(
            BUDGET_OPTIONS.keys()
        ),
        index=2,
    )

with col3:
    place_condition = st.selectbox(
        "📍 今日は？",
        [
            "🏠 家",
            "🚶 外出",
            "🌏 どちらでも",
        ],
        index=2,
    )


if st.button(
    "🎲 ガチャを回す！",
    type="primary",
    use_container_width=True,
):
    max_minutes = (
        TIME_OPTIONS[
            time_name
        ]
    )

    max_budget = (
        BUDGET_OPTIONS[
            budget_name
        ]
    )

    candidates = find_candidates(
        plans,
        max_minutes,
        max_budget,
        place_condition,
    )

    if not candidates:
        st.warning(
            "今の条件に合う予定がありません。"
            "時間や予算を少し広げてみよう！"
        )

    else:
        chosen = random.choice(
            candidates
        )

        st.session_state[
            "gacha_plan_id"
        ] = chosen.get(
            "id"
        )

        st.session_state[
            "gacha_time"
        ] = max_minutes

        st.session_state[
            "gacha_budget"
        ] = max_budget

        st.session_state[
            "gacha_place"
        ] = place_condition

        st.session_state[
            "pass_mode"
        ] = False

        st.rerun()


# =========================================================
# ガチャ結果
# =========================================================

gacha_plan_id = (
    st.session_state[
        "gacha_plan_id"
    ]
)

if gacha_plan_id:
    plan = get_plan_by_id(
        data,
        gacha_plan_id,
    )

    if (
        plan
        and plan.get(
            "status"
        ) == "waiting"
    ):
        st.markdown(
            f"""
            <div class="gacha-box">

                <div>
                    ✨ 今日これどう？
                </div>

                <div class="gacha-title">
                    {plan.get("title", "")}
                </div>

                <br>

                <div>
                    {plan.get("category", "")}
                </div>

                <div>
                    ⏱️ {time_label(
                        plan.get("minutes", 0)
                    )}
                    &nbsp;&nbsp;
                    💰 {money_text(
                        plan.get("budget", 0)
                    )}
                </div>

                <div>
                    {plan.get("location", "")}
                    &nbsp;&nbsp;
                    {interest_stars(
                        plan.get("interest", 3)
                    )}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if plan.get(
            "memo",
            "",
        ):
            st.caption(
                "💬 "
                + plan.get(
                    "memo",
                    "",
                )
            )

        col1, col2, col3 = (
            st.columns(3)
        )

        with col1:
            if st.button(
                "🚀 やってみる！",
                type="primary",
                use_container_width=True,
            ):
                start_plan(
                    data,
                    gacha_plan_id,
                )

                st.session_state[
                    "gacha_plan_id"
                ] = None

                st.rerun()

        with col2:
            if st.button(
                "🎲 もう一回！",
                use_container_width=True,
            ):
                candidates = (
                    find_candidates(
                        plans,
                        st.session_state[
                            "gacha_time"
                        ],
                        st.session_state[
                            "gacha_budget"
                        ],
                        st.session_state[
                            "gacha_place"
                        ],
                    )
                )

                candidates = [
                    item
                    for item in candidates
                    if item.get(
                        "id"
                    ) != gacha_plan_id
                ]

                if candidates:
                    chosen = random.choice(
                        candidates
                    )

                    st.session_state[
                        "gacha_plan_id"
                    ] = chosen.get(
                        "id"
                    )

                    st.session_state[
                        "pass_mode"
                    ] = False

                    st.rerun()

                else:
                    st.info(
                        "ほかの候補がありません。"
                    )

        with col3:
            if st.button(
                "💤 今回はパス",
                use_container_width=True,
            ):
                st.session_state[
                    "pass_mode"
                ] = True

        if st.session_state[
            "pass_mode"
        ]:
            st.markdown(
                "#### 💤 パスする理由"
            )

            pass_reason = st.selectbox(
                "理由",
                PASS_REASONS,
                key="pass_reason",
            )

            if st.button(
                "💤 パスを記録",
                use_container_width=True,
            ):
                pass_plan(
                    data,
                    gacha_plan_id,
                    pass_reason,
                )

                st.session_state[
                    "gacha_plan_id"
                ] = None

                st.session_state[
                    "pass_mode"
                ] = False

                st.rerun()


# =========================================================
# 挑戦中
# =========================================================

if doing_plans:
    st.divider()

    st.subheader(
        "🚀 挑戦中"
    )

    for plan in doing_plans:
        plan_id = plan.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### 🚀 "
                f"{plan.get('title', '')}"
            )

            st.write(
                plan.get(
                    "category",
                    "",
                )
            )

            st.caption(
                f"⏱️ "
                f"{time_label(plan.get('minutes', 0))}"
                f" ｜ 💰 "
                f"{money_text(plan.get('budget', 0))}"
                f" ｜ "
                f"{plan.get('location', '')}"
            )

            with st.expander(
                "🎉 やってみた！"
            ):
                satisfaction = st.slider(
                    "😊 満足度",
                    0,
                    100,
                    80,
                    key=(
                        "satisfaction_"
                        + plan_id
                    ),
                )

                comment = st.text_area(
                    "💬 一言",
                    placeholder=(
                        "やってみてどうだった？"
                    ),
                    key=(
                        "comment_"
                        + plan_id
                    ),
                )

                first_time = st.checkbox(
                    "✨ 初めての体験だった",
                    key=(
                        "first_time_"
                        + plan_id
                    ),
                )

                return_gacha = st.checkbox(
                    "🔁 またガチャ候補に戻す",
                    value=False,
                    key=(
                        "return_"
                        + plan_id
                    ),
                )

                if st.button(
                    "✨ 完了！",
                    type="primary",
                    key=(
                        "complete_"
                        + plan_id
                    ),
                    use_container_width=True,
                ):
                    complete_plan(
                        data,
                        plan_id,
                        satisfaction,
                        comment.strip(),
                        first_time,
                        return_gacha,
                    )

                    st.rerun()

            if st.button(
                "↩️ ガチャ候補へ戻す",
                key=(
                    "cancel_doing_"
                    + plan_id
                ),
            ):
                return_to_waiting(
                    data,
                    plan_id,
                )

                st.rerun()


# =========================================================
# 予定を追加
# =========================================================

st.divider()

st.subheader(
    "🌱 いつかやりたい"
)

with st.expander(
    "➕ ガチャ候補を追加"
):
    with st.form(
        "new_plan_form",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "やりたいこと",
            placeholder=(
                "例：行ったことのない店で"
                "ランチする"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            minutes = st.number_input(
                "⏱️ 必要時間（分）",
                min_value=1,
                max_value=1440,
                value=60,
                step=10,
            )

            budget = st.number_input(
                "💰 予算",
                min_value=0,
                max_value=1000000,
                value=0,
                step=500,
            )

        with col2:
            location = st.selectbox(
                "📍 場所",
                LOCATIONS,
            )

            interest = st.slider(
                "⭐ 気になる度",
                1,
                5,
                3,
            )

        memo = st.text_area(
            "💬 メモ",
            placeholder=(
                "店名・場所・やりたい理由など"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🎲 ガチャに追加",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "やりたいことを入力してね。"
                )

            else:
                add_plan(
                    data,
                    title.strip(),
                    category,
                    minutes,
                    budget,
                    location,
                    interest,
                    memo.strip(),
                )

                st.rerun()


# =========================================================
# 何度もパスしている予定
# =========================================================

often_passed = [
    plan
    for plan in waiting_plans
    if int(
        plan.get(
            "pass_count",
            0,
        )
    ) >= 5
]

if often_passed:
    st.divider()

    st.subheader(
        "👀 これ、本当にまだやりたい？"
    )

    st.caption(
        "5回以上パスした予定です。"
        "今もやりたいか見直してみよう。"
    )

    for plan in often_passed:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### {plan.get('title', '')}"
            )

            st.write(
                f"💤 パス "
                f"{plan.get('pass_count', 0)}回"
            )

            if plan.get(
                "last_pass_reason",
                "",
            ):
                st.caption(
                    "前回："
                    + plan.get(
                        "last_pass_reason",
                        "",
                    )
                )


# =========================================================
# やってよかった記録
# =========================================================

if history:
    st.divider()

    st.subheader(
        "🏆 やってよかった！"
    )

    best_history = sorted(
        history,
        key=lambda item: (
            int(
                item.get(
                    "satisfaction",
                    0,
                )
            ),
            item.get(
                "record_date",
                "",
            ),
        ),
        reverse=True,
    )[:5]

    for index, item in enumerate(
        best_history,
        start=1,
    ):
        with st.container(
            border=True
        ):
            st.markdown(
                f"### {index}. "
                f"{item.get('title', '')}"
            )

            st.write(
                f"😊 満足度 "
                f"{item.get('satisfaction', 0)}%"
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('record_date', '')}"
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


# =========================================================
# カテゴリー分析
# =========================================================

if waiting_plans:
    st.divider()

    st.subheader(
        "📊 ガチャの中身"
    )

    category_df = pd.DataFrame(
        [
            {
                "カテゴリー": plan.get(
                    "category",
                    "✨ その他",
                )
            }
            for plan in waiting_plans
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
            name="候補数"
        )
    )

    st.bar_chart(
        category_count.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 月別実行数
# =========================================================

if history:
    st.divider()

    st.subheader(
        "📈 月別「いつか」を実行した数"
    )

    monthly_rows = []

    for item in history:
        record_date = item.get(
            "record_date",
            "",
        )

        if len(record_date) >= 7:
            monthly_rows.append(
                {
                    "月": record_date[:7]
                }
            )

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
            name="実行数"
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
# ガチャ候補一覧
# =========================================================

st.divider()

st.subheader(
    "🎲 ガチャ候補一覧"
)

search_text = st.text_input(
    "🔎 候補を検索",
    placeholder=(
        "やりたいこと・メモから検索"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="plan_category_filter",
    )

with col2:
    location_filter = st.selectbox(
        "場所",
        ["すべて"] + LOCATIONS,
        key="plan_location_filter",
    )


filtered_plans = []

for plan in waiting_plans:
    if (
        category_filter != "すべて"
        and plan.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        location_filter != "すべて"
        and plan.get(
            "location"
        ) != location_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                plan.get(
                    "title",
                    "",
                ),
                plan.get(
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

    filtered_plans.append(
        plan
    )


filtered_plans = sorted(
    filtered_plans,
    key=lambda plan: (
        not plan.get(
            "favorite",
            False,
        ),
        -int(
            plan.get(
                "interest",
                0,
            )
        ),
    ),
)


if not filtered_plans:
    st.info(
        "条件に合う候補はありません。"
    )

else:
    for plan in filtered_plans:
        plan_id = plan.get(
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
                    f"### 🎲 "
                    f"{plan.get('title', '')}"
                )

            with col2:
                icon = (
                    "⭐"
                    if plan.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    icon,
                    key=(
                        "favorite_"
                        + plan_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        plan_id,
                    )

                    st.rerun()

            st.write(
                plan.get(
                    "category",
                    "",
                )
            )

            st.caption(
                f"⏱️ "
                f"{time_label(plan.get('minutes', 0))}"
                f" ｜ 💰 "
                f"{money_text(plan.get('budget', 0))}"
                f" ｜ "
                f"{plan.get('location', '')}"
                f" ｜ "
                f"{interest_stars(plan.get('interest', 3))}"
            )

            if int(
                plan.get(
                    "pass_count",
                    0,
                )
            ) > 0:
                st.caption(
                    f"💤 パス "
                    f"{plan.get('pass_count', 0)}回"
                )

            if plan.get(
                "memo",
                "",
            ):
                st.write(
                    plan.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ ガチャ候補を編集・削除"
):
    editable_plans = [
        plan
        for plan in plans
        if plan.get(
            "status"
        ) != "completed"
    ]

    if not editable_plans:
        st.caption(
            "編集できる候補がありません。"
        )

    for plan in editable_plans:
        plan_id = plan.get(
            "id",
            "",
        )

        with st.expander(
            plan.get(
                "title",
                "",
            )
        ):
            edit_title = st.text_input(
                "やりたいこと",
                value=plan.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + plan_id
                ),
            )

            current_category = (
                plan.get(
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
                    + plan_id
                ),
            )

            edit_minutes = st.number_input(
                "必要時間（分）",
                min_value=1,
                max_value=1440,
                value=int(
                    plan.get(
                        "minutes",
                        60,
                    )
                ),
                key=(
                    "edit_minutes_"
                    + plan_id
                ),
            )

            edit_budget = st.number_input(
                "予算",
                min_value=0,
                max_value=1000000,
                value=int(
                    plan.get(
                        "budget",
                        0,
                    )
                ),
                key=(
                    "edit_budget_"
                    + plan_id
                ),
            )

            current_location = (
                plan.get(
                    "location",
                    "🌏 どちらでも",
                )
            )

            location_index = (
                LOCATIONS.index(
                    current_location
                )
                if current_location
                in LOCATIONS
                else 2
            )

            edit_location = st.selectbox(
                "場所",
                LOCATIONS,
                index=location_index,
                key=(
                    "edit_location_"
                    + plan_id
                ),
            )

            edit_interest = st.slider(
                "気になる度",
                1,
                5,
                int(
                    plan.get(
                        "interest",
                        3,
                    )
                ),
                key=(
                    "edit_interest_"
                    + plan_id
                ),
            )

            edit_memo = st.text_area(
                "メモ",
                value=plan.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + plan_id
                ),
            )

            edit_favorite = st.checkbox(
                "⭐ お気に入り",
                value=plan.get(
                    "favorite",
                    False,
                ),
                key=(
                    "edit_fav_"
                    + plan_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + plan_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.warning(
                            "やりたいことを入力してね。"
                        )

                    else:
                        update_plan(
                            data,
                            plan_id,
                            edit_title.strip(),
                            edit_category,
                            edit_minutes,
                            edit_budget,
                            edit_location,
                            edit_interest,
                            edit_memo.strip(),
                            edit_favorite,
                        )

                        st.rerun()

            with col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_"
                        + plan_id
                    ),
                    use_container_width=True,
                ):
                    delete_plan(
                        data,
                        plan_id,
                    )

                    if (
                        st.session_state.get(
                            "gacha_plan_id"
                        )
                        == plan_id
                    ):
                        st.session_state[
                            "gacha_plan_id"
                        ] = None

                    st.rerun()


# =========================================================
# 完了履歴
# =========================================================

st.divider()

st.subheader(
    "📚 やってみた履歴"
)

if not history:
    st.info(
        "まだ完了した予定はありません。"
    )

else:
    history_rows = []

    for item in sorted(
        history,
        key=lambda item: (
            item.get(
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
                "やったこと": (
                    item.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    item.get(
                        "category",
                        "",
                    )
                ),
                "満足度": (
                    f"{item.get('satisfaction', 0)}%"
                ),
                "初体験": (
                    "✨"
                    if item.get(
                        "first_time",
                        False,
                    )
                    else ""
                ),
                "一言": item.get(
                    "comment",
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
# 完了済み候補
# =========================================================

completed_plans = [
    plan
    for plan in plans
    if plan.get(
        "status"
    ) == "completed"
]

if completed_plans:
    with st.expander(
        "🎓 ガチャを卒業した予定"
    ):
        for plan in completed_plans:
            plan_id = plan.get(
                "id",
                "",
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"**🎓 "
                    f"{plan.get('title', '')}**"
                )

                st.caption(
                    plan.get(
                        "category",
                        "",
                    )
                )

                if st.button(
                    "🔁 ガチャへ戻す",
                    key=(
                        "restore_"
                        + plan_id
                    ),
                ):
                    return_to_waiting(
                        data,
                        plan_id,
                    )

                    st.rerun()


# =========================================================
# 履歴削除
# =========================================================

with st.expander(
    "🗑️ 完了履歴を削除"
):
    if not history:
        st.caption(
            "履歴はありません。"
        )

    else:
        history_sorted = sorted(
            history,
            key=lambda item: (
                item.get(
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
                f"{item.get('satisfaction', 0)}%"
            ): item.get(
                "id"
            )
            for item in history_sorted
        }

        selected_history = (
            st.selectbox(
                "削除する履歴",
                list(
                    delete_options.keys()
                ),
            )
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
            "future_plan_gacha_"
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
    "「いつかやりたい」を、"
    "今日やってみる。🎲➡️🚀"
)
