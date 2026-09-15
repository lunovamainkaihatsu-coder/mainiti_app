import json
import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日のごほうび",
    page_icon="🎁",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "rewards.json",
)

CATEGORIES = [
    "☕ 食べる・飲む",
    "🎮 ゲーム",
    "🎬 動画・映画",
    "🛁 リラックス",
    "🛍️ 買い物",
    "🚶 お出かけ",
    "😴 休む",
    "🎨 趣味",
    "👨‍👩‍👧 家族",
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
        "rewards": []
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
    return target.strftime("%Y-%m")


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
            "rewards",
            [],
        )

        for reward in data["rewards"]:
            reward.setdefault(
                "id",
                create_id(),
            )

            reward.setdefault(
                "effort",
                "",
            )

            reward.setdefault(
                "reward",
                "",
            )

            reward.setdefault(
                "category",
                "✨ その他",
            )

            reward.setdefault(
                "satisfaction",
                50,
            )

            reward.setdefault(
                "recovery",
                50,
            )

            reward.setdefault(
                "memo",
                "",
            )

            reward.setdefault(
                "favorite",
                False,
            )

            reward.setdefault(
                "record_date",
                str(date.today()),
            )

            reward.setdefault(
                "created_at",
                now_text(),
            )

            reward.setdefault(
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

def get_reward_by_id(
    data,
    reward_id,
):
    return next(
        (
            reward
            for reward in data["rewards"]
            if reward.get("id") == reward_id
        ),
        None,
    )


def add_reward(
    data,
    effort,
    reward_text,
    category,
    satisfaction,
    recovery,
    memo,
    favorite,
    record_date,
):
    data["rewards"].append(
        {
            "id": create_id(),
            "effort": effort,
            "reward": reward_text,
            "category": category,
            "satisfaction": int(
                satisfaction
            ),
            "recovery": int(
                recovery
            ),
            "memo": memo,
            "favorite": bool(
                favorite
            ),
            "record_date": str(
                record_date
            ),
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_reward(
    data,
    reward_id,
    effort,
    reward_text,
    category,
    satisfaction,
    recovery,
    memo,
    favorite,
    record_date,
):
    item = get_reward_by_id(
        data,
        reward_id,
    )

    if not item:
        return

    item["effort"] = effort
    item["reward"] = reward_text
    item["category"] = category
    item["satisfaction"] = int(
        satisfaction
    )
    item["recovery"] = int(
        recovery
    )
    item["memo"] = memo
    item["favorite"] = bool(
        favorite
    )
    item["record_date"] = str(
        record_date
    )
    item["updated_at"] = now_text()

    save_data(data)


def delete_reward(
    data,
    reward_id,
):
    data["rewards"] = [
        reward
        for reward in data["rewards"]
        if reward.get("id") != reward_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    reward_id,
):
    item = get_reward_by_id(
        data,
        reward_id,
    )

    if not item:
        return

    item["favorite"] = not item.get(
        "favorite",
        False,
    )

    item["updated_at"] = now_text()

    save_data(data)


# =========================================================
# 集計関数
# =========================================================

def records_for_month(
    rewards,
    target_month,
):
    return [
        reward
        for reward in rewards
        if reward.get(
            "record_date",
            "",
        ).startswith(target_month)
    ]


def average_value(
    rewards,
    key,
):
    if not rewards:
        return 0

    return round(
        sum(
            int(
                reward.get(
                    key,
                    0,
                )
            )
            for reward in rewards
        )
        / len(rewards),
        1,
    )


def unique_days(rewards):
    return len(
        {
            reward.get(
                "record_date",
                "",
            )
            for reward in rewards
            if reward.get(
                "record_date"
            )
        }
    )


def category_stats(rewards):
    if not rewards:
        return pd.DataFrame()

    rows = []

    for reward in rewards:
        rows.append(
            {
                "カテゴリー": reward.get(
                    "category",
                    "✨ その他",
                ),
                "満足度": int(
                    reward.get(
                        "satisfaction",
                        0,
                    )
                ),
                "回復度": int(
                    reward.get(
                        "recovery",
                        0,
                    )
                ),
            }
        )

    df = pd.DataFrame(rows)

    grouped = (
        df.groupby(
            "カテゴリー",
            as_index=False,
        )
        .agg(
            満足度=("満足度", "mean"),
            回復度=("回復度", "mean"),
            回数=("カテゴリー", "count"),
        )
    )

    grouped["満足度"] = (
        grouped["満足度"]
        .round(1)
    )

    grouped["回復度"] = (
        grouped["回復度"]
        .round(1)
    )

    return grouped


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
        border-radius: 16px;
        padding: 15px;
        background: rgba(255, 180, 80, 0.08);
        border: 1px solid rgba(255, 180, 80, 0.18);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;
        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 90, 0.18),
                rgba(255, 130, 190, 0.10)
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

    .reward-message {
        padding: 24px;
        border-radius: 22px;
        margin-top: 12px;
        margin-bottom: 12px;
        text-align: center;
        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 100, 0.12),
                rgba(120, 220, 180, 0.08)
            );
    }

    .reward-message-title {
        font-size: 0.9rem;
        opacity: 0.7;
        font-weight: 700;
    }

    .reward-message-value {
        font-size: 1.35rem;
        font-weight: 900;
        margin-top: 7px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ
# =========================================================

data = load_data()

rewards = data["rewards"]

today = date.today()
today_text = str(today)
current_month = month_key(today)

month_rewards = records_for_month(
    rewards,
    current_month,
)

today_rewards = [
    reward
    for reward in rewards
    if reward.get(
        "record_date"
    ) == today_text
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎁 今日のごほうび</h1>

        <p>
            頑張った自分に、
            ちゃんと回復する時間を。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

month_satisfaction = average_value(
    month_rewards,
    "satisfaction",
)

month_recovery = average_value(
    month_rewards,
    "recovery",
)

month_days = unique_days(
    month_rewards
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🎁 今月のごほうび",
    f"{len(month_rewards)}回",
)

col2.metric(
    "😊 平均満足度",
    (
        f"{month_satisfaction}%"
        if month_rewards
        else "-"
    ),
)

col3.metric(
    "⚡ 平均回復度",
    (
        f"{month_recovery}%"
        if month_rewards
        else "-"
    ),
)

col4.metric(
    "🔥 ごほうびをあげた日",
    f"{month_days}日",
)


# =========================================================
# 新しいごほうび
# =========================================================

st.divider()

st.subheader(
    "🎀 今日のごほうびを記録"
)

with st.form(
    "new_reward_form"
):
    effort = st.text_input(
        "💪 今日頑張ったこと",
        placeholder=(
            "例：AIの勉強を30分やった"
        ),
    )

    reward_text = st.text_input(
        "🎁 自分へのごほうび",
        placeholder=(
            "例：コーヒーを飲みながら"
            "好きな動画を見た"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        satisfaction = st.slider(
            "😊 満足度",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
        )

    with col2:
        record_date = st.date_input(
            "📅 記録日",
            value=date.today(),
        )

        recovery = st.slider(
            "⚡ 回復度",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
        )

    memo = st.text_area(
        "💬 今日のひとこと",
        placeholder=(
            "例：短時間でもかなり"
            "気分転換になった！"
        ),
    )

    favorite = st.checkbox(
        "⭐ お気に入りのごほうびにする"
    )

    submitted = st.form_submit_button(
        "🎁 ごほうびを記録",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if not effort.strip():
            st.warning(
                "今日頑張ったことを入力してね。"
            )

        elif not reward_text.strip():
            st.warning(
                "ごほうびを入力してね。"
            )

        else:
            add_reward(
                data,
                effort.strip(),
                reward_text.strip(),
                category,
                satisfaction,
                recovery,
                memo.strip(),
                favorite,
                record_date,
            )

            st.rerun()


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "🌿 今日のごほうび"
)

if not today_rewards:
    st.info(
        "今日はまだごほうびを"
        "記録していません。"
    )

else:
    today_sorted = sorted(
        today_rewards,
        key=lambda reward: reward.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    for reward in today_sorted:
        with st.container(
            border=True
        ):
            top_col1, top_col2 = st.columns(
                [5, 1]
            )

            with top_col1:
                st.markdown(
                    f"### {reward.get('category', '✨ その他')}"
                )

            with top_col2:
                favorite_icon = (
                    "⭐"
                    if reward.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    favorite_icon,
                    key=(
                        "today_fav_"
                        + reward["id"]
                    ),
                ):
                    toggle_favorite(
                        data,
                        reward["id"],
                    )

                    st.rerun()

            st.write(
                "**💪 頑張ったこと**"
            )

            st.write(
                reward.get(
                    "effort",
                    "",
                )
            )

            st.write(
                "**🎁 ごほうび**"
            )

            st.write(
                reward.get(
                    "reward",
                    "",
                )
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "😊 満足度",
                f"{reward.get('satisfaction', 0)}%",
            )

            col2.metric(
                "⚡ 回復度",
                f"{reward.get('recovery', 0)}%",
            )

            if reward.get(
                "memo",
                "",
            ):
                st.caption(
                    "💬 "
                    + reward.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 自分に効くごほうび
# =========================================================

st.divider()

st.subheader(
    "🏆 自分に効くごほうび"
)

stats_df = category_stats(
    month_rewards
)

if stats_df.empty:
    st.info(
        "記録が増えると、"
        "自分に効くごほうびが"
        "見えてきます。"
    )

else:
    satisfaction_best = (
        stats_df.sort_values(
            "満足度",
            ascending=False,
        )
        .iloc[0]
    )

    recovery_best = (
        stats_df.sort_values(
            "回復度",
            ascending=False,
        )
        .iloc[0]
    )

    most_used = (
        stats_df.sort_values(
            "回数",
            ascending=False,
        )
        .iloc[0]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="reward-message">

                <div class="reward-message-title">
                    😊 満足度 No.1
                </div>

                <div class="reward-message-value">
                    {satisfaction_best["カテゴリー"]}
                </div>

                <div>
                    平均
                    {satisfaction_best["満足度"]}%
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="reward-message">

                <div class="reward-message-title">
                    ⚡ 回復度 No.1
                </div>

                <div class="reward-message-value">
                    {recovery_best["カテゴリー"]}
                </div>

                <div>
                    平均
                    {recovery_best["回復度"]}%
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="reward-message">

                <div class="reward-message-title">
                    🎁 よく選ぶごほうび
                </div>

                <div class="reward-message-value">
                    {most_used["カテゴリー"]}
                </div>

                <div>
                    {int(most_used["回数"])}回
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# カテゴリー分析
# =========================================================

if not stats_df.empty:
    st.divider()

    st.subheader(
        "📊 ごほうび分析"
    )

    chart_df = stats_df[
        [
            "カテゴリー",
            "満足度",
            "回復度",
        ]
    ].copy()

    st.bar_chart(
        chart_df.set_index(
            "カテゴリー"
        )
    )

    with st.expander(
        "📋 カテゴリー別データ"
    ):
        st.dataframe(
            stats_df.sort_values(
                "回復度",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 月内推移
# =========================================================

if month_rewards:
    st.divider()

    st.subheader(
        "📈 今月の満足度・回復度"
    )

    trend_rows = []

    for reward in month_rewards:
        trend_rows.append(
            {
                "日付": reward.get(
                    "record_date",
                    "",
                ),
                "満足度": int(
                    reward.get(
                        "satisfaction",
                        0,
                    )
                ),
                "回復度": int(
                    reward.get(
                        "recovery",
                        0,
                    )
                ),
            }
        )

    trend_df = pd.DataFrame(
        trend_rows
    )

    daily_df = (
        trend_df.groupby(
            "日付",
            as_index=False,
        )[
            [
                "満足度",
                "回復度",
            ]
        ]
        .mean()
        .sort_values("日付")
    )

    st.line_chart(
        daily_df.set_index(
            "日付"
        )
    )


# =========================================================
# お気に入り
# =========================================================

favorite_rewards = [
    reward
    for reward in rewards
    if reward.get(
        "favorite",
        False,
    )
]

if favorite_rewards:
    st.divider()

    st.subheader(
        "⭐ お気に入りのごほうび"
    )

    favorite_sorted = sorted(
        favorite_rewards,
        key=lambda reward: (
            reward.get(
                "satisfaction",
                0,
            )
            + reward.get(
                "recovery",
                0,
            )
        ),
        reverse=True,
    )

    for reward in favorite_sorted[:5]:
        with st.container(
            border=True
        ):
            st.markdown(
                f"**{reward.get('category', '✨ その他')}**"
            )

            st.write(
                "🎁 "
                + reward.get(
                    "reward",
                    "",
                )
            )

            st.caption(
                f"😊 {reward.get('satisfaction', 0)}%"
                f" ｜ "
                f"⚡ {reward.get('recovery', 0)}%"
                f" ｜ "
                f"{reward.get('record_date', '')}"
            )


# =========================================================
# 履歴・検索
# =========================================================

st.divider()

st.subheader(
    "📚 ごほうび履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "頑張ったこと・ごほうび・"
        "メモから検索"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="history_category",
    )

with col2:
    favorite_filter = st.selectbox(
        "お気に入り",
        [
            "すべて",
            "⭐ お気に入りのみ",
        ],
    )

filtered_rewards = []

for reward in rewards:
    if (
        category_filter != "すべて"
        and reward.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        favorite_filter
        == "⭐ お気に入りのみ"
        and not reward.get(
            "favorite",
            False,
        )
    ):
        continue

    if search_text.strip():
        target_text = " ".join(
            [
                reward.get(
                    "effort",
                    "",
                ),
                reward.get(
                    "reward",
                    "",
                ),
                reward.get(
                    "memo",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text.lower()
            not in target_text
        ):
            continue

    filtered_rewards.append(
        reward
    )

filtered_rewards = sorted(
    filtered_rewards,
    key=lambda reward: (
        reward.get(
            "record_date",
            "",
        ),
        reward.get(
            "created_at",
            "",
        ),
    ),
    reverse=True,
)

if not filtered_rewards:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    history_rows = []

    for reward in filtered_rewards:
        history_rows.append(
            {
                "日付": reward.get(
                    "record_date",
                    "",
                ),
                "カテゴリー": reward.get(
                    "category",
                    "",
                ),
                "頑張ったこと": reward.get(
                    "effort",
                    "",
                ),
                "ごほうび": reward.get(
                    "reward",
                    "",
                ),
                "満足度": reward.get(
                    "satisfaction",
                    0,
                ),
                "回復度": reward.get(
                    "recovery",
                    0,
                ),
                "お気に入り": (
                    "⭐"
                    if reward.get(
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
    if not rewards:
        st.caption(
            "まだ記録がありません。"
        )

    else:
        edit_rewards = sorted(
            rewards,
            key=lambda reward: (
                reward.get(
                    "record_date",
                    "",
                ),
                reward.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        for reward in edit_rewards:
            reward_id = reward.get(
                "id",
                ""
            )

            title = (
                f"{reward.get('category', '✨ その他')} "
                f"{reward.get('reward', '')[:30]}"
            )

            with st.expander(
                title
            ):
                edit_effort = st.text_input(
                    "頑張ったこと",
                    value=reward.get(
                        "effort",
                        "",
                    ),
                    key=(
                        "edit_effort_"
                        + reward_id
                    ),
                )

                edit_reward = st.text_input(
                    "ごほうび",
                    value=reward.get(
                        "reward",
                        "",
                    ),
                    key=(
                        "edit_reward_"
                        + reward_id
                    ),
                )

                col1, col2 = st.columns(2)

                with col1:
                    current_category = (
                        reward.get(
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
                        else 0
                    )

                    edit_category = st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=category_index,
                        key=(
                            "edit_category_"
                            + reward_id
                        ),
                    )

                    edit_satisfaction = st.slider(
                        "満足度",
                        0,
                        100,
                        int(
                            reward.get(
                                "satisfaction",
                                50,
                            )
                        ),
                        5,
                        key=(
                            "edit_satisfaction_"
                            + reward_id
                        ),
                    )

                with col2:
                    edit_date = st.date_input(
                        "記録日",
                        value=parse_date(
                            reward.get(
                                "record_date",
                                "",
                            )
                        ),
                        key=(
                            "edit_date_"
                            + reward_id
                        ),
                    )

                    edit_recovery = st.slider(
                        "回復度",
                        0,
                        100,
                        int(
                            reward.get(
                                "recovery",
                                50,
                            )
                        ),
                        5,
                        key=(
                            "edit_recovery_"
                            + reward_id
                        ),
                    )

                edit_memo = st.text_area(
                    "ひとこと",
                    value=reward.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + reward_id
                    ),
                )

                edit_favorite = st.checkbox(
                    "⭐ お気に入り",
                    value=reward.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "edit_favorite_"
                        + reward_id
                    ),
                )

                button_col1, button_col2 = (
                    st.columns(2)
                )

                with button_col1:
                    if st.button(
                        "💾 変更を保存",
                        key=(
                            "save_"
                            + reward_id
                        ),
                        use_container_width=True,
                    ):
                        if (
                            edit_effort.strip()
                            and edit_reward.strip()
                        ):
                            update_reward(
                                data,
                                reward_id,
                                edit_effort.strip(),
                                edit_reward.strip(),
                                edit_category,
                                edit_satisfaction,
                                edit_recovery,
                                edit_memo.strip(),
                                edit_favorite,
                                edit_date,
                            )

                            st.rerun()

                        else:
                            st.warning(
                                "頑張ったことと"
                                "ごほうびを入力してね。"
                            )

                with button_col2:
                    if st.button(
                        "🗑️ 削除",
                        key=(
                            "delete_"
                            + reward_id
                        ),
                        use_container_width=True,
                    ):
                        delete_reward(
                            data,
                            reward_id,
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
            "today_reward_"
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
    "頑張った自分に、ちゃんと回復する時間を。🎁🌿"
)
