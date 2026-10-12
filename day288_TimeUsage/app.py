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
    page_title="今日は何に時間使った？",
    page_icon="⏰",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "time_usage.json",
)

DEFAULT_CATEGORIES = [
    {
        "name": "😴 睡眠",
        "direction": "⚖️ 今くらい",
        "purpose": "🧱 必要な時間",
        "is_default": True,
    },
    {
        "name": "💼 仕事",
        "direction": "⚖️ 今くらい",
        "purpose": "🧱 必要な時間",
        "is_default": True,
    },
    {
        "name": "👨‍👩‍👧 家族",
        "direction": "⚖️ 今くらい",
        "purpose": "🤝 誰かのため",
        "is_default": True,
    },
    {
        "name": "🏠 生活・家事",
        "direction": "⚖️ 今くらい",
        "purpose": "🧱 必要な時間",
        "is_default": True,
    },
    {
        "name": "📚 学習",
        "direction": "🎯 増やしたい",
        "purpose": "🌱 自分のため",
        "is_default": True,
    },
    {
        "name": "🎨 創作・開発",
        "direction": "🎯 増やしたい",
        "purpose": "🌱 自分のため",
        "is_default": True,
    },
    {
        "name": "🏃 運動",
        "direction": "🎯 増やしたい",
        "purpose": "🌱 自分のため",
        "is_default": True,
    },
    {
        "name": "🚃 移動",
        "direction": "⚖️ 今くらい",
        "purpose": "🧱 必要な時間",
        "is_default": True,
    },
    {
        "name": "🎮 自由時間",
        "direction": "⚖️ 今くらい",
        "purpose": "🎈 自由",
        "is_default": True,
    },
    {
        "name": "📱 SNS・ネット",
        "direction": "📉 減らしたい",
        "purpose": "🎈 自由",
        "is_default": True,
    },
    {
        "name": "🍽️ 食事",
        "direction": "⚖️ 今くらい",
        "purpose": "🧱 必要な時間",
        "is_default": True,
    },
    {
        "name": "✨ その他",
        "direction": "⚖️ 今くらい",
        "purpose": "🧱 必要な時間",
        "is_default": True,
    },
]

DIRECTIONS = [
    "🎯 増やしたい",
    "📉 減らしたい",
    "⚖️ 今くらい",
]

PURPOSES = [
    "🌱 自分のため",
    "🤝 誰かのため",
    "🧱 必要な時間",
    "🎈 自由",
]

