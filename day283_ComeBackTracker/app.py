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
    page_title="最近これやってない！",
    page_icon="🌱",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "activities.json",
)

CATEGORIES = [
    "📚 勉強",
    "🏃 運動",
    "🎨 創作",
    "🧘 心・休息",
    "👥 人付き合い",
    "🏠 生活",
    "🎮 趣味",
    "💻 開発",
    "✨ その他",
]

FEELINGS = [
    "😄 最高だった",
    "😊 楽しかった",
    "😌 普通",
    "😣 ちょっと大変",
    "😵 かなり大変",
]

FEELING_SCORES = {
    "😄 最高だった": 5,
    "😊 楽しかった": 4,
    "😌 普通": 3,
    "😣 ちょっと大変": 2,
    "😵 かなり大変": 1,
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


def today_text():
    return str(date.today())


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()
    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d"
    )


def days_since(value):
    parsed = parse_date(value)

    if not parsed:
        return 0

    return max(
        (date.today() - parsed).days,
        0,
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


def get_feeling_score(feeling):
    return FEELING_SCORES.get(
        feeling,
        0,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "activities": [],
        "history": [],
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
            "activities",
            [],
        )

        data.setdefault(
            "history",
            [],
        )

        for activity in data[
            "activities"
        ]:
            activity.setdefault(
                "id",
                create_id(),
            )

            activity.setdefault(
                "name",
                "",
            )

            activity.setdefault(
                "category",
                "✨ その他",
            )

            activity.setdefault(
                "threshold_days",
                7,
            )

            activity.setdefault(
                "last_done_date",
                today_text(),
            )

            activity.setdefault(
                "status",
                "active",
            )

            activity.setdefault(
                "memo",
                "",
            )

            activity.setdefault(
                "favorite",
                False,
            )

            activity.setdefault(
                "created_at",
                now_text(),
            )

            activity.setdefault(
                "updated_at",
                activity.get(
                    "created_at",
                    now_text(),
                ),
            )

        for item in data[
            "history"
        ]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "activity_id",
                "",
            )

            item.setdefault(
                "done_date",
                today_text(),
            )

            item.setdefault(
                "gap_days",
                0,
            )

            item.setdefault(
                "is_comeback",
                False,
            )

            item.setdefault(
                "feeling",
                "😌 普通",
            )

            item.setdefault(
                "comment",
                "",
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
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# CRUD
# =========================================================

def get_activity(
    data,
    activity_id,
):
    return next(
        (
            activity
            for activity
            in data["activities"]
            if activity.get("id")
            == activity_id
        ),
        None,
    )


def add_activity(
    data,
    name,
    category,
    last_done_date,
    threshold_days,
    memo,
):
    activity = {
        "id": create_id(),
        "name": name,
        "category": category,
        "last_done_date": str(
            last_done_date
        ),
        "threshold_days": int(
            threshold_days
        ),
        "status": "active",
        "memo": memo,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["activities"].append(
        activity
    )

    save_data(data)

    return activity["id"]


def update_activity(
    data,
    activity_id,
    name,
    category,
    last_done_date,
    threshold_days,
    memo,
):
    activity = get_activity(
        data,
        activity_id,
    )

    if not activity:
        return

    activity["name"] = name
    activity["category"] = category
    activity["last_done_date"] = str(
        last_done_date
    )
    activity["threshold_days"] = int(
        threshold_days
    )
    activity["memo"] = memo
    activity["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    activity_id,
):
    activity = get_activity(
        data,
        activity_id,
    )

    if not activity:
        return

    activity["favorite"] = (
        not activity.get(
            "favorite",
            False,
        )
    )

    activity["updated_at"] = (
        now_text()
    )

    save_data(data)


def pause_activity(
    data,
    activity_id,
):
    activity = get_activity(
        data,
        activity_id,
    )

    if not activity:
        return

    activity["status"] = "paused"
    activity["updated_at"] = (
        now_text()
    )

    save_data(data)


def resume_activity(
    data,
    activity_id,
):
    activity = get_activity(
        data,
        activity_id,
    )

    if not activity:
        return

    activity["status"] = "active"
    activity["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_activity(
    data,
    activity_id,
):
    data["activities"] = [
        activity
        for activity
        in data["activities"]
        if activity.get("id")
        != activity_id
    ]

    data["history"] = [
        item
        for item
        in data["history"]
        if item.get("activity_id")
        != activity_id
    ]

    save_data(data)


def record_activity(
    data,
    activity_id,
    feeling,
    comment,
):
    activity = get_activity(
        data,
        activity_id,
    )

    if not activity:
        return None

    previous_date = parse_date(
        activity.get(
            "last_done_date"
        )
    )

    today = date.today()

    if previous_date:
        gap_days = max(
            (
                today
                - previous_date
            ).days,
            0,
        )
    else:
        gap_days = 0

    threshold = int(
        activity.get(
            "threshold_days",
            7,
        )
    )

    is_comeback = (
        gap_days >= threshold
    )

    history_item = {
        "id": create_id(),
        "activity_id": (
            activity_id
        ),
        "done_date": today_text(),
        "gap_days": gap_days,
        "is_comeback": is_comeback,
        "feeling": feeling,
        "comment": comment,
        "created_at": now_text(),
    }

    data["history"].append(
        history_item
    )

    activity[
        "last_done_date"
    ] = today_text()

    activity[
        "updated_at"
    ] = now_text()

    save_data(data)

    return history_item


def delete_history_item(
    data,
    history_id,
):
    data["history"] = [
        item
        for item in data["history"]
        if item.get("id")
        != history_id
    ]

    save_data(data)


# =========================================================
# 集計
# =========================================================

def activity_history(
    data,
    activity_id,
):
    return [
        item
        for item in data["history"]
        if item.get(
            "activity_id"
        )
        == activity_id
    ]


def comeback_history(
    data,
    activity_id=None,
):
    items = [
        item
        for item in data["history"]
        if item.get(
            "is_comeback",
            False,
        )
    ]

    if activity_id:
        items = [
            item
            for item in items
            if item.get(
                "activity_id"
            )
            == activity_id
        ]

    return items


def activity_stats(
    data,
    activity_id,
):
    history = activity_history(
        data,
        activity_id,
    )

    comebacks = [
        item
        for item in history
        if item.get(
            "is_comeback",
            False,
        )
    ]

    comeback_gaps = [
        int(
            item.get(
                "gap_days",
                0,
            )
        )
        for item in comebacks
    ]

    comeback_scores = [
        get_feeling_score(
            item.get(
                "feeling",
                "",
            )
        )
        for item in comebacks
        if get_feeling_score(
            item.get(
                "feeling",
                "",
            )
        )
        > 0
    ]

    return {
        "records": len(history),
        "comebacks": len(
            comebacks
        ),
        "max_gap": (
            max(comeback_gaps)
            if comeback_gaps
            else 0
        ),
        "avg_gap": (
            average(
                comeback_gaps
            )
            if comeback_gaps
            else 0
        ),
        "avg_feeling": (
            average(
                comeback_scores
            )
            if comeback_scores
            else 0
        ),
    }


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
        background: rgba(70, 180, 120, 0.07);
        border: 1px solid rgba(70, 180, 120, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 190, 120, 0.20),
                rgba(90, 150, 220, 0.08)
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

    .gap-number {
        font-size: 2.7rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 8px 0;
    }

    .soft-text {
        opacity: 0.72;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

activities = data[
    "activities"
]

history = data[
    "history"
]

active_activities = [
    activity
    for activity in activities
    if activity.get(
        "status",
        "active",
    )
    == "active"
]

paused_activities = [
    activity
    for activity in activities
    if activity.get(
        "status"
    )
    == "paused"
]

due_activities = [
    activity
    for activity
    in active_activities
    if days_since(
        activity.get(
            "last_done_date"
        )
    )
    >= int(
        activity.get(
            "threshold_days",
            7,
        )
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>👀 最近これやってない！</h1>
        <p>
            途切れたことより、
            戻ってきたことを数えよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

all_comebacks = comeback_history(
    data
)

max_comeback_gap = max(
    [
        int(
            item.get(
                "gap_days",
                0,
            )
        )
        for item in all_comebacks
    ],
    default=0,
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌱 継続中",
    f"{len(active_activities)}個",
)

col2.metric(
    "👀 そろそろ",
    f"{len(due_activities)}個",
)

col3.metric(
    "🎉 復活",
    f"{len(all_comebacks)}回",
)

col4.metric(
    "🏆 最大ブランク",
    (
        f"{max_comeback_gap}日"
        if all_comebacks
        else "-"
    ),
)


# =========================================================
# 登録直後のメッセージ
# =========================================================

last_result = (
    st.session_state.pop(
        "last_comeback_result",
        None,
    )
)

if last_result:
    if last_result.get(
        "is_comeback"
    ):
        st.success(
            "🎉 おかえり！ "
            f"{last_result.get('gap_days', 0)}日ぶりに"
            "戻ってきました！"
        )
    else:
        st.success(
            "🌱 今日の記録を残しました！"
        )


# =========================================================
# 活動登録
# =========================================================

st.divider()

st.subheader(
    "🌱 続けたいことを登録"
)

with st.form(
    "new_activity_form",
    clear_on_submit=True,
):
    name = st.text_input(
        "🌱 続けたいこと",
        placeholder=(
            "例：絵を描く"
        ),
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        category = (
            st.selectbox(
                "🏷️ カテゴリー",
                CATEGORIES,
            )
        )

        last_done_date = (
            st.date_input(
                "📅 最近やった日",
                value=date.today(),
                max_value=date.today(),
            )
        )

    with col2:
        threshold_days = (
            st.number_input(
                "👀 何日空いたら気にする？",
                min_value=1,
                max_value=3650,
                value=7,
                step=1,
            )
        )

        st.caption(
            "この日数以上空いてから"
            "再開すると「復活」になります。"
        )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "例：週1くらいでも"
            "続けていきたい"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🌱 登録する",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not name.strip():
            st.warning(
                "活動名を入力してね。"
            )

        else:
            add_activity(
                data=data,
                name=name.strip(),
                category=category,
                last_done_date=(
                    last_done_date
                ),
                threshold_days=(
                    threshold_days
                ),
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# そろそろどう？
# =========================================================

st.divider()

st.subheader(
    "👀 そろそろどう？"
)

st.caption(
    "やらなきゃ、ではなく"
    "「そろそろ戻ってみる？」くらいで。"
)

if not due_activities:
    st.success(
        "🌿 今は「そろそろ」の活動はありません。"
    )

else:
    due_sorted = sorted(
        due_activities,
        key=lambda item: (
            days_since(
                item.get(
                    "last_done_date"
                )
            )
        ),
        reverse=True,
    )

    for activity in due_sorted:
        activity_id = (
            activity.get(
                "id",
                "",
            )
        )

        gap = days_since(
            activity.get(
                "last_done_date"
            )
        )

        stats = activity_stats(
            data,
            activity_id,
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [7, 1]
                )
            )

            with col1:
                st.subheader(
                    activity.get(
                        "name",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if activity.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "due_favorite_"
                        + activity_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        activity_id,
                    )
                    st.rerun()

            st.caption(
                activity.get(
                    "category",
                    "",
                )
                + " ｜ 最後："
                + format_date(
                    activity.get(
                        "last_done_date"
                    )
                )
            )

            st.markdown(
                f"""
                <div class="gap-number">
                    {gap}日ぶり
                </div>
                <div class="soft-text">
                    また戻れるチャンス。
                </div>
                """,
                unsafe_allow_html=True,
            )

            if stats["comebacks"]:
                st.write(
                    f"🌱 これまで"
                    f" **{stats['comebacks']}回**"
                    " 戻ってきています。"
                )

            with st.expander(
                "🌱 今日やった！"
            ):
                feeling = (
                    st.selectbox(
                        "今日どうだった？",
                        FEELINGS,
                        index=1,
                        key=(
                            "due_feeling_"
                            + activity_id
                        ),
                    )
                )

                comment = (
                    st.text_area(
                        "ひとこと",
                        key=(
                            "due_comment_"
                            + activity_id
                        ),
                        placeholder=(
                            "例：久しぶりだけど"
                            "意外とできた"
                        ),
                    )
                )

                if st.button(
                    "🎉 今日やった！",
                    key=(
                        "due_done_"
                        + activity_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    result = (
                        record_activity(
                            data,
                            activity_id,
                            feeling,
                            comment.strip(),
                        )
                    )

                    st.session_state[
                        "last_comeback_result"
                    ] = result

                    st.rerun()

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                st.caption(
                    "💤 今日は戻らなくてもOK。"
                )

            with col2:
                if st.button(
                    "👋 今は休止する",
                    key=(
                        "pause_due_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    pause_activity(
                        data,
                        activity_id,
                    )
                    st.rerun()


# =========================================================
# 今日戻るなら？
# =========================================================

if due_activities:
    st.divider()

    st.subheader(
        "🎲 今日ひとつ戻るなら？"
    )

    valid_ids = [
        activity.get("id")
        for activity in due_activities
    ]

    random_id = (
        st.session_state.get(
            "random_return_id"
        )
    )

    if (
        not random_id
        or random_id
        not in valid_ids
    ):
        random_id = random.choice(
            valid_ids
        )

        st.session_state[
            "random_return_id"
        ] = random_id

    candidate = get_activity(
        data,
        random_id,
    )

    if candidate:
        with st.container(
            border=True
        ):
            st.subheader(
                candidate.get(
                    "name",
                    "",
                )
            )

            candidate_gap = (
                days_since(
                    candidate.get(
                        "last_done_date"
                    )
                )
            )

            st.metric(
                "最後にやってから",
                f"{candidate_gap}日",
            )

            st.write(
                "🌱 **まず5分だけでもOK。**"
            )

        if st.button(
            "🎲 別の候補を見る",
            use_container_width=True,
        ):
            if len(valid_ids) > 1:
                alternatives = [
                    item
                    for item
                    in valid_ids
                    if item
                    != random_id
                ]

                st.session_state[
                    "random_return_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 継続中の活動
# =========================================================

st.divider()

st.subheader(
    "🌿 継続中"
)

if not active_activities:
    st.info(
        "継続中の活動はありません。"
    )

else:
    for activity in sorted(
        active_activities,
        key=lambda item: (
            days_since(
                item.get(
                    "last_done_date"
                )
            )
        ),
        reverse=True,
    ):
        activity_id = (
            activity.get(
                "id",
                "",
            )
        )

        gap = days_since(
            activity.get(
                "last_done_date"
            )
        )

        threshold = int(
            activity.get(
                "threshold_days",
                7,
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                activity.get(
                    "name",
                    "",
                )
            )

            st.caption(
                activity.get(
                    "category",
                    "",
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "最後",
                (
                    "今日"
                    if gap == 0
                    else f"{gap}日前"
                ),
            )

            col2.metric(
                "そろそろ",
                f"{threshold}日",
            )

            stats = activity_stats(
                data,
                activity_id,
            )

            col3.metric(
                "🌱 復活",
                f"{stats['comebacks']}回",
            )

            if gap < threshold:
                remaining = (
                    threshold - gap
                )

                st.progress(
                    min(
                        gap / threshold,
                        1.0,
                    )
                )

                st.caption(
                    f"「そろそろ」まで"
                    f"あと{remaining}日"
                )

            with st.expander(
                "🌱 今日やった"
            ):
                feeling = (
                    st.selectbox(
                        "今日どうだった？",
                        FEELINGS,
                        index=1,
                        key=(
                            "active_feeling_"
                            + activity_id
                        ),
                    )
                )

                comment = (
                    st.text_area(
                        "ひとこと",
                        key=(
                            "active_comment_"
                            + activity_id
                        ),
                    )
                )

                if st.button(
                    "🌱 記録する",
                    key=(
                        "active_done_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    result = (
                        record_activity(
                            data,
                            activity_id,
                            feeling,
                            comment.strip(),
                        )
                    )

                    st.session_state[
                        "last_comeback_result"
                    ] = result

                    st.rerun()


# =========================================================
# 復活ランキング
# =========================================================

if all_comebacks:
    st.divider()

    st.subheader(
        "🏆 復活記録"
    )

    ranking = []

    for activity in activities:
        stats = activity_stats(
            data,
            activity.get(
                "id"
            ),
        )

        if stats["comebacks"] > 0:
            ranking.append(
                {
                    "活動": (
                        activity.get(
                            "name",
                            "",
                        )
                    ),
                    "復活回数": (
                        stats[
                            "comebacks"
                        ]
                    ),
                    "最大ブランク": (
                        stats[
                            "max_gap"
                        ]
                    ),
                    "平均ブランク": (
                        stats[
                            "avg_gap"
                        ]
                    ),
                    "満足度": (
                        stats[
                            "avg_feeling"
                        ]
                    ),
                }
            )

    ranking_df = pd.DataFrame(
        ranking
    ).sort_values(
        [
            "復活回数",
            "最大ブランク",
        ],
        ascending=False,
    )

    st.dataframe(
        ranking_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "復活回数": st.column_config.NumberColumn(
                "🌱 復活回数",
                format="%d回",
            ),
            "最大ブランク": st.column_config.NumberColumn(
                "🏆 最大ブランク",
                format="%d日",
            ),
            "平均ブランク": st.column_config.NumberColumn(
                "📅 平均ブランク",
                format="%.1f日",
            ),
            "満足度": st.column_config.NumberColumn(
                "😊 復活後満足度",
                format="%.1f / 5",
            ),
        },
    )


# =========================================================
# 月間分析
# =========================================================

st.divider()

current_month = date.today().strftime(
    "%Y-%m"
)

month_history = [
    item
    for item in history
    if (
        item.get(
            "done_date",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]

month_comebacks = [
    item
    for item in month_history
    if item.get(
        "is_comeback",
        False,
    )
]

month_normal = [
    item
    for item in month_history
    if not item.get(
        "is_comeback",
        False,
    )
]

month_scores = [
    get_feeling_score(
        item.get(
            "feeling",
            "",
        )
    )
    for item in month_history
    if get_feeling_score(
        item.get(
            "feeling",
            "",
        )
    )
    > 0
]

month_max_gap = max(
    [
        int(
            item.get(
                "gap_days",
                0,
            )
        )
        for item in month_comebacks
    ],
    default=0,
)

st.subheader(
    f"📊 {date.today().month}月の「おかえり」"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌱 復活",
    f"{len(month_comebacks)}回",
)

col2.metric(
    "✅ 普通の記録",
    f"{len(month_normal)}回",
)

col3.metric(
    "🏆 最大ブランク",
    (
        f"{month_max_gap}日"
        if month_comebacks
        else "-"
    ),
)

col4.metric(
    "😊 平均満足度",
    (
        f"{average(month_scores):.1f} / 5"
        if month_scores
        else "-"
    ),
)


# =========================================================
# 今月最大の復活
# =========================================================

if month_comebacks:
    biggest = max(
        month_comebacks,
        key=lambda item: int(
            item.get(
                "gap_days",
                0,
            )
        ),
    )

    biggest_activity = (
        get_activity(
            data,
            biggest.get(
                "activity_id"
            ),
        )
    )

    if biggest_activity:
        st.success(
            "🏆 今月最大の復活："
            f"「{biggest_activity.get('name', '')}」"
            f" {biggest.get('gap_days', 0)}日ぶり！"
        )


# =========================================================
# 復活カテゴリー
# =========================================================

if all_comebacks:
    st.markdown(
        "### 🌱 復活しやすいカテゴリー"
    )

    category_counts = {}

    for item in all_comebacks:
        activity = get_activity(
            data,
            item.get(
                "activity_id"
            ),
        )

        if not activity:
            continue

        category = activity.get(
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

    if category_counts:
        category_df = (
            pd.DataFrame(
                [
                    {
                        "カテゴリー": category,
                        "復活回数": count,
                    }
                    for category, count
                    in category_counts.items()
                ]
            )
            .sort_values(
                "復活回数",
                ascending=False,
            )
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 復活曜日
# =========================================================

if all_comebacks:
    st.markdown(
        "### 📅 戻ってきた曜日"
    )

    weekday_names = [
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日",
    ]

    weekday_counts = {
        weekday: 0
        for weekday
        in weekday_names
    }

    for item in all_comebacks:
        done_date = parse_date(
            item.get(
                "done_date"
            )
        )

        if not done_date:
            continue

        weekday = weekday_names[
            done_date.weekday()
        ]

        weekday_counts[
            weekday
        ] += 1

    weekday_df = pd.DataFrame(
        [
            {
                "曜日": weekday,
                "復活回数": (
                    weekday_counts[
                        weekday
                    ]
                ),
            }
            for weekday
            in weekday_names
        ]
    )

    st.bar_chart(
        weekday_df.set_index(
            "曜日"
        )
    )


# =========================================================
# 大切な活動
# =========================================================

favorites = [
    activity
    for activity in activities
    if activity.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 大切な活動"
    )

    for activity in favorites:
        stats = activity_stats(
            data,
            activity.get(
                "id"
            ),
        )

        with st.container(
            border=True
        ):
            st.subheader(
                activity.get(
                    "name",
                    "",
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "🌱 復活",
                f"{stats['comebacks']}回",
            )

            col2.metric(
                "🏆 最大ブランク",
                (
                    f"{stats['max_gap']}日"
                    if stats[
                        "comebacks"
                    ]
                    else "-"
                ),
            )


# =========================================================
# 休眠中
# =========================================================

if paused_activities:
    st.divider()

    st.subheader(
        "😴 休眠中"
    )

    st.caption(
        "今は休んでいてOK。"
        "またやりたくなったら戻せます。"
    )

    for activity in (
        paused_activities
    ):
        activity_id = (
            activity.get(
                "id",
                "",
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                activity.get(
                    "name",
                    "",
                )
            )

            st.caption(
                activity.get(
                    "category",
                    "",
                )
            )

            st.write(
                f"最後："
                f"{format_date(activity.get('last_done_date'))}"
            )

            if st.button(
                "🌱 また始める",
                key=(
                    "resume_"
                    + activity_id
                ),
                use_container_width=True,
            ):
                resume_activity(
                    data,
                    activity_id,
                )

                st.rerun()


# =========================================================
# 活動図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 活動図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "読書、運動、絵……"
    ),
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
                "🌱 継続中",
                "😴 休眠中",
                "👀 そろそろ",
            ],
            key=(
                "library_status"
            ),
        )
    )


filtered_activities = []

for activity in activities:
    if (
        category_filter
        != "すべて"
        and activity.get(
            "category"
        )
        != category_filter
    ):
        continue

    status = activity.get(
        "status",
        "active",
    )

    gap = days_since(
        activity.get(
            "last_done_date"
        )
    )

    threshold = int(
        activity.get(
            "threshold_days",
            7,
        )
    )

    if (
        status_filter
        == "🌱 継続中"
        and status
        != "active"
    ):
        continue

    if (
        status_filter
        == "😴 休眠中"
        and status
        != "paused"
    ):
        continue

    if (
        status_filter
        == "👀 そろそろ"
        and (
            status
            != "active"
            or gap
            < threshold
        )
    ):
        continue

    searchable = " ".join(
        [
            activity.get(
                "name",
                "",
            ),
            activity.get(
                "category",
                "",
            ),
            activity.get(
                "memo",
                "",
            ),
        ]
    ).lower()

    if (
        search_text.strip()
        and search_text
        .strip()
        .lower()
        not in searchable
    ):
        continue

    filtered_activities.append(
        activity
    )


if not filtered_activities:
    st.info(
        "条件に合う活動はありません。"
    )

else:
    rows = []

    for activity in sorted(
        filtered_activities,
        key=lambda item: (
            days_since(
                item.get(
                    "last_done_date"
                )
            )
        ),
        reverse=True,
    ):
        stats = activity_stats(
            data,
            activity.get(
                "id"
            ),
        )

        rows.append(
            {
                "活動": (
                    activity.get(
                        "name",
                        "",
                    )
                ),
                "カテゴリー": (
                    activity.get(
                        "category",
                        "",
                    )
                ),
                "最後": (
                    f"{days_since(activity.get('last_done_date'))}日前"
                ),
                "復活": (
                    f"{stats['comebacks']}回"
                ),
                "状態": (
                    "😴 休眠中"
                    if activity.get(
                        "status"
                    )
                    == "paused"
                    else "🌱 継続中"
                ),
                "⭐": (
                    "⭐"
                    if activity.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 復活履歴
# =========================================================

if all_comebacks:
    st.divider()

    st.subheader(
        "🎉 おかえり履歴"
    )

    comeback_rows = []

    for item in sorted(
        all_comebacks,
        key=lambda row: (
            row.get(
                "done_date",
                "",
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        activity = get_activity(
            data,
            item.get(
                "activity_id"
            ),
        )

        if not activity:
            continue

        comeback_rows.append(
            {
                "日付": (
                    format_date(
                        item.get(
                            "done_date"
                        )
                    )
                ),
                "活動": (
                    activity.get(
                        "name",
                        "",
                    )
                ),
                "ブランク": (
                    f"{item.get('gap_days', 0)}日"
                ),
                "気分": (
                    item.get(
                        "feeling",
                        "",
                    )
                ),
                "ひとこと": (
                    item.get(
                        "comment",
                        "",
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            comeback_rows
        ),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・管理"
):
    if not activities:
        st.caption(
            "まだ活動がありません。"
        )

    for activity in sorted(
        activities,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        activity_id = (
            activity.get(
                "id",
                "",
            )
        )

        with st.expander(
            activity.get(
                "name",
                "",
            )
        ):
            edit_name = (
                st.text_input(
                    "活動名",
                    value=activity.get(
                        "name",
                        "",
                    ),
                    key=(
                        "edit_name_"
                        + activity_id
                    ),
                )
            )

            old_category = (
                activity.get(
                    "category",
                    "✨ その他",
                )
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
                        "edit_category_"
                        + activity_id
                    ),
                )
            )

            old_date = (
                parse_date(
                    activity.get(
                        "last_done_date"
                    )
                )
                or date.today()
            )

            edit_last_date = (
                st.date_input(
                    "最近やった日",
                    value=old_date,
                    max_value=date.today(),
                    key=(
                        "edit_date_"
                        + activity_id
                    ),
                )
            )

            edit_threshold = (
                st.number_input(
                    "何日空いたら気にする？",
                    min_value=1,
                    max_value=3650,
                    value=int(
                        activity.get(
                            "threshold_days",
                            7,
                        )
                    ),
                    key=(
                        "edit_threshold_"
                        + activity_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=activity.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + activity_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_activity_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_name.strip()
                    ):
                        st.warning(
                            "活動名を入力してね。"
                        )

                    else:
                        update_activity(
                            data=data,
                            activity_id=(
                                activity_id
                            ),
                            name=(
                                edit_name.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            last_done_date=(
                                edit_last_date
                            ),
                            threshold_days=(
                                edit_threshold
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ 大切から外す"
                    if activity.get(
                        "favorite",
                        False,
                    )
                    else "☆ 大切にする"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_fav_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        activity_id,
                    )
                    st.rerun()

            if activity.get(
                "status"
            ) == "paused":
                if st.button(
                    "🌱 再開する",
                    key=(
                        "manage_resume_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    resume_activity(
                        data,
                        activity_id,
                    )
                    st.rerun()

            else:
                if st.button(
                    "😴 休止する",
                    key=(
                        "manage_pause_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    pause_activity(
                        data,
                        activity_id,
                    )
                    st.rerun()

            item_history = sorted(
                activity_history(
                    data,
                    activity_id,
                ),
                key=lambda item: (
                    item.get(
                        "created_at",
                        "",
                    )
                ),
                reverse=True,
            )

            if item_history:
                st.markdown(
                    "#### 📜 記録履歴"
                )

                for item in (
                    item_history
                ):
                    history_id = (
                        item.get(
                            "id",
                            "",
                        )
                    )

                    col1, col2 = (
                        st.columns(
                            [6, 1]
                        )
                    )

                    with col1:
                        prefix = (
                            "🎉 復活"
                            if item.get(
                                "is_comeback",
                                False,
                            )
                            else "🌱 記録"
                        )

                        st.write(
                            f"{prefix} ｜ "
                            f"{format_date(item.get('done_date'))}"
                            f" ｜ {item.get('gap_days', 0)}日ぶり"
                        )

                        if item.get(
                            "comment"
                        ):
                            st.caption(
                                item.get(
                                    "comment",
                                    "",
                                )
                            )

                    with col2:
                        if st.button(
                            "🗑️",
                            key=(
                                "delete_history_"
                                + history_id
                            ),
                        ):
                            delete_history_item(
                                data,
                                history_id,
                            )
                            st.rerun()

            confirm_delete = (
                st.checkbox(
                    "この活動と履歴を削除する",
                    key=(
                        "confirm_delete_"
                        + activity_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_activity_"
                    + activity_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_activity(
                    data,
                    activity_id,
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
            "comeback_tracker_"
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
    "🌱 途切れたことより、"
    "戻ってきたことを数えよう。"
)
