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
    page_title="今の自分に必要なのは？",
    page_icon="🧭",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "need_data.json",
)

NEED_TYPES = [
    "😴 睡眠・休息",
    "🌿 回復",
    "😊 気分転換",
    "🧠 集中",
    "🧹 整理",
    "🚀 行動",
]

PLACES = [
    "🏠 家",
    "💼 仕事・学校",
    "🚃 移動中",
    "🌳 外出先",
    "✨ どこでも",
]

TIME_OPTIONS = [
    5,
    10,
    15,
    30,
    60,
    120,
]


# =========================================================
# 初期アクション
# =========================================================

DEFAULT_ACTIONS = [
    {
        "name": "目を閉じて5分休む",
        "need_type": "😴 睡眠・休息",
        "minutes": 5,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
            "🚃 移動中",
            "✨ どこでも",
        ],
    },
    {
        "name": "15分だけ横になる",
        "need_type": "😴 睡眠・休息",
        "minutes": 15,
        "places": [
            "🏠 家",
        ],
    },
    {
        "name": "今日は早めに休む準備をする",
        "need_type": "😴 睡眠・休息",
        "minutes": 10,
        "places": [
            "🏠 家",
        ],
    },
    {
        "name": "水を一杯飲む",
        "need_type": "🌿 回復",
        "minutes": 5,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "10分だけ何もしない",
        "need_type": "🌿 回復",
        "minutes": 10,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
            "✨ どこでも",
        ],
    },
    {
        "name": "10分散歩する",
        "need_type": "🌿 回復",
        "minutes": 10,
        "places": [
            "🌳 外出先",
            "🏠 家",
        ],
    },
    {
        "name": "ゆっくり飲み物を飲む",
        "need_type": "🌿 回復",
        "minutes": 10,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "好きな音楽を1曲聴く",
        "need_type": "😊 気分転換",
        "minutes": 5,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "外の空気を吸う",
        "need_type": "😊 気分転換",
        "minutes": 5,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
            "🌳 外出先",
        ],
    },
    {
        "name": "15分だけ好きなことをする",
        "need_type": "😊 気分転換",
        "minutes": 15,
        "places": [
            "🏠 家",
        ],
    },
    {
        "name": "25分だけ集中する",
        "need_type": "🧠 集中",
        "minutes": 25,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
        ],
    },
    {
        "name": "通知を切って15分作業する",
        "need_type": "🧠 集中",
        "minutes": 15,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
        ],
    },
    {
        "name": "一番重要な作業を1個だけ進める",
        "need_type": "🧠 集中",
        "minutes": 30,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
        ],
    },
    {
        "name": "机の上を1か所だけ片付ける",
        "need_type": "🧹 整理",
        "minutes": 5,
        "places": [
            "🏠 家",
            "💼 仕事・学校",
        ],
    },
    {
        "name": "頭の中のことを全部メモする",
        "need_type": "🧹 整理",
        "minutes": 10,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "次にやることを3つ書く",
        "need_type": "🧹 整理",
        "minutes": 5,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "一番小さいタスクを1個終わらせる",
        "need_type": "🚀 行動",
        "minutes": 10,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "5分だけ手をつける",
        "need_type": "🚀 行動",
        "minutes": 5,
        "places": [
            "✨ どこでも",
        ],
    },
    {
        "name": "やることを1つ選んで開始する",
        "need_type": "🚀 行動",
        "minutes": 15,
        "places": [
            "✨ どこでも",
        ],
    },
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


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value
        )
    except (ValueError, TypeError):
        return None


def format_datetime(value):
    parsed = parse_datetime(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d %H:%M"
    )


def average(values):
    values = [
        value
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "checks": [],
        "actions": [],
        "sessions": [],
    }


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