SATISFACTION_LABELS = {
    1: "★☆☆☆☆",
    2: "★★☆☆☆",
    3: "★★★☆☆",
    4: "★★★★☆",
    5: "★★★★★",
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

    return parsed.strftime("%Y/%m/%d")


def hours_text(hours):
    hours = float(hours or 0)

    if hours <= 0:
        return "0分"

    total_minutes = round(
        hours * 60
    )

    h = total_minutes // 60
    m = total_minutes % 60

    if h and m:
        return f"{h}時間{m}分"

    if h:
        return f"{h}時間"

    return f"{m}分"


def average(values):
    values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        2,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "days": [],
        "categories": [
            {
                **category,
                "id": create_id(),
            }
            for category
            in DEFAULT_CATEGORIES
        ],
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
            "days",
            [],
        )

        data.setdefault(
            "categories",
            [],
        )

        # 古い空データなどの場合は
        # デフォルトカテゴリーを復元
        if not data["categories"]:
            data["categories"] = [
                {
                    **category,
                    "id": create_id(),
                }
                for category
                in DEFAULT_CATEGORIES
            ]

        for category in data["categories"]:
            category.setdefault(
                "id",
                create_id(),
            )
            category.setdefault(
                "name",
                "✨ その他",
            )
            category.setdefault(
                "direction",
                "⚖️ 今くらい",
            )
            category.setdefault(
                "purpose",
                "🧱 必要な時間",
            )
            category.setdefault(
                "is_default",
                False,
            )

        for day in data["days"]:
            day.setdefault(
                "id",
                create_id(),
            )
            day.setdefault(
                "date",
                today_text(),
            )
            day.setdefault(
                "entries",
                {},
            )
            day.setdefault(
                "satisfaction",
                3,
            )
            day.setdefault(
                "memo",
                "",
            )
            day.setdefault(
                "created_at",
                now_text(),
            )
            day.setdefault(
                "updated_at",
                day.get(
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
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# カテゴリー
# =========================================================

def get_category(
    data,
    category_id,
):
    return next(
        (
            category
            for category
            in data["categories"]
            if category.get(
                "id"
            ) == category_id
        ),
        None,
    )


def category_name(
    data,
    category_id,
):
    category = get_category(
        data,
        category_id,
    )

    if not category:
        return "不明"

    return category.get(
        "name",
        "不明",
    )


def add_category(
    data,
    name,
    direction,
    purpose,
):
    data["categories"].append(
        {
            "id": create_id(),
            "name": name,
            "direction": direction,
            "purpose": purpose,
            "is_default": False,
        }
    )

    save_data(data)


def update_category(
    data,
    category_id,
    name,
    direction,
    purpose,
):
    category = get_category(
        data,
        category_id,
    )

    if not category:
        return

    category["name"] = name
    category["direction"] = direction
    category["purpose"] = purpose

    save_data(data)


def delete_category(
    data,
    category_id,
):
    data["categories"] = [
        category
        for category
        in data["categories"]
        if category.get(
            "id"
        ) != category_id
    ]

    for day in data["days"]:
        if category_id in day.get(
            "entries",
            {},
        ):
            del day["entries"][
                category_id
            ]

    save_data(data)


# =========================================================
# 日次データ
# =========================================================

def get_day(
    data,
    target_date,
):
    target = str(target_date)

    return next(
        (
            day
            for day in data["days"]
            if day.get("date")
            == target
        ),
        None,
    )


def save_day(
    data,
    target_date,
    entries,
    satisfaction,
    memo,
):
    existing = get_day(
        data,
        target_date,
    )

    cleaned_entries = {
        category_id: round(
            float(hours),
            2,
        )
        for category_id, hours
        in entries.items()
        if float(hours) > 0
    }

    if existing:
        existing[
            "entries"
        ] = cleaned_entries

        existing[
            "satisfaction"
        ] = int(
            satisfaction
        )

        existing[
            "memo"
        ] = memo

        existing[
            "updated_at"
        ] = now_text()

    else:
        data["days"].append(
            {
                "id": create_id(),
                "date": str(
                    target_date
                ),
                "entries": (
                    cleaned_entries
                ),
                "satisfaction": int(
                    satisfaction
                ),
                "memo": memo,
                "created_at": (
                    now_text()
                ),
                "updated_at": (
                    now_text()
                ),
            }
        )

    save_data(data)


def delete_day(
    data,
    day_id,
):
    data["days"] = [
        day
        for day in data["days"]
        if day.get("id")
        != day_id
    ]

    save_data(data)


def total_hours(day):
    return round(
        sum(
            float(hours)
            for hours in day.get(
                "entries",
                {},
            ).values()
        ),
        2,
    )


# =========================================================
# 期間集計
# =========================================================

def days_between(
    days,
    start_date,
    end_date,
):
    result = []

    for day in days:
        parsed = parse_date(
            day.get("date")
        )

        if (
            parsed
            and start_date
            <= parsed
            <= end_date
        ):
            result.append(
                day
            )

    return result


def aggregate_categories(
    data,
    selected_days,
):
    totals = {
        category.get("id"): 0.0
        for category
        in data["categories"]
    }

    for day in selected_days:
        for (
            category_id,
            hours,
        ) in day.get(
            "entries",
            {},
        ).items():
            totals[
                category_id
            ] = (
                totals.get(
                    category_id,
                    0.0,
                )
                + float(hours)
            )

    return totals


def monday_of(target_date):
    return (
        target_date
        - timedelta(
            days=target_date.weekday()
        )
    )


def category_comparison(
    data,
    current_days,
    previous_days,
):
    current = aggregate_categories(
        data,
        current_days,
    )

    previous = aggregate_categories(
        data,
        previous_days,
    )

    rows = []

    for category in data["categories"]:
        category_id = category.get(
            "id"
        )

        current_value = current.get(
            category_id,
            0,
        )

        previous_value = previous.get(
            category_id,
            0,
        )

        rows.append(
            {
                "category_id": (
                    category_id
                ),
                "カテゴリー": (
                    category.get(
                        "name",
                        "",
                    )
                ),
                "今週": round(
                    current_value,
                    2,
                ),
                "先週": round(
                    previous_value,
                    2,
                ),
                "差": round(
                    current_value
                    - previous_value,
                    2,
                ),
                "方向": category.get(
                    "direction",
                    "⚖️ 今くらい",
                ),
            }
        )

    return rows


# =========================================================
# 連続記録
# =========================================================

def current_streak(days):
    dates = sorted(
        {
            parse_date(
                day.get("date")
            )
            for day in days
            if parse_date(
                day.get("date")
            )
        }
    )

    if not dates:
        return 0

    date_set = set(dates)

    cursor = date.today()

    # 今日未入力でも昨日まで
    # 続いていれば継続扱い
    if cursor not in date_set:
        cursor -= timedelta(
            days=1
        )

    streak = 0

    while cursor in date_set:
        streak += 1
        cursor -= timedelta(
            days=1
        )

    return streak


# =========================================================
# 満足度傾向
# =========================================================

def satisfaction_category_average(
    data,
    target_days,
):
    result = {}

    for category in data[
        "categories"
    ]:
        category_id = (
            category.get(
                "id"
            )
        )

        values = []

        for day in target_days:
            values.append(
                float(
                    day.get(
                        "entries",
                        {},
                    ).get(
                        category_id,
                        0,
                    )
                )
            )

        result[
            category_id
        ] = average(
            values
        )

    return result


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
        background: rgba(70, 150, 220, 0.07);
        border: 1px solid rgba(70, 150, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 150, 220, 0.18),
                rgba(110, 210, 170, 0.09)
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

days = data["days"]
categories = data["categories"]

today = date.today()

today_day = get_day(
    data,
    today,
)

streak = current_streak(
    days
)

month_prefix = (
    today.strftime(
        "%Y-%m"
    )
)

month_days = [
    day
    for day in days
    if (
        day.get(
            "date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⏰ 今日は何に時間使った？</h1>
        <p>
            時間は、使い方が見えると、
            自分の暮らしが見えてくる。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_hours = (
    total_hours(
        today_day
    )
    if today_day
    else 0
)

self_category_ids = [
    category.get("id")
    for category in categories
    if category.get(
        "purpose"
    ) == "🌱 自分のため"
]

month_self_hours = 0

for day in month_days:
    for category_id in (
        self_category_ids
    ):
        month_self_hours += float(
            day.get(
                "entries",
                {},
            ).get(
                category_id,
                0,
            )
        )

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "⏰ 今日の記録",
    hours_text(
        today_hours
    ),
)

col2.metric(
    "🔥 連続記録",
    f"{streak}日",
)

col3.metric(
    "📅 今月",
    f"{len(month_days)}日記録",
)

col4.metric(
    "🌱 今月、自分のため",
    hours_text(
        month_self_hours
    ),
)


# =========================================================
# 今日の入力
# =========================================================

st.divider()

st.subheader(
    "🌞 今日の24時間"
)

target_date = st.date_input(
    "📅 記録する日",
    value=today,
    max_value=today,
)

existing_day = get_day(
    data,
    target_date,
)

with st.form(
    "daily_time_form"
):
    st.caption(
        "💡 正確じゃなくても大丈夫。"
        "ざっくり把握できればOK！"
    )

    entries = {}

    for index in range(
        0,
        len(categories),
        2,
    ):
        columns = st.columns(2)

        pair = categories[
            index:index + 2
        ]

        for column, category in zip(
            columns,
            pair,
        ):
            category_id = (
                category.get(
                    "id"
                )
            )

            default_value = 0.0

            if existing_day:
                default_value = float(
                    existing_day.get(
                        "entries",
                        {},
                    ).get(
                        category_id,
                        0,
                    )
                )

            with column:
                entries[
                    category_id
                ] = st.number_input(
                    category.get(
                        "name",
                        "",
                    ),
                    min_value=0.0,
                    max_value=24.0,
                    value=default_value,
                    step=0.5,
                    key=(
                        "daily_"
                        + category_id
                    ),
                )

    entered_total = round(
        sum(
            float(value)
            for value in entries.values()
        ),
        2,
    )

    difference = round(
        24 - entered_total,
        2,
    )

    st.markdown(
        f"### ⏰ 合計："
        f"{hours_text(entered_total)}"
    )

    if entered_total < 24:
        st.info(
            "未分類："
            + hours_text(
                difference
            )
        )

    elif entered_total == 24:
        st.success(
            "🎉 24時間ぴったり！"
        )

    else:
        st.warning(
            "⚠️ 24時間を "
            + hours_text(
                abs(difference)
            )
            + " 超えています。"
        )

    old_satisfaction = (
        int(
            existing_day.get(
                "satisfaction",
                3,
            )
        )
        if existing_day
        else 3
    )

    satisfaction = (
        st.select_slider(
            "😊 今日の時間の使い方、満足度は？",
            options=[
                1,
                2,
                3,
                4,
                5,
            ],
            value=old_satisfaction,
            format_func=lambda value: (
                SATISFACTION_LABELS[
                    value
                ]
            ),
        )
    )

    memo = st.text_area(
        "💭 今日のひとこと",
        value=(
            existing_day.get(
                "memo",
                "",
            )
            if existing_day
            else ""
        ),
        placeholder=(
            "例：仕事は長かったけど、"
            "夜に少し勉強できた"
        ),
    )

    submitted = (
        st.form_submit_button(
            "💾 今日の時間を記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if entered_total > 24:
            st.warning(
                "合計が24時間を"
                "超えています。"
                "入力を確認してね。"
            )

        elif entered_total == 0:
            st.warning(
                "時間を1つ以上"
                "入力してね。"
            )

        else:
            save_day(
                data=data,
                target_date=target_date,
                entries=entries,
                satisfaction=(
                    satisfaction
                ),
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 今日のバランス
# =========================================================

selected_day = get_day(
    data,
    target_date,
)

if selected_day:
    st.divider()

    st.subheader(
        "📊 この日の時間バランス"
    )

    selected_total = (
        total_hours(
            selected_day
        )
    )

    balance_rows = []

    for category in categories:
        category_id = (
            category.get(
                "id"
            )
        )

        hours = float(
            selected_day.get(
                "entries",
                {},
            ).get(
                category_id,
                0,
            )
        )

        if hours <= 0:
            continue

        percentage = (
            hours
            / selected_total
            * 100
            if selected_total
            else 0
        )

        balance_rows.append(
            {
                "カテゴリー": (
                    category.get(
                        "name",
                        "",
                    )
                ),
                "時間": hours,
                "割合": round(
                    percentage,
                    1,
                ),
            }
        )

    if balance_rows:
        balance_df = (
            pd.DataFrame(
                balance_rows
            )
            .sort_values(
                "時間",
                ascending=False,
            )
        )

        st.bar_chart(
            balance_df.set_index(
                "カテゴリー"
            )["時間"]
        )

        st.dataframe(
            balance_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "時間": (
                    st.column_config.NumberColumn(
                        "時間",
                        format="%.1fh",
                    )
                ),
                "割合": (
                    st.column_config.NumberColumn(
                        "割合",
                        format="%.1f%%",
                    )
                ),
            },
        )


# =========================================================
# 今週と先週
# =========================================================

st.divider()

st.subheader(
    "📅 今週の時間"
)

this_monday = monday_of(
    today
)

this_sunday = (
    this_monday
    + timedelta(
        days=6
    )
)

last_monday = (
    this_monday
    - timedelta(
        days=7
    )
)

last_sunday = (
    this_monday
    - timedelta(
        days=1
    )
)

this_week_days = (
    days_between(
        days,
        this_monday,
        this_sunday,
    )
)

last_week_days = (
    days_between(
        days,
        last_monday,
        last_sunday,
    )
)

comparison_rows = (
    category_comparison(
        data,
        this_week_days,
        last_week_days,
    )
)

comparison_rows = [
    row
    for row in comparison_rows
    if (
        row["今週"] > 0
        or row["先週"] > 0
    )
]

if not comparison_rows:
    st.info(
        "週次比較に使えるデータが"
        "まだありません。"
    )

else:
    comparison_df = pd.DataFrame(
        comparison_rows
    )

    display_comparison = (
        comparison_df[
            [
                "カテゴリー",
                "今週",
                "先週",
                "差",
                "方向",
            ]
        ].copy()
    )

    st.dataframe(
        display_comparison,
        hide_index=True,
        use_container_width=True,
        column_config={
            "今週": (
                st.column_config.NumberColumn(
                    "今週",
                    format="%.1fh",
                )
            ),
            "先週": (
                st.column_config.NumberColumn(
                    "先週",
                    format="%.1fh",
                )
            ),
            "差": (
                st.column_config.NumberColumn(
                    "先週比",
                    format="%+.1fh",
                )
            ),
        },
    )

    st.markdown(
        "### 🧭 目指している方向との比較"
    )

    for row in comparison_rows:
        direction = row[
            "方向"
        ]

        difference = row[
            "差"
        ]

        name = row[
            "カテゴリー"
        ]

        if (
            direction
            == "🎯 増やしたい"
        ):
            if difference > 0:
                st.success(
                    f"{name}："
                    f"先週より "
                    f"+{hours_text(difference)}。"
                    "増やしたい方向に進んでいます。"
                )
            elif difference < 0:
                st.info(
                    f"{name}："
                    f"先週より "
                    f"-{hours_text(abs(difference))}。"
                )

        elif (
            direction
            == "📉 減らしたい"
        ):
            if difference < 0:
                st.success(
                    f"{name}："
                    f"先週より "
                    f"-{hours_text(abs(difference))}。"
                    "減らしたい方向に進んでいます。"
                )
            elif difference > 0:
                st.info(
                    f"{name}："
                    f"先週より "
                    f"+{hours_text(difference)}。"
                )


# =========================================================
# 自分のための時間
# =========================================================

this_week_self = 0
last_week_self = 0

for day in this_week_days:
    for category_id in (
        self_category_ids
    ):
        this_week_self += float(
            day.get(
                "entries",
                {},
            ).get(
                category_id,
                0,
            )
        )

for day in last_week_days:
    for category_id in (
        self_category_ids
    ):
        last_week_self += float(
            day.get(
                "entries",
                {},
            ).get(
                category_id,
                0,
            )
        )

st.markdown(
    "### 🌱 自分のために使えた時間"
)

col1, col2, col3 = (
    st.columns(3)
)

col1.metric(
    "今週",
    hours_text(
        this_week_self
    ),
)

col2.metric(
    "先週",
    hours_text(
        last_week_self
    ),
)

self_difference = round(
    this_week_self
    - last_week_self,
    2,
)

col3.metric(
    "変化",
    (
        "+"
        if self_difference > 0
        else ""
    )
    + hours_text(
        self_difference
    )
    if self_difference >= 0
    else "-"
    + hours_text(
        abs(self_difference)
    ),
)


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📆 {today.month}月の時間"
)

month_totals = (
    aggregate_categories(
        data,
        month_days,
    )
)

month_rows = []

for category in categories:
    category_id = (
        category.get(
            "id"
        )
    )

    hours = month_totals.get(
        category_id,
        0,
    )

    if hours > 0:
        month_rows.append(
            {
                "カテゴリー": (
                    category.get(
                        "name",
                        "",
                    )
                ),
                "時間": round(
                    hours,
                    2,
                ),
            }
        )

if not month_rows:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    month_df = (
        pd.DataFrame(
            month_rows
        )
        .sort_values(
            "時間",
            ascending=False,
        )
    )

    exclude_sleep = (
        st.toggle(
            "😴 睡眠を除外して見る"
        )
    )

    chart_df = (
        month_df.copy()
    )

    if exclude_sleep:
        chart_df = chart_df[
            chart_df[
                "カテゴリー"
            ]
            != "😴 睡眠"
        ]

    st.bar_chart(
        chart_df.set_index(
            "カテゴリー"
        )["時間"]
    )

    total_month_hours = (
        chart_df["時間"].sum()
        if not chart_df.empty
        else 0
    )

    if total_month_hours > 0:
        chart_df = (
            chart_df.copy()
        )

        chart_df["割合"] = (
            chart_df["時間"]
            / total_month_hours
            * 100
        )

        st.dataframe(
            chart_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "時間": (
                    st.column_config.NumberColumn(
                        "時間",
                        format="%.1fh",
                    )
                ),
                "割合": (
                    st.column_config.NumberColumn(
                        "割合",
                        format="%.1f%%",
                    )
                ),
            },
        )


# =========================================================
# 満足度との傾向
# =========================================================

if len(days) >= 5:
    st.divider()

    st.subheader(
        "😊 満足度が高い日・低い日の傾向"
    )

    high_days = [
        day
        for day in days
        if int(
            day.get(
                "satisfaction",
                3,
            )
        ) >= 4
    ]

    low_days = [
        day
        for day in days
        if int(
            day.get(
                "satisfaction",
                3,
            )
        ) <= 2
    ]

    if (
        len(high_days) >= 2
        and len(low_days) >= 2
    ):
        high_average = (
            satisfaction_category_average(
                data,
                high_days,
            )
        )

        low_average = (
            satisfaction_category_average(
                data,
                low_days,
            )
        )

        tendency_rows = []

        for category in categories:
            category_id = (
                category.get(
                    "id"
                )
            )

            tendency_rows.append(
                {
                    "カテゴリー": (
                        category.get(
                            "name",
                            "",
                        )
                    ),
                    "満足度が高い日": (
                        high_average.get(
                            category_id,
                            0,
                        )
                    ),
                    "満足度が低い日": (
                        low_average.get(
                            category_id,
                            0,
                        )
                    ),
                }
            )

        tendency_df = pd.DataFrame(
            tendency_rows
        )

        tendency_df[
            "差"
        ] = (
            tendency_df[
                "満足度が高い日"
            ]
            - tendency_df[
                "満足度が低い日"
            ]
        )

        tendency_df = (
            tendency_df.sort_values(
                "差",
                ascending=False,
            )
        )

        st.dataframe(
            tendency_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "満足度が高い日": (
                    st.column_config.NumberColumn(
                        "😊 高い日の平均",
                        format="%.1fh",
                    )
                ),
                "満足度が低い日": (
                    st.column_config.NumberColumn(
                        "😐 低い日の平均",
                        format="%.1fh",
                    )
                ),
                "差": (
                    st.column_config.NumberColumn(
                        "差",
                        format="%+.1fh",
                    )
                ),
            },
        )

        st.caption(
            "※ これは記録上の関連を"
            "比較したものです。"
            "時間配分が満足度の原因だと"
            "断定するものではありません。"
        )

    else:
        st.caption(
            "満足度4〜5の日と1〜2の日が"
            "それぞれ2日以上あると"
            "比較できます。"
        )


# =========================================================
# 過去の一日
# =========================================================

old_days = [
    day
    for day in days
    if parse_date(
        day.get(
            "date"
        )
    )
    and parse_date(
        day.get(
            "date"
        )
    ) < today
]

if old_days:
    st.divider()

    st.subheader(
        "🎲 こんな一日がありました"
    )

    day_ids = [
        day.get("id")
        for day in old_days
    ]

    random_day_id = (
        st.session_state.get(
            "random_day_id"
        )
    )

    if random_day_id not in day_ids:
        random_day_id = (
            random.choice(
                day_ids
            )
        )

        st.session_state[
            "random_day_id"
        ] = random_day_id

    random_day = next(
        (
            day
            for day in old_days
            if day.get(
                "id"
            ) == random_day_id
        ),
        None,
    )

    if random_day:
        with st.container(
            border=True
        ):
            st.subheader(
                format_date(
                    random_day.get(
                        "date"
                    )
                )
            )

            st.write(
                "満足度："
                + SATISFACTION_LABELS[
                    int(
                        random_day.get(
                            "satisfaction",
                            3,
                        )
                    )
                ]
            )

            random_rows = []

            for (
                category_id,
                hours,
            ) in random_day.get(
                "entries",
                {},
            ).items():
                random_rows.append(
                    {
                        "カテゴリー": (
                            category_name(
                                data,
                                category_id,
                            )
                        ),
                        "時間": (
                            float(
                                hours
                            )
                        ),
                    }
                )

            random_rows = sorted(
                random_rows,
                key=lambda row: (
                    row["時間"]
                ),
                reverse=True,
            )

            for row in random_rows:
                st.write(
                    f"{row['カテゴリー']}："
                    f"{hours_text(row['時間'])}"
                )

            if random_day.get(
                "memo"
            ):
                st.info(
                    "💭 "
                    + random_day.get(
                        "memo",
                        "",
                    )
                )

        if st.button(
            "🎲 別の日を見る",
            use_container_width=True,
        ):
            alternatives = [
                day_id
                for day_id in day_ids
                if day_id
                != random_day_id
            ]

            if alternatives:
                st.session_state[
                    "random_day_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 時間図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 時間図鑑"
)

if not days:
    st.info(
        "まだ記録がありません。"
    )

else:
    library_rows = []

    for day in sorted(
        days,
        key=lambda item: (
            item.get(
                "date",
                "",
            )
        ),
        reverse=True,
    ):
        total = total_hours(
            day
        )

        library_rows.append(
            {
                "日付": format_date(
                    day.get(
                        "date"
                    )
                ),
                "満足度": (
                    SATISFACTION_LABELS[
                        int(
                            day.get(
                                "satisfaction",
                                3,
                            )
                        )
                    ]
                ),
                "記録時間": (
                    total
                ),
                "未分類": max(
                    24 - total,
                    0,
                ),
                "ひとこと": (
                    day.get(
                        "memo",
                        "",
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            library_rows
        ),
        hide_index=True,
        use_container_width=True,
        column_config={
            "記録時間": (
                st.column_config.NumberColumn(
                    "記録時間",
                    format="%.1fh",
                )
            ),
            "未分類": (
                st.column_config.NumberColumn(
                    "未分類",
                    format="%.1fh",
                )
            ),
        },
    )


# =========================================================
# 記録削除
# =========================================================

with st.expander(
    "🗑️ 日次記録の削除"
):
    for day in sorted(
        days,
        key=lambda item: (
            item.get(
                "date",
                "",
            )
        ),
        reverse=True,
    ):
        day_id = day.get(
            "id",
            "",
        )

        col1, col2 = (
            st.columns(
                [5, 1]
            )
        )

        with col1:
            st.write(
                f"**{format_date(day.get('date'))}**"
                f" ｜ "
                f"{SATISFACTION_LABELS[int(day.get('satisfaction', 3))]}"
                f" ｜ "
                f"{hours_text(total_hours(day))}"
            )

        with col2:
            if st.button(
                "🗑️",
                key=(
                    "delete_day_"
                    + day_id
                ),
            ):
                delete_day(
                    data,
                    day_id,
                )

                st.rerun()


# =========================================================
# カテゴリー設定
# =========================================================

st.divider()

st.subheader(
    "⚙️ カテゴリー設定"
)

with st.expander(
    "➕ カスタムカテゴリーを追加"
):
    with st.form(
        "add_category_form",
        clear_on_submit=True,
    ):
        new_name = (
            st.text_input(
                "カテゴリー名",
                placeholder=(
                    "例：📖 読書"
                ),
            )
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            new_direction = (
                st.selectbox(
                    "方向",
                    DIRECTIONS,
                )
            )

        with col2:
            new_purpose = (
                st.selectbox(
                    "時間の種類",
                    PURPOSES,
                )
            )

        add_submitted = (
            st.form_submit_button(
                "➕ 追加",
                use_container_width=True,
            )
        )

        if add_submitted:
            if not (
                new_name.strip()
            ):
                st.warning(
                    "カテゴリー名を入力してね。"
                )

            else:
                add_category(
                    data,
                    new_name.strip(),
                    new_direction,
                    new_purpose,
                )

                st.rerun()


for category in categories:
    category_id = (
        category.get(
            "id",
            "",
        )
    )

    with st.expander(
        category.get(
            "name",
            "",
        )
    ):
        edit_name = (
            st.text_input(
                "名前",
                value=category.get(
                    "name",
                    "",
                ),
                key=(
                    "category_name_"
                    + category_id
                ),
            )
        )

        old_direction = (
            category.get(
                "direction",
                "⚖️ 今くらい",
            )
        )

        direction_index = (
            DIRECTIONS.index(
                old_direction
            )
            if old_direction
            in DIRECTIONS
            else 2
        )

        edit_direction = (
            st.selectbox(
                "方向",
                DIRECTIONS,
                index=direction_index,
                key=(
                    "category_direction_"
                    + category_id
                ),
            )
        )

        old_purpose = (
            category.get(
                "purpose",
                "🧱 必要な時間",
            )
        )

        purpose_index = (
            PURPOSES.index(
                old_purpose
            )
            if old_purpose
            in PURPOSES
            else 2
        )

        edit_purpose = (
            st.selectbox(
                "時間の種類",
                PURPOSES,
                index=purpose_index,
                key=(
                    "category_purpose_"
                    + category_id
                ),
            )
        )

        if st.button(
            "💾 カテゴリー保存",
            key=(
                "save_category_"
                + category_id
            ),
            use_container_width=True,
        ):
            if not edit_name.strip():
                st.warning(
                    "カテゴリー名を入力してね。"
                )
            else:
                update_category(
                    data,
                    category_id,
                    edit_name.strip(),
                    edit_direction,
                    edit_purpose,
                )

                st.rerun()

        if not category.get(
            "is_default",
            False,
        ):
            confirm_delete = (
                st.checkbox(
                    "このカテゴリーを削除",
                    key=(
                        "confirm_category_delete_"
                        + category_id
                    ),
                )
            )

            if st.button(
                "🗑️ カテゴリー削除",
                key=(
                    "delete_category_"
                    + category_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_category(
                    data,
                    category_id,
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
            "time_usage_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "⏰ 時間は、使い方が見えると、"
    "自分の暮らしが見えてくる。"
)

st.caption(
    "記録できなかった日も、"
    "ちゃんと生きていた日。"
)
