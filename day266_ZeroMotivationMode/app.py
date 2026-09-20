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
    page_title="やる気ゼロモード",
    page_icon="🪫",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "zero_motivation.json",
)

CATEGORIES = [
    "💻 AI・開発",
    "📚 勉強",
    "🎨 イラスト",
    "💼 仕事",
    "🏠 家事",
    "🧹 片付け",
    "💪 運動",
    "💰 お金",
    "🌿 生活",
    "🎮 趣味",
    "✨ その他",
]

STATES = [
    "😴 眠い",
    "😮‍💨 疲れた",
    "😐 普通",
    "🙂 まあまあ",
    "🔥 元気",
]

AVAILABLE_TIMES = [
    1,
    5,
    10,
    30,
    60,
]

LEVEL_LABELS = {
    1: "🪫 レベル1",
    2: "🌱 レベル2",
    3: "🙂 レベル3",
    4: "🔥 レベル4",
    5: "🚀 レベル5",
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
        "goals": [],
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


def motivation_level(
    motivation,
):
    if motivation <= 20:
        return 1

    if motivation <= 40:
        return 2

    if motivation <= 60:
        return 3

    if motivation <= 80:
        return 4

    return 5


def motivation_band(
    motivation,
):
    if motivation <= 20:
        return "🪫 0〜20%"

    if motivation <= 40:
        return "🌱 21〜40%"

    if motivation <= 60:
        return "🙂 41〜60%"

    if motivation <= 80:
        return "🔥 61〜80%"

    return "🚀 81〜100%"


def time_text(seconds):
    seconds = int(seconds)

    if seconds < 60:
        return f"約{seconds}秒"

    minutes = max(
        1,
        round(seconds / 60),
    )

    return f"約{minutes}分"


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
            "goals",
            [],
        )

        data.setdefault(
            "history",
            [],
        )

        for goal in data["goals"]:
            goal.setdefault(
                "id",
                create_id(),
            )

            goal.setdefault(
                "name",
                "",
            )

            goal.setdefault(
                "category",
                "✨ その他",
            )

            goal.setdefault(
                "active",
                True,
            )

            goal.setdefault(
                "favorite",
                False,
            )

            goal.setdefault(
                "created_at",
                now_text(),
            )

            goal.setdefault(
                "actions",
                [],
            )

            while len(
                goal["actions"]
            ) < 5:
                level = (
                    len(
                        goal["actions"]
                    )
                    + 1
                )

                goal["actions"].append(
                    {
                        "level": level,
                        "text": "",
                        "seconds": (
                            10
                            if level == 1
                            else level * 60
                        ),
                    }
                )

        for item in data["history"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "goal_id",
                "",
            )

            item.setdefault(
                "goal_name",
                "",
            )

            item.setdefault(
                "category",
                "✨ その他",
            )

            item.setdefault(
                "action",
                "",
            )

            item.setdefault(
                "level",
                1,
            )

            item.setdefault(
                "motivation",
                0,
            )

            item.setdefault(
                "state",
                "😐 普通",
            )

            item.setdefault(
                "available_minutes",
                5,
            )

            item.setdefault(
                "seconds",
                10,
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
# データ操作
# =========================================================

def get_goal_by_id(
    data,
    goal_id,
):
    return next(
        (
            goal
            for goal in data["goals"]
            if goal.get(
                "id"
            ) == goal_id
        ),
        None,
    )


def add_goal(
    data,
    name,
    category,
    actions,
):
    data["goals"].append(
        {
            "id": create_id(),
            "name": name,
            "category": category,
            "actions": actions,
            "active": True,
            "favorite": False,
            "created_at": now_text(),
        }
    )

    save_data(data)


def update_goal(
    data,
    goal_id,
    name,
    category,
    actions,
    active,
    favorite,
):
    goal = get_goal_by_id(
        data,
        goal_id,
    )

    if not goal:
        return

    goal["name"] = name
    goal["category"] = category
    goal["actions"] = actions
    goal["active"] = active
    goal["favorite"] = favorite

    save_data(data)


def delete_goal(
    data,
    goal_id,
):
    data["goals"] = [
        goal
        for goal in data["goals"]
        if goal.get(
            "id"
        ) != goal_id
    ]

    save_data(data)


def add_history(
    data,
    goal,
    action,
    motivation,
    state,
    available_minutes,
):
    data["history"].append(
        {
            "id": create_id(),
            "goal_id": goal.get(
                "id",
                "",
            ),
            "goal_name": goal.get(
                "name",
                "",
            ),
            "category": goal.get(
                "category",
                "✨ その他",
            ),
            "action": action.get(
                "text",
                "",
            ),
            "level": int(
                action.get(
                    "level",
                    1,
                )
            ),
            "motivation": int(
                motivation
            ),
            "state": state,
            "available_minutes": int(
                available_minutes
            ),
            "seconds": int(
                action.get(
                    "seconds",
                    10,
                )
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


# =========================================================
# 提案ロジック
# =========================================================

def find_candidates(
    goals,
    motivation,
    available_minutes,
):
    level = motivation_level(
        motivation
    )

    max_seconds = (
        available_minutes * 60
    )

    candidates = []

    active_goals = [
        goal
        for goal in goals
        if goal.get(
            "active",
            True,
        )
    ]

    for goal in active_goals:
        actions = goal.get(
            "actions",
            [],
        )

        valid_actions = [
            action
            for action in actions
            if (
                action.get(
                    "text",
                    ""
                ).strip()
                and int(
                    action.get(
                        "seconds",
                        0,
                    )
                ) <= max_seconds
                and int(
                    action.get(
                        "level",
                        1,
                    )
                ) <= level
            )
        ]

        if not valid_actions:
            valid_actions = [
                action
                for action in actions
                if (
                    action.get(
                        "text",
                        ""
                    ).strip()
                    and int(
                        action.get(
                            "seconds",
                            0,
                        )
                    ) <= max_seconds
                )
            ]

        if valid_actions:
            best_level = max(
                int(
                    action.get(
                        "level",
                        1,
                    )
                )
                for action
                in valid_actions
            )

            best_actions = [
                action
                for action
                in valid_actions
                if int(
                    action.get(
                        "level",
                        1,
                    )
                ) == best_level
            ]

            for action in best_actions:
                candidates.append(
                    {
                        "goal": goal,
                        "action": action,
                    }
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
            rgba(80, 190, 120, 0.07);
        border:
            1px solid
            rgba(80, 190, 120, 0.15);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 190, 120, 0.18),
                rgba(255, 210, 70, 0.08)
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

    .mission {
        padding: 28px;
        border-radius: 24px;
        margin-top: 15px;
        margin-bottom: 15px;

        background:
            linear-gradient(
                135deg,
                rgba(70, 190, 120, 0.12),
                rgba(100, 170, 255, 0.06)
            );
    }

    .mission-title {
        font-size: 1.8rem;
        font-weight: 800;
    }

    .success-box {
        padding: 25px;
        border-radius: 22px;
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

goals = data[
    "goals"
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


# =========================================================
# Session State
# =========================================================

defaults = {
    "suggested_goal_id": None,
    "suggested_level": None,
    "current_motivation": 20,
    "current_state": "😮‍💨 疲れた",
    "current_available": 5,
    "just_completed": False,
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

        <h1>🪫 やる気ゼロモード</h1>

        <p>
            やる気がなくても、
            10秒なら進める。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

month_days = len(
    {
        item.get(
            "record_date"
        )
        for item in month_history
        if item.get(
            "record_date"
        )
    }
)

low_motivation_count = len(
    [
        item
        for item in month_history
        if int(
            item.get(
                "motivation",
                0,
            )
        ) <= 20
    ]
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌱 今日の一歩",
    f"{len(today_history)}回",
)

col2.metric(
    "🔥 今月動けた日",
    f"{month_days}日",
)

col3.metric(
    "🪫 低やる気から動けた",
    f"{low_motivation_count}回",
)

col4.metric(
    "🏆 今月の行動",
    f"{len(month_history)}回",
)


# =========================================================
# 今日の状態
# =========================================================

st.divider()

st.subheader(
    "🪫 今の状態"
)

if not goals:
    st.info(
        "まずは下の「行動セットを作る」から"
        "目標を1つ登録してみよう！"
    )

motivation = st.slider(
    "今のやる気",
    min_value=0,
    max_value=100,
    value=st.session_state[
        "current_motivation"
    ],
    step=1,
)

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox(
        "今の状態",
        STATES,
        index=(
            STATES.index(
                st.session_state[
                    "current_state"
                ]
            )
            if st.session_state[
                "current_state"
            ] in STATES
            else 2
        ),
    )

with col2:
    available_minutes = (
        st.selectbox(
            "今使える時間",
            AVAILABLE_TIMES,
            index=(
                AVAILABLE_TIMES.index(
                    st.session_state[
                        "current_available"
                    ]
                )
                if st.session_state[
                    "current_available"
                ] in AVAILABLE_TIMES
                else 1
            ),
            format_func=lambda value: (
                f"{value}分"
            ),
        )
    )

st.caption(
    f"現在のモード："
    f"{LEVEL_LABELS[motivation_level(motivation)]}"
)


# =========================================================
# 提案ボタン
# =========================================================

if st.button(
    "🎯 これならできるを探す",
    type="primary",
    use_container_width=True,
):
    candidates = find_candidates(
        goals,
        motivation,
        available_minutes,
    )

    if not candidates:
        st.warning(
            "今の条件でできる行動がありません。"
            "もっと短い行動を登録してみよう。"
        )

    else:
        chosen = random.choice(
            candidates
        )

        st.session_state[
            "suggested_goal_id"
        ] = chosen[
            "goal"
        ].get(
            "id"
        )

        st.session_state[
            "suggested_level"
        ] = chosen[
            "action"
        ].get(
            "level"
        )

        st.session_state[
            "current_motivation"
        ] = motivation

        st.session_state[
            "current_state"
        ] = state

        st.session_state[
            "current_available"
        ] = available_minutes

        st.session_state[
            "just_completed"
        ] = False

        st.rerun()


# =========================================================
# 現在の提案
# =========================================================

suggested_goal_id = (
    st.session_state[
        "suggested_goal_id"
    ]
)

suggested_level = (
    st.session_state[
        "suggested_level"
    ]
)

if (
    suggested_goal_id
    and suggested_level
):
    goal = get_goal_by_id(
        data,
        suggested_goal_id,
    )

    if goal:
        action = next(
            (
                item
                for item in goal.get(
                    "actions",
                    [],
                )
                if int(
                    item.get(
                        "level",
                        0,
                    )
                ) == int(
                    suggested_level
                )
            ),
            None,
        )

        if action:
            st.markdown(
                f"""
                <div class="mission">

                    <div>
                        🎯 今はこれだけ
                    </div>

                    <div class="mission-title">
                        {action.get("text", "")}
                    </div>

                    <br>

                    <div>
                        {goal.get("category", "")}
                        &nbsp;
                        {goal.get("name", "")}
                    </div>

                    <div>
                        ⏱️ {time_text(
                            action.get("seconds", 10)
                        )}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.success(
                "これだけでOK。"
                "終わったら、そのまま今日は"
                "終了しても成功です。"
            )

            button_col1, button_col2 = (
                st.columns(2)
            )

            with button_col1:
                if st.button(
                    "✅ やった！",
                    type="primary",
                    use_container_width=True,
                ):
                    add_history(
                        data,
                        goal,
                        action,
                        st.session_state[
                            "current_motivation"
                        ],
                        st.session_state[
                            "current_state"
                        ],
                        st.session_state[
                            "current_available"
                        ],
                    )

                    st.session_state[
                        "just_completed"
                    ] = True

                    st.session_state[
                        "suggested_goal_id"
                    ] = None

                    st.session_state[
                        "suggested_level"
                    ] = None

                    st.rerun()

            with button_col2:
                if st.button(
                    "🎲 別のにする",
                    use_container_width=True,
                ):
                    candidates = (
                        find_candidates(
                            goals,
                            st.session_state[
                                "current_motivation"
                            ],
                            st.session_state[
                                "current_available"
                            ],
                        )
                    )

                    candidates = [
                        candidate
                        for candidate
                        in candidates
                        if not (
                            candidate[
                                "goal"
                            ].get(
                                "id"
                            )
                            == suggested_goal_id
                            and int(
                                candidate[
                                    "action"
                                ].get(
                                    "level",
                                    0,
                                )
                            )
                            == int(
                                suggested_level
                            )
                        )
                    ]

                    if candidates:
                        chosen = (
                            random.choice(
                                candidates
                            )
                        )

                        st.session_state[
                            "suggested_goal_id"
                        ] = chosen[
                            "goal"
                        ].get(
                            "id"
                        )

                        st.session_state[
                            "suggested_level"
                        ] = chosen[
                            "action"
                        ].get(
                            "level"
                        )

                        st.rerun()

                    else:
                        st.info(
                            "今の条件では"
                            "ほかの候補がありません。"
                        )


# =========================================================
# 完了メッセージ
# =========================================================

if st.session_state[
    "just_completed"
]:
    st.divider()

    st.markdown(
        """
        <div class="success-box">

            <h2>🎉 できた！</h2>

            <p>
                今日の一歩 +1
            </p>

            <strong>
                ここで終わっても成功です。
            </strong>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🌙 今日はここまで",
            use_container_width=True,
        ):
            st.session_state[
                "just_completed"
            ] = False

            st.rerun()

    with col2:
        if st.button(
            "🌱 もう一歩だけ",
            type="primary",
            use_container_width=True,
        ):
            candidates = find_candidates(
                goals,
                st.session_state[
                    "current_motivation"
                ],
                st.session_state[
                    "current_available"
                ],
            )

            if candidates:
                chosen = random.choice(
                    candidates
                )

                st.session_state[
                    "suggested_goal_id"
                ] = chosen[
                    "goal"
                ].get(
                    "id"
                )

                st.session_state[
                    "suggested_level"
                ] = chosen[
                    "action"
                ].get(
                    "level"
                )

            st.session_state[
                "just_completed"
            ] = False

            st.rerun()


# =========================================================
# 今日できたこと
# =========================================================

if today_history:
    st.divider()

    st.subheader(
        "🌱 今日できたこと"
    )

    today_sorted = sorted(
        today_history,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for item in today_sorted:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### ✅ "
                f"{item.get('action', '')}"
            )

            st.write(
                item.get(
                    "category",
                    ""
                ),
                "・",
                item.get(
                    "goal_name",
                    "",
                ),
            )

            st.caption(
                f"🪫 やる気 "
                f"{item.get('motivation', 0)}% "
                f"｜ "
                f"{item.get('state', '')} "
                f"｜ "
                f"⏱️ {time_text(item.get('seconds', 10))}"
            )


# =========================================================
# 行動セット作成
# =========================================================

st.divider()

st.subheader(
    "🧩 行動セットを作る"
)

with st.expander(
    "➕ 新しい行動セット"
):
    with st.form(
        "new_goal_form"
    ):
        goal_name = st.text_input(
            "目標・テーマ",
            placeholder=(
                "例：AIの勉強"
            ),
        )

        goal_category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        st.markdown(
            "### 🌱 5段階の行動"
        )

        action1 = st.text_input(
            "🪫 レベル1",
            placeholder=(
                "参考書を開く"
            ),
        )

        seconds1 = st.number_input(
            "レベル1の秒数",
            min_value=1,
            max_value=3600,
            value=10,
        )

        action2 = st.text_input(
            "🌱 レベル2",
            placeholder=(
                "1段落読む"
            ),
        )

        seconds2 = st.number_input(
            "レベル2の秒数",
            min_value=1,
            max_value=3600,
            value=60,
        )

        action3 = st.text_input(
            "🙂 レベル3",
            placeholder=(
                "1ページ読む"
            ),
        )

        seconds3 = st.number_input(
            "レベル3の秒数",
            min_value=1,
            max_value=7200,
            value=300,
        )

        action4 = st.text_input(
            "🔥 レベル4",
            placeholder=(
                "10分勉強する"
            ),
        )

        seconds4 = st.number_input(
            "レベル4の秒数",
            min_value=1,
            max_value=7200,
            value=600,
        )

        action5 = st.text_input(
            "🚀 レベル5",
            placeholder=(
                "1節進める"
            ),
        )

        seconds5 = st.number_input(
            "レベル5の秒数",
            min_value=1,
            max_value=10800,
            value=1800,
        )

        create_goal = (
            st.form_submit_button(
                "🧩 行動セットを登録",
                type="primary",
                use_container_width=True,
            )
        )

        if create_goal:
            actions = [
                {
                    "level": 1,
                    "text": action1.strip(),
                    "seconds": int(
                        seconds1
                    ),
                },
                {
                    "level": 2,
                    "text": action2.strip(),
                    "seconds": int(
                        seconds2
                    ),
                },
                {
                    "level": 3,
                    "text": action3.strip(),
                    "seconds": int(
                        seconds3
                    ),
                },
                {
                    "level": 4,
                    "text": action4.strip(),
                    "seconds": int(
                        seconds4
                    ),
                },
                {
                    "level": 5,
                    "text": action5.strip(),
                    "seconds": int(
                        seconds5
                    ),
                },
            ]

            if not goal_name.strip():
                st.warning(
                    "目標・テーマを入力してね。"
                )

            elif not any(
                action["text"]
                for action in actions
            ):
                st.warning(
                    "行動を1つ以上登録してね。"
                )

            else:
                add_goal(
                    data,
                    goal_name.strip(),
                    goal_category,
                    actions,
                )

                st.rerun()


# =========================================================
# やる気別の成功数
# =========================================================

if history:
    st.divider()

    st.subheader(
        "📊 やる気がなくても動けた"
    )

    band_order = [
        "🪫 0〜20%",
        "🌱 21〜40%",
        "🙂 41〜60%",
        "🔥 61〜80%",
        "🚀 81〜100%",
    ]

    band_counts = {
        band: 0
        for band in band_order
    }

    for item in history:
        band = motivation_band(
            int(
                item.get(
                    "motivation",
                    0,
                )
            )
        )

        band_counts[band] += 1

    band_df = pd.DataFrame(
        [
            {
                "やる気": band,
                "成功回数": (
                    band_counts[band]
                ),
            }
            for band in band_order
        ]
    )

    st.bar_chart(
        band_df.set_index(
            "やる気"
        )
    )

    if low_motivation_count > 0:
        st.success(
            f"🪫 今月は、やる気20%以下でも"
            f" {low_motivation_count}回 "
            "行動できています。"
        )


# =========================================================
# カテゴリー分析
# =========================================================

if month_history:
    st.divider()

    st.subheader(
        "🌱 今月動けたカテゴリー"
    )

    category_df = pd.DataFrame(
        [
            {
                "カテゴリー": item.get(
                    "category",
                    "✨ その他",
                )
            }
            for item in month_history
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

if history:
    st.divider()

    st.subheader(
        "📈 月別の一歩"
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
                name="行動回数"
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
# 行動セット管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 行動セットを編集"
):
    if not goals:
        st.caption(
            "まだ行動セットがありません。"
        )

    for goal in goals:
        goal_id = goal.get(
            "id",
            "",
        )

        with st.expander(
            (
                f"{goal.get('category', '')} "
                f"{goal.get('name', '')}"
            )
        ):
            edit_name = st.text_input(
                "目標・テーマ",
                value=goal.get(
                    "name",
                    "",
                ),
                key=(
                    "edit_name_"
                    + goal_id
                ),
            )

            current_category = (
                goal.get(
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
                        + goal_id
                    ),
                )
            )

            edit_actions = []

            for level in range(
                1,
                6,
            ):
                action = next(
                    (
                        item
                        for item
                        in goal.get(
                            "actions",
                            [],
                        )
                        if int(
                            item.get(
                                "level",
                                0,
                            )
                        ) == level
                    ),
                    {
                        "text": "",
                        "seconds": 60,
                    },
                )

                st.markdown(
                    f"**{LEVEL_LABELS[level]}**"
                )

                edit_text = (
                    st.text_input(
                        "行動",
                        value=action.get(
                            "text",
                            "",
                        ),
                        key=(
                            f"action_text_"
                            f"{goal_id}_"
                            f"{level}"
                        ),
                    )
                )

                edit_seconds = (
                    st.number_input(
                        "秒数",
                        min_value=1,
                        max_value=10800,
                        value=int(
                            action.get(
                                "seconds",
                                60,
                            )
                        ),
                        key=(
                            f"action_seconds_"
                            f"{goal_id}_"
                            f"{level}"
                        ),
                    )
                )

                edit_actions.append(
                    {
                        "level": level,
                        "text": (
                            edit_text.strip()
                        ),
                        "seconds": int(
                            edit_seconds
                        ),
                    }
                )

            edit_active = (
                st.checkbox(
                    "🎯 提案対象にする",
                    value=goal.get(
                        "active",
                        True,
                    ),
                    key=(
                        "active_"
                        + goal_id
                    ),
                )
            )

            edit_favorite = (
                st.checkbox(
                    "⭐ お気に入り",
                    value=goal.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "favorite_"
                        + goal_id
                    ),
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_goal_"
                        + goal_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.warning(
                            "目標名を入力してね。"
                        )

                    else:
                        update_goal(
                            data,
                            goal_id,
                            edit_name.strip(),
                            edit_category,
                            edit_actions,
                            edit_active,
                            edit_favorite,
                        )

                        st.rerun()

            with col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_goal_"
                        + goal_id
                    ),
                    use_container_width=True,
                ):
                    delete_goal(
                        data,
                        goal_id,
                    )

                    if (
                        st.session_state[
                            "suggested_goal_id"
                        ]
                        == goal_id
                    ):
                        st.session_state[
                            "suggested_goal_id"
                        ] = None

                        st.session_state[
                            "suggested_level"
                        ] = None

                    st.rerun()


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 行動履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "目標・行動から検索"
    ),
)

history_months = sorted(
    {
        item.get(
            "record_date",
            "",
        )[:7]
        for item in history
        if item.get(
            "record_date"
        )
    },
    reverse=True,
)

col1, col2 = st.columns(2)

with col1:
    month_filter = st.selectbox(
        "月",
        ["すべて"]
        + history_months,
    )

with col2:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key=(
                "history_category"
            ),
        )
    )


filtered_history = []

for item in history:
    if (
        month_filter != "すべて"
        and not item.get(
            "record_date",
            "",
        ).startswith(
            month_filter
        )
    ):
        continue

    if (
        category_filter != "すべて"
        and item.get(
            "category"
        ) != category_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                item.get(
                    "goal_name",
                    "",
                ),
                item.get(
                    "action",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text.lower()
            not in target
        ):
            continue

    filtered_history.append(
        item
    )


filtered_history = sorted(
    filtered_history,
    key=lambda item: (
        item.get(
            "created_at",
            "",
        )
    ),
    reverse=True,
)


if not filtered_history:
    st.info(
        "条件に合う履歴はありません。"
    )

else:
    rows = []

    for item in filtered_history:
        rows.append(
            {
                "日付": item.get(
                    "record_date",
                    "",
                ),
                "目標": item.get(
                    "goal_name",
                    "",
                ),
                "行動": item.get(
                    "action",
                    "",
                ),
                "カテゴリー": (
                    item.get(
                        "category",
                        "",
                    )
                ),
                "やる気": (
                    f"{item.get('motivation', 0)}%"
                ),
                "状態": item.get(
                    "state",
                    "",
                ),
                "時間": time_text(
                    item.get(
                        "seconds",
                        10,
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
# 履歴削除
# =========================================================

with st.expander(
    "🗑️ 履歴を削除"
):
    if not history:
        st.caption(
            "まだ履歴がありません。"
        )

    else:
        delete_options = {
            (
                f"{item.get('record_date', '')} ｜ "
                f"{item.get('action', '')}"
            ): item.get(
                "id"
            )
            for item in sorted(
                history,
                key=lambda item: (
                    item.get(
                        "created_at",
                        "",
                    )
                ),
                reverse=True,
            )
        }

        selected_label = (
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
                    selected_label
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
            "zero_motivation_"
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
    "やる気がなくても、10秒なら進める。"
    "小さく始めて、そこで終わっても成功。🪫🌱"
)
