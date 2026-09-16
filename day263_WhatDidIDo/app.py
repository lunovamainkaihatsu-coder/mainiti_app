import json
import os
import uuid
from datetime import date, datetime, time

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今なにした？",
    page_icon="⏱️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "activity_log.json",
)

CATEGORIES = [
    "☕ 食事",
    "📚 勉強",
    "💻 AI・開発",
    "💼 仕事",
    "🏠 家事",
    "🚗 移動",
    "💪 運動",
    "😴 休憩・睡眠",
    "🎮 趣味・ゲーム",
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
        "activities": []
    }


def parse_date(text):
    try:
        return datetime.strptime(
            text,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def parse_time(text):
    try:
        return datetime.strptime(
            text,
            "%H:%M",
        ).time()

    except (ValueError, TypeError):
        return datetime.now().time().replace(
            second=0,
            microsecond=0,
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

    weekday = weekdays[
        target.weekday()
    ]

    return (
        f"{target.year}年"
        f"{target.month}月"
        f"{target.day}日"
        f"（{weekday}）"
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
            "activities",
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
                "title",
                "",
            )

            activity.setdefault(
                "category",
                "✨ その他",
            )

            activity.setdefault(
                "memo",
                "",
            )

            activity.setdefault(
                "record_date",
                str(date.today()),
            )

            activity.setdefault(
                "record_time",
                datetime.now().strftime(
                    "%H:%M"
                ),
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

def get_activity_by_id(
    data,
    activity_id,
):
    return next(
        (
            activity
            for activity
            in data["activities"]
            if activity.get(
                "id"
            ) == activity_id
        ),
        None,
    )


def add_activity(
    data,
    title,
    category,
    memo,
    record_date,
    record_time,
):
    data["activities"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "memo": memo,
            "record_date": str(
                record_date
            ),
            "record_time": (
                record_time.strftime(
                    "%H:%M"
                )
            ),
            "favorite": False,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_activity(
    data,
    activity_id,
    title,
    category,
    memo,
    record_date,
    record_time,
    favorite,
):
    activity = get_activity_by_id(
        data,
        activity_id,
    )

    if not activity:
        return

    activity["title"] = title

    activity["category"] = (
        category
    )

    activity["memo"] = memo

    activity["record_date"] = str(
        record_date
    )

    activity["record_time"] = (
        record_time.strftime(
            "%H:%M"
        )
    )

    activity["favorite"] = bool(
        favorite
    )

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
        if activity.get(
            "id"
        ) != activity_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    activity_id,
):
    activity = get_activity_by_id(
        data,
        activity_id,
    )

    if not activity:
        return

    activity["favorite"] = not (
        activity.get(
            "favorite",
            False,
        )
    )

    activity["updated_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# 集計関数
# =========================================================

def activities_for_date(
    activities,
    target_date,
):
    target_text = str(
        target_date
    )

    return [
        activity
        for activity in activities
        if activity.get(
            "record_date"
        ) == target_text
    ]


def activities_for_month(
    activities,
    month_text,
):
    return [
        activity
        for activity in activities
        if activity.get(
            "record_date",
            "",
        ).startswith(
            month_text
        )
    ]


def most_common_category(
    activities,
):
    if not activities:
        return None, 0

    counts = {}

    for activity in activities:
        category = activity.get(
            "category",
            "✨ その他",
        )

        counts[category] = (
            counts.get(
                category,
                0,
            )
            + 1
        )

    category = max(
        counts,
        key=counts.get,
    )

    return (
        category,
        counts[category],
    )


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
            rgba(80, 160, 255, 0.07);
        border:
            1px solid
            rgba(80, 160, 255, 0.15);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 160, 255, 0.16),
                rgba(100, 220, 180, 0.10)
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

    .timeline-time {
        font-size: 1.35rem;
        font-weight: 900;
    }

    .timeline-line {
        margin-left: 21px;
        height: 20px;
        border-left:
            2px solid
            rgba(120, 120, 120, 0.25);
    }

    .quick-box {
        padding: 20px;
        border-radius: 20px;
        margin-top: 12px;
        margin-bottom: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 80, 0.10),
                rgba(80, 160, 255, 0.07)
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

activities = data[
    "activities"
]

today = date.today()

today_activities = (
    activities_for_date(
        activities,
        today,
    )
)

today_activities = sorted(
    today_activities,
    key=lambda activity: (
        activity.get(
            "record_time",
            "00:00",
        )
    ),
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>⏱️ 今なにした？</h1>

        <p>
            予定ではなく、
            実際に過ごした一日を残す。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日のダッシュボード
# =========================================================

common_category, common_count = (
    most_common_category(
        today_activities
    )
)

first_time = (
    today_activities[0].get(
        "record_time",
        "-"
    )
    if today_activities
    else "-"
)

latest_time = (
    today_activities[-1].get(
        "record_time",
        "-"
    )
    if today_activities
    else "-"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📝 今日の記録",
    f"{len(today_activities)}件",
)

col2.metric(
    "🔥 一番多い活動",
    (
        common_category
        if common_category
        else "-"
    ),
    (
        f"{common_count}回"
        if common_category
        else None
    ),
)

col3.metric(
    "🌅 最初の記録",
    first_time,
)

col4.metric(
    "🌙 最新の記録",
    latest_time,
)


# =========================================================
# クイック記録
# =========================================================

st.divider()

st.subheader(
    "➕ 今やったことを記録"
)

current_time = (
    datetime.now()
    .time()
    .replace(
        second=0,
        microsecond=0,
    )
)

with st.form(
    "new_activity_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "今なにした？",
        placeholder=(
            "例：AIの勉強をした"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        record_date = st.date_input(
            "日付",
            value=date.today(),
        )

    with col2:
        record_time = st.time_input(
            "時刻",
            value=current_time,
        )

        memo = st.text_input(
            "メモ（任意）",
            placeholder=(
                "例：強化学習の続きを読んだ"
            ),
        )

    submitted = (
        st.form_submit_button(
            "＋ 記録する",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "やったことを入力してね。"
            )

        else:
            add_activity(
                data,
                title.strip(),
                category,
                memo.strip(),
                record_date,
                record_time,
            )

            st.rerun()


# =========================================================
# 今日のタイムライン
# =========================================================

st.divider()

st.subheader(
    "📅 今日のタイムライン"
)

if not today_activities:
    st.info(
        "今日の記録はまだありません。"
    )

else:
    for index, activity in enumerate(
        today_activities
    ):
        activity_id = activity.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2, col3 = (
                st.columns(
                    [1, 5, 1]
                )
            )

            with col1:
                st.markdown(
                    f"### "
                    f"{activity.get('record_time', '')}"
                )

            with col2:
                st.markdown(
                    f"**{activity.get('category', '✨ その他')}**"
                )

                st.write(
                    activity.get(
                        "title",
                        "",
                    )
                )

                if activity.get(
                    "memo",
                    "",
                ):
                    st.caption(
                        "💬 "
                        + activity.get(
                            "memo",
                            "",
                        )
                    )

            with col3:
                favorite_icon = (
                    "⭐"
                    if activity.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    favorite_icon,
                    key=(
                        "today_fav_"
                        + activity_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        activity_id,
                    )

                    st.rerun()

        if (
            index
            < len(today_activities) - 1
        ):
            st.markdown(
                """
                <div class="timeline-line">
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# 今日のカテゴリー分析
# =========================================================

if today_activities:
    st.divider()

    st.subheader(
        "📊 今日の活動"
    )

    category_rows = []

    for activity in today_activities:
        category_rows.append(
            {
                "カテゴリー": (
                    activity.get(
                        "category",
                        "✨ その他",
                    )
                )
            }
        )

    category_df = pd.DataFrame(
        category_rows
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

    st.caption(
        "※ 記録回数のグラフです。"
        "実際に使った時間の長さではありません。"
    )


# =========================================================
# 日別記録数
# =========================================================

if activities:
    st.divider()

    st.subheader(
        "📈 最近の記録数"
    )

    daily_rows = []

    for activity in activities:
        daily_rows.append(
            {
                "日付": activity.get(
                    "record_date",
                    "",
                )
            }
        )

    daily_df = pd.DataFrame(
        daily_rows
    )

    daily_count = (
        daily_df[
            "日付"
        ]
        .value_counts()
        .rename_axis(
            "日付"
        )
        .reset_index(
            name="記録数"
        )
        .sort_values(
            "日付"
        )
    )

    daily_count = (
        daily_count.tail(30)
    )

    st.line_chart(
        daily_count.set_index(
            "日付"
        )
    )

    st.caption(
        "直近30日分の記録数を表示します。"
    )


# =========================================================
# 月間カテゴリー
# =========================================================

current_month = (
    today.strftime(
        "%Y-%m"
    )
)

month_activities = (
    activities_for_month(
        activities,
        current_month,
    )
)

if month_activities:
    st.divider()

    st.subheader(
        "🗓️ 今月よく記録した活動"
    )

    month_rows = []

    for activity in month_activities:
        month_rows.append(
            {
                "カテゴリー": (
                    activity.get(
                        "category",
                        "✨ その他",
                    )
                )
            }
        )

    month_df = pd.DataFrame(
        month_rows
    )

    month_category_count = (
        month_df[
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

    st.dataframe(
        month_category_count,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# お気に入り
# =========================================================

favorite_activities = [
    activity
    for activity in activities
    if activity.get(
        "favorite",
        False,
    )
]

if favorite_activities:
    st.divider()

    st.subheader(
        "⭐ 残しておきたい行動"
    )

    favorites = sorted(
        favorite_activities,
        key=lambda activity: (
            activity.get(
                "record_date",
                "",
            ),
            activity.get(
                "record_time",
                "",
            ),
        ),
        reverse=True,
    )

    for activity in favorites[:5]:
        with st.container(
            border=True
        ):
            st.markdown(
                f"**{activity.get('category', '✨ その他')} "
                f"{activity.get('title', '')}**"
            )

            st.caption(
                f"{activity.get('record_date', '')} "
                f"{activity.get('record_time', '')}"
            )

            if activity.get(
                "memo",
                "",
            ):
                st.write(
                    activity.get(
                        "memo",
                        "",
                    )
                )


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
        "やったこと・メモから検索"
    ),
)

col1, col2, col3 = st.columns(3)

with col1:
    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="history_category",
    )

with col2:
    date_filter = st.date_input(
        "日付",
        value=None,
        key="history_date",
    )

with col3:
    favorite_filter = st.selectbox(
        "表示",
        [
            "すべて",
            "⭐ お気に入りのみ",
        ],
    )


filtered_activities = []

for activity in activities:
    if (
        category_filter != "すべて"
        and activity.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        date_filter is not None
        and activity.get(
            "record_date"
        ) != str(date_filter)
    ):
        continue

    if (
        favorite_filter
        == "⭐ お気に入りのみ"
        and not activity.get(
            "favorite",
            False,
        )
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                activity.get(
                    "title",
                    "",
                ),
                activity.get(
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

    filtered_activities.append(
        activity
    )


filtered_activities = sorted(
    filtered_activities,
    key=lambda activity: (
        activity.get(
            "record_date",
            "",
        ),
        activity.get(
            "record_time",
            "",
        ),
    ),
    reverse=True,
)


if not filtered_activities:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    history_rows = []

    for activity in (
        filtered_activities
    ):
        history_rows.append(
            {
                "日付": activity.get(
                    "record_date",
                    "",
                ),
                "時刻": activity.get(
                    "record_time",
                    "",
                ),
                "カテゴリー": (
                    activity.get(
                        "category",
                        "",
                    )
                ),
                "やったこと": (
                    activity.get(
                        "title",
                        "",
                    )
                ),
                "メモ": activity.get(
                    "memo",
                    "",
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
    edit_activities = sorted(
        activities,
        key=lambda activity: (
            activity.get(
                "record_date",
                "",
            ),
            activity.get(
                "record_time",
                "",
            ),
        ),
        reverse=True,
    )

    if not edit_activities:
        st.caption(
            "まだ記録がありません。"
        )

    for activity in edit_activities:
        activity_id = activity.get(
            "id",
            "",
        )

        title_text = (
            f"{activity.get('record_date', '')} "
            f"{activity.get('record_time', '')}"
            f" ｜ "
            f"{activity.get('title', '')[:25]}"
        )

        with st.expander(
            title_text
        ):
            edit_title = st.text_input(
                "やったこと",
                value=activity.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + activity_id
                ),
            )

            current_category = (
                activity.get(
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
                        + activity_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                edit_date = (
                    st.date_input(
                        "日付",
                        value=parse_date(
                            activity.get(
                                "record_date",
                                "",
                            )
                        ),
                        key=(
                            "edit_date_"
                            + activity_id
                        ),
                    )
                )

            with col2:
                edit_time = (
                    st.time_input(
                        "時刻",
                        value=parse_time(
                            activity.get(
                                "record_time",
                                "",
                            )
                        ),
                        key=(
                            "edit_time_"
                            + activity_id
                        ),
                    )
                )

            edit_memo = st.text_area(
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

            edit_favorite = (
                st.checkbox(
                    "⭐ お気に入り",
                    value=activity.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "edit_favorite_"
                        + activity_id
                    ),
                )
            )

            button_col1, button_col2 = (
                st.columns(2)
            )

            with button_col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + activity_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.warning(
                            "やったことを"
                            "入力してね。"
                        )

                    else:
                        update_activity(
                            data,
                            activity_id,
                            edit_title.strip(),
                            edit_category,
                            edit_memo.strip(),
                            edit_date,
                            edit_time,
                            edit_favorite,
                        )

                        st.rerun()

            with button_col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_"
                        + activity_id
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
            "activity_log_"
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
    "予定ではなく、実際に過ごした一日を残す。⏱️📖✨"
)