def initialize_actions(data):
    if data["actions"]:
        return

    for action in DEFAULT_ACTIONS:
        data["actions"].append(
            {
                "id": create_id(),
                "name": action["name"],
                "need_type": action[
                    "need_type"
                ],
                "minutes": action[
                    "minutes"
                ],
                "places": action[
                    "places"
                ],
                "custom": False,
                "active": True,
                "created_at": now_text(),
            }
        )

    save_data(data)


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = empty_data()
        save_data(data)
        initialize_actions(data)
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
            data = empty_data()

        data.setdefault(
            "checks",
            [],
        )
        data.setdefault(
            "actions",
            [],
        )
        data.setdefault(
            "sessions",
            [],
        )

        initialize_actions(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = empty_data()
        save_data(data)
        initialize_actions(data)
        return data


# =========================================================
# 判定
# =========================================================

def determine_need(
    energy,
    focus,
    sleepiness,
    stress,
):
    if sleepiness >= 75:
        return (
            "😴 睡眠・休息",
            "眠気がかなり高めです。"
            "まず休息を優先してみよう。",
        )

    if energy <= 35:
        return (
            "🌿 回復",
            "エネルギーが低めです。"
            "今は回復を優先するのがおすすめ。",
        )

    if stress >= 70:
        return (
            "😊 気分転換",
            "ストレスが高めです。"
            "いったん気分を切り替えてみよう。",
        )

    if (
        focus >= 70
        and energy >= 55
    ):
        return (
            "🧠 集中",
            "集中力とエネルギーがあります。"
            "今は集中作業のチャンス。",
        )

    if (
        focus <= 40
        and energy >= 45
    ):
        return (
            "🧹 整理",
            "動く余力はありますが、"
            "集中が散り気味です。"
            "まず整理すると進みやすそう。",
        )

    return (
        "🚀 行動",
        "大きく崩れてはいません。"
        "小さな一歩を始めてみよう。",
    )


# =========================================================
# CRUD
# =========================================================

def add_check(
    data,
    energy,
    focus,
    sleepiness,
    stress,
    available_minutes,
    place,
):
    need_type, reason = (
        determine_need(
            energy,
            focus,
            sleepiness,
            stress,
        )
    )

    check = {
        "id": create_id(),
        "energy": energy,
        "focus": focus,
        "sleepiness": sleepiness,
        "stress": stress,
        "available_minutes": (
            available_minutes
        ),
        "place": place,
        "need_type": need_type,
        "reason": reason,
        "created_at": now_text(),
    }

    data["checks"].append(
        check
    )

    save_data(data)

    return check


def get_check(
    data,
    check_id,
):
    return next(
        (
            item
            for item in data["checks"]
            if item.get("id")
            == check_id
        ),
        None,
    )


def get_action(
    data,
    action_id,
):
    return next(
        (
            item
            for item in data["actions"]
            if item.get("id")
            == action_id
        ),
        None,
    )


def add_custom_action(
    data,
    name,
    need_type,
    minutes,
    places,
):
    action = {
        "id": create_id(),
        "name": name,
        "need_type": need_type,
        "minutes": int(
            minutes
        ),
        "places": places,
        "custom": True,
        "active": True,
        "created_at": now_text(),
    }

    data["actions"].append(
        action
    )

    save_data(data)


def delete_custom_action(
    data,
    action_id,
):
    data["actions"] = [
        action
        for action in data["actions"]
        if not (
            action.get("id")
            == action_id
            and action.get(
                "custom",
                False,
            )
        )
    ]

    save_data(data)


def start_session(
    data,
    check_id,
    action_id,
):
    check = get_check(
        data,
        check_id,
    )

    action = get_action(
        data,
        action_id,
    )

    if not check or not action:
        return None

    session = {
        "id": create_id(),
        "check_id": check_id,
        "action_id": action_id,
        "action_name": action[
            "name"
        ],
        "need_type": action[
            "need_type"
        ],
        "before_energy": check[
            "energy"
        ],
        "before_focus": check[
            "focus"
        ],
        "before_sleepiness": check[
            "sleepiness"
        ],
        "before_stress": check[
            "stress"
        ],
        "after_energy": None,
        "after_focus": None,
        "after_sleepiness": None,
        "after_stress": None,
        "status": "running",
        "started_at": now_text(),
        "completed_at": None,
        "comment": "",
    }

    data["sessions"].append(
        session
    )

    save_data(data)

    return session


def complete_session(
    data,
    session_id,
    energy,
    focus,
    sleepiness,
    stress,
    comment,
):
    session = next(
        (
            item
            for item
            in data["sessions"]
            if item.get("id")
            == session_id
        ),
        None,
    )

    if not session:
        return

    session[
        "after_energy"
    ] = energy

    session[
        "after_focus"
    ] = focus

    session[
        "after_sleepiness"
    ] = sleepiness

    session[
        "after_stress"
    ] = stress

    session["status"] = (
        "completed"
    )

    session["completed_at"] = (
        now_text()
    )

    session["comment"] = comment

    save_data(data)


def cancel_session(
    data,
    session_id,
):
    session = next(
        (
            item
            for item
            in data["sessions"]
            if item.get("id")
            == session_id
        ),
        None,
    )

    if not session:
        return

    session["status"] = (
        "cancelled"
    )

    session["completed_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# 提案
# =========================================================

def matching_actions(
    data,
    need_type,
    available_minutes,
    place,
):
    actions = []

    for action in data[
        "actions"
    ]:
        if not action.get(
            "active",
            True,
        ):
            continue

        if action.get(
            "need_type"
        ) != need_type:
            continue

        if int(
            action.get(
                "minutes",
                0,
            )
        ) > available_minutes:
            continue

        places = action.get(
            "places",
            [],
        )

        if (
            place not in places
            and "✨ どこでも"
            not in places
        ):
            continue

        actions.append(action)

    return actions


# =========================================================
# 効果計算
# =========================================================

def session_effect(
    session,
):
    if session.get(
        "status"
    ) != "completed":
        return None

    values = [
        session.get(
            "after_energy"
        ),
        session.get(
            "after_focus"
        ),
        session.get(
            "after_sleepiness"
        ),
        session.get(
            "after_stress"
        ),
    ]

    if any(
        value is None
        for value in values
    ):
        return None

    energy_change = (
        session["after_energy"]
        - session[
            "before_energy"
        ]
    )

    focus_change = (
        session["after_focus"]
        - session[
            "before_focus"
        ]
    )

    sleep_change = (
        session[
            "before_sleepiness"
        ]
        - session[
            "after_sleepiness"
        ]
    )

    stress_change = (
        session[
            "before_stress"
        ]
        - session[
            "after_stress"
        ]
    )

    score = (
        energy_change
        + focus_change
        + sleep_change
        + stress_change
    ) / 4

    return {
        "energy": energy_change,
        "focus": focus_change,
        "sleepiness": sleep_change,
        "stress": stress_change,
        "score": round(
            score,
            1,
        ),
    }


def action_effect_stats(
    data,
):
    stats = {}

    for session in data[
        "sessions"
    ]:
        effect = session_effect(
            session
        )

        if not effect:
            continue

        action_name = (
            session.get(
                "action_name",
                "",
            )
        )

        if action_name not in stats:
            stats[action_name] = {
                "count": 0,
                "energy": [],
                "focus": [],
                "sleepiness": [],
                "stress": [],
                "score": [],
            }

        stats[
            action_name
        ]["count"] += 1

        for key in [
            "energy",
            "focus",
            "sleepiness",
            "stress",
            "score",
        ]:
            stats[
                action_name
            ][key].append(
                effect[key]
            )

    rows = []

    for action_name, values in (
        stats.items()
    ):
        rows.append(
            {
                "アクション": (
                    action_name
                ),
                "回数": (
                    values["count"]
                ),
                "🔋": average(
                    values["energy"]
                ),
                "🧠": average(
                    values["focus"]
                ),
                "😴改善": average(
                    values[
                        "sleepiness"
                    ]
                ),
                "😣改善": average(
                    values["stress"]
                ),
                "総合効果": average(
                    values["score"]
                ),
            }
        )

    return rows


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
        background: rgba(80, 150, 220, 0.07);
        border: 1px solid rgba(80, 150, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 150, 230, 0.18),
                rgba(90, 200, 140, 0.10)
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

    .need-box {
        padding: 25px;
        border-radius: 20px;
        background: rgba(
            100,
            180,
            150,
            0.08
        );
        margin: 15px 0;
    }

    .need-title {
        font-size: 2rem;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

checks = data["checks"]
actions = data["actions"]
sessions = data["sessions"]

completed_sessions = [
    session
    for session in sessions
    if session.get(
        "status"
    )
    == "completed"
]

running_sessions = [
    session
    for session in sessions
    if session.get(
        "status"
    )
    == "running"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧭 今の自分に必要なのは？</h1>
        <p>
            完璧な答えじゃなくていい。
            今の自分に合う、次の一歩を。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

effects = [
    session_effect(session)
    for session
    in completed_sessions
]

effects = [
    effect
    for effect in effects
    if effect
]

improved_count = len(
    [
        effect
        for effect in effects
        if effect["score"] > 0
    ]
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🧭 チェック",
    f"{len(checks)}回",
)

col2.metric(
    "🌱 実行",
    f"{len(completed_sessions)}回",
)

col3.metric(
    "✨ 改善",
    f"{improved_count}回",
)

col4.metric(
    "📈 平均効果",
    (
        f"{average([e['score'] for e in effects]):+.1f}"
        if effects
        else "-"
    ),
)


# =========================================================
# 実行中
# =========================================================

if running_sessions:
    st.divider()

    st.subheader(
        "🌱 今やっていること"
    )

    for session in (
        running_sessions
    ):
        session_id = (
            session.get(
                "id",
                "",
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                session.get(
                    "action_name",
                    "",
                )
            )

            st.caption(
                "開始："
                + format_datetime(
                    session.get(
                        "started_at"
                    )
                )
            )

            st.write(
                f"🧭 {session.get('need_type', '')}"
            )

            with st.expander(
                "✅ やった！"
            ):
                st.write(
                    "### 終わった後の状態"
                )

                after_energy = (
                    st.slider(
                        "🔋 エネルギー",
                        0,
                        100,
                        int(
                            session.get(
                                "before_energy",
                                50,
                            )
                        ),
                        key=(
                            "after_energy_"
                            + session_id
                        ),
                    )
                )

                after_focus = (
                    st.slider(
                        "🧠 集中力",
                        0,
                        100,
                        int(
                            session.get(
                                "before_focus",
                                50,
                            )
                        ),
                        key=(
                            "after_focus_"
                            + session_id
                        ),
                    )
                )

                after_sleepiness = (
                    st.slider(
                        "😴 眠気",
                        0,
                        100,
                        int(
                            session.get(
                                "before_sleepiness",
                                50,
                            )
                        ),
                        key=(
                            "after_sleep_"
                            + session_id
                        ),
                    )
                )

                after_stress = (
                    st.slider(
                        "😣 ストレス",
                        0,
                        100,
                        int(
                            session.get(
                                "before_stress",
                                50,
                            )
                        ),
                        key=(
                            "after_stress_"
                            + session_id
                        ),
                    )
                )

                comment = (
                    st.text_area(
                        "📝 ひとこと",
                        key=(
                            "complete_comment_"
                            + session_id
                        ),
                    )
                )

                if st.button(
                    "✅ 完了する",
                    key=(
                        "complete_"
                        + session_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    complete_session(
                        data,
                        session_id,
                        after_energy,
                        after_focus,
                        after_sleepiness,
                        after_stress,
                        comment.strip(),
                    )

                    st.session_state[
                        "completed_session_id"
                    ] = session_id

                    st.rerun()

            if st.button(
                "⏹️ 今回はやめる",
                key=(
                    "cancel_"
                    + session_id
                ),
            ):
                cancel_session(
                    data,
                    session_id,
                )
                st.rerun()


# =========================================================
# 完了直後の効果
# =========================================================

completed_id = (
    st.session_state.pop(
        "completed_session_id",
        None,
    )
)

if completed_id:
    completed = next(
        (
            item
            for item in data[
                "sessions"
            ]
            if item.get("id")
            == completed_id
        ),
        None,
    )

    if completed:
        effect = session_effect(
            completed
        )

        if effect:
            st.success(
                "✨ おつかれさま！"
                " Before / Afterを記録しました。"
            )

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            col1.metric(
                "🔋 エネルギー",
                completed[
                    "after_energy"
                ],
                effect["energy"],
            )

            col2.metric(
                "🧠 集中力",
                completed[
                    "after_focus"
                ],
                effect["focus"],
            )

            col3.metric(
                "😴 眠気",
                completed[
                    "after_sleepiness"
                ],
                -effect[
                    "sleepiness"
                ],
                delta_color="inverse",
            )

            col4.metric(
                "😣 ストレス",
                completed[
                    "after_stress"
                ],
                -effect["stress"],
                delta_color="inverse",
            )


# =========================================================
# 状態チェック
# =========================================================

st.divider()

st.subheader(
    "🧭 今の自分をチェック"
)

with st.form(
    "check_form"
):
    col1, col2 = (
        st.columns(2)
    )

    with col1:
        energy = st.slider(
            "🔋 エネルギー",
            0,
            100,
            50,
        )

        focus = st.slider(
            "🧠 集中力",
            0,
            100,
            50,
        )

    with col2:
        sleepiness = st.slider(
            "😴 眠気",
            0,
            100,
            50,
        )

        stress = st.slider(
            "😣 ストレス",
            0,
            100,
            50,
        )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        available_minutes = (
            st.select_slider(
                "⏰ 使える時間",
                options=TIME_OPTIONS,
                value=15,
                format_func=lambda x: (
                    f"{x}分"
                ),
            )
        )

    with col2:
        place = st.selectbox(
            "📍 今いる場所",
            PLACES,
        )

    check_submit = (
        st.form_submit_button(
            "🧭 今必要なものを見る",
            type="primary",
            use_container_width=True,
        )
    )

    if check_submit:
        new_check = add_check(
            data=data,
            energy=energy,
            focus=focus,
            sleepiness=sleepiness,
            stress=stress,
            available_minutes=(
                available_minutes
            ),
            place=place,
        )

        st.session_state[
            "current_check_id"
        ] = new_check["id"]

        st.session_state.pop(
            "suggested_action_id",
            None,
        )

        st.rerun()


# =========================================================
# 判定結果
# =========================================================

current_check_id = (
    st.session_state.get(
        "current_check_id"
    )
)

current_check = (
    get_check(
        data,
        current_check_id,
    )
    if current_check_id
    else None
)

if current_check:
    st.divider()

    st.subheader(
        "✨ 今のあなたには……"
    )

    st.markdown(
        f"""
        <div class="need-box">
            <div class="need-title">
                {current_check["need_type"]}
            </div>
            <p>
                {current_check["reason"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "🔋",
        current_check["energy"],
    )

    col2.metric(
        "🧠",
        current_check["focus"],
    )

    col3.metric(
        "😴",
        current_check["sleepiness"],
    )

    col4.metric(
        "😣",
        current_check["stress"],
    )

    candidates = matching_actions(
        data,
        current_check[
            "need_type"
        ],
        current_check[
            "available_minutes"
        ],
        current_check[
            "place"
        ],
    )

    # 場所で候補がなくても、
    # どこでも使えるものを再検索
    if not candidates:
        candidates = [
            action
            for action
            in data["actions"]
            if (
                action.get(
                    "need_type"
                )
                == current_check[
                    "need_type"
                ]
                and int(
                    action.get(
                        "minutes",
                        0,
                    )
                )
                <= current_check[
                    "available_minutes"
                ]
                and action.get(
                    "active",
                    True,
                )
            )
        ]

    if candidates:
        valid_ids = [
            item["id"]
            for item in candidates
        ]

        suggested_id = (
            st.session_state.get(
                "suggested_action_id"
            )
        )

        if (
            suggested_id
            not in valid_ids
        ):
            suggested_id = (
                random.choice(
                    valid_ids
                )
            )

            st.session_state[
                "suggested_action_id"
            ] = suggested_id

        suggested = get_action(
            data,
            suggested_id,
        )

        if suggested:
            st.markdown(
                "### 🎯 次の一歩"
            )

            with st.container(
                border=True
            ):
                st.subheader(
                    suggested["name"]
                )

                st.write(
                    f"⏰ 約"
                    f"{suggested['minutes']}分"
                )

                st.caption(
                    suggested[
                        "need_type"
                    ]
                )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "🌱 やってみる",
                    type="primary",
                    use_container_width=True,
                ):
                    start_session(
                        data,
                        current_check[
                            "id"
                        ],
                        suggested[
                            "id"
                        ],
                    )

                    st.session_state.pop(
                        "current_check_id",
                        None,
                    )

                    st.session_state.pop(
                        "suggested_action_id",
                        None,
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "🎲 別の提案",
                    use_container_width=True,
                ):
                    alternatives = [
                        item
                        for item
                        in valid_ids
                        if item
                        != suggested_id
                    ]

                    if alternatives:
                        st.session_state[
                            "suggested_action_id"
                        ] = random.choice(
                            alternatives
                        )

                    st.rerun()

    else:
        st.info(
            "条件に合うアクションが"
            "まだありません。"
            "自分専用アクションを"
            "追加してみよう。"
        )


# =========================================================
# 自分に効く行動
# =========================================================

effect_rows = (
    action_effect_stats(
        data
    )
)

if effect_rows:
    st.divider()

    st.subheader(
        "🧠 自分には何が効く？"
    )

    effect_df = pd.DataFrame(
        effect_rows
    ).sort_values(
        [
            "総合効果",
            "回数",
        ],
        ascending=False,
    )

    best = effect_df.iloc[0]

    with st.container(
        border=True
    ):
        st.write(
            "🥇 **今のところ"
            "一番効果が高い行動**"
        )

        st.subheader(
            best["アクション"]
        )

        st.write(
            f"総合効果 "
            f"**{best['総合効果']:+.1f}**"
            f" ｜ {int(best['回数'])}回"
        )

    st.dataframe(
        effect_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "回数": st.column_config.NumberColumn(
                "回数",
                format="%d回",
            ),
            "🔋": st.column_config.NumberColumn(
                "🔋 エネルギー",
                format="%+.1f",
            ),
            "🧠": st.column_config.NumberColumn(
                "🧠 集中力",
                format="%+.1f",
            ),
            "😴改善": st.column_config.NumberColumn(
                "😴 眠気改善",
                format="%+.1f",
            ),
            "😣改善": st.column_config.NumberColumn(
                "😣 ストレス改善",
                format="%+.1f",
            ),
            "総合効果": st.column_config.NumberColumn(
                "✨ 総合効果",
                format="%+.1f",
            ),
        },
    )


# =========================================================
# 今月
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の自分"
)

month_prefix = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_checks = [
    item
    for item in checks
    if (
        item.get(
            "created_at",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_sessions = [
    item
    for item
    in completed_sessions
    if (
        item.get(
            "completed_at",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_effects = [
    session_effect(item)
    for item
    in month_sessions
]

month_effects = [
    item
    for item in month_effects
    if item
]

month_improved = len(
    [
        item
        for item
        in month_effects
        if item["score"] > 0
    ]
)

col1, col2, col3 = (
    st.columns(3)
)

col1.metric(
    "🧭 チェック",
    f"{len(month_checks)}回",
)

col2.metric(
    "🌱 行動実行",
    f"{len(month_sessions)}回",
)

col3.metric(
    "✨ 改善",
    f"{month_improved}回",
)


if month_checks:
    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "平均 🔋",
        f"{average([x['energy'] for x in month_checks]):.1f}",
    )

    col2.metric(
        "平均 🧠",
        f"{average([x['focus'] for x in month_checks]):.1f}",
    )

    col3.metric(
        "平均 😴",
        f"{average([x['sleepiness'] for x in month_checks]):.1f}",
    )

    col4.metric(
        "平均 😣",
        f"{average([x['stress'] for x in month_checks]):.1f}",
    )

    need_counts = {}

    for item in month_checks:
        need_type = item.get(
            "need_type",
            "",
        )

        need_counts[
            need_type
        ] = (
            need_counts.get(
                need_type,
                0,
            )
            + 1
        )

    if need_counts:
        most_common_need = max(
            need_counts,
            key=need_counts.get,
        )

        st.info(
            "🧭 今月もっとも多かった状態："
            f" **{most_common_need}**"
        )

        need_df = pd.DataFrame(
            [
                {
                    "状態": key,
                    "回数": value,
                }
                for key, value
                in need_counts.items()
            ]
        )

        st.bar_chart(
            need_df.set_index(
                "状態"
            )
        )


# =========================================================
# 状態推移
# =========================================================

if checks:
    st.divider()

    st.subheader(
        "📈 状態の推移"
    )

    recent_checks = sorted(
        checks,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
    )[-30:]

    chart_rows = []

    for item in recent_checks:
        parsed = parse_datetime(
            item.get(
                "created_at"
            )
        )

        if not parsed:
            continue

        chart_rows.append(
            {
                "日時": parsed,
                "エネルギー": (
                    item["energy"]
                ),
                "集中力": (
                    item["focus"]
                ),
                "眠気": (
                    item["sleepiness"]
                ),
                "ストレス": (
                    item["stress"]
                ),
            }
        )

    if chart_rows:
        chart_df = (
            pd.DataFrame(
                chart_rows
            )
            .set_index(
                "日時"
            )
        )

        st.line_chart(
            chart_df
        )


# =========================================================
# 自分専用アクション
# =========================================================

st.divider()

st.subheader(
    "🛠️ 自分専用アクション"
)

with st.form(
    "custom_action_form",
    clear_on_submit=True,
):
    custom_name = (
        st.text_input(
            "✨ アクション名",
            placeholder=(
                "例：ベランダで"
                "コーヒーを飲む"
            ),
        )
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        custom_type = (
            st.selectbox(
                "🧭 タイプ",
                NEED_TYPES,
            )
        )

        custom_minutes = (
            st.number_input(
                "⏰ 必要時間",
                min_value=1,
                max_value=240,
                value=10,
            )
        )

    with col2:
        custom_places = (
            st.multiselect(
                "📍 使える場所",
                PLACES,
                default=[
                    "✨ どこでも"
                ],
            )
        )

    add_submit = (
        st.form_submit_button(
            "➕ アクションを追加",
            use_container_width=True,
        )
    )

    if add_submit:
        if not custom_name.strip():
            st.warning(
                "アクション名を"
                "入力してね。"
            )

        elif not custom_places:
            st.warning(
                "使える場所を"
                "1つ以上選んでね。"
            )

        else:
            add_custom_action(
                data=data,
                name=(
                    custom_name.strip()
                ),
                need_type=(
                    custom_type
                ),
                minutes=(
                    custom_minutes
                ),
                places=(
                    custom_places
                ),
            )

            st.rerun()


custom_actions = [
    action
    for action in data["actions"]
    if action.get(
        "custom",
        False,
    )
]

if custom_actions:
    for action in custom_actions:
        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [6, 1]
                )
            )

            with col1:
                st.write(
                    f"**{action['name']}**"
                )

                st.caption(
                    f"{action['need_type']}"
                    f" ｜ {action['minutes']}分"
                    f" ｜ "
                    + " / ".join(
                        action[
                            "places"
                        ]
                    )
                )

            with col2:
                if st.button(
                    "🗑️",
                    key=(
                        "delete_action_"
                        + action["id"]
                    ),
                ):
                    delete_custom_action(
                        data,
                        action["id"],
                    )
                    st.rerun()


# =========================================================
# 履歴
# =========================================================

if completed_sessions:
    st.divider()

    st.subheader(
        "📚 行動履歴"
    )

    rows = []

    for session in sorted(
        completed_sessions,
        key=lambda item: (
            item.get(
                "completed_at",
                "",
            )
        ),
        reverse=True,
    ):
        effect = session_effect(
            session
        )

        rows.append(
            {
                "日時": (
                    format_datetime(
                        session.get(
                            "completed_at"
                        )
                    )
                ),
                "行動": (
                    session.get(
                        "action_name",
                        "",
                    )
                ),
                "タイプ": (
                    session.get(
                        "need_type",
                        "",
                    )
                ),
                "🔋": (
                    f"{effect['energy']:+}"
                    if effect
                    else "-"
                ),
                "🧠": (
                    f"{effect['focus']:+}"
                    if effect
                    else "-"
                ),
                "😴改善": (
                    f"{effect['sleepiness']:+}"
                    if effect
                    else "-"
                ),
                "😣改善": (
                    f"{effect['stress']:+}"
                    if effect
                    else "-"
                ),
                "総合": (
                    f"{effect['score']:+.1f}"
                    if effect
                    else "-"
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# データ管理
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
            "what_do_i_need_"
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
    "🧭 完璧な答えじゃなくていい。"
    "今の自分に合う、次の一歩を。"
)
