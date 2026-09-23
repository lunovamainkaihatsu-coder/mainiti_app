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
    page_title="今日の余白",
    page_icon="🌿",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "margin.json",
)

ACTIVITIES = [
    "☕ ぼーっとした",
    "🚶 散歩した",
    "🎵 音楽を聴いた",
    "🌤️ 外を眺めた",
    "📖 軽く読書した",
    "🛋️ 横になった",
    "🫖 飲み物を楽しんだ",
    "🌿 深呼吸した",
    "✨ その他",
]

QUICK_MINUTES = [
    5,
    10,
    15,
    30,
    60,
]

DAY_STATUS = {
    "margin": "🌿 余白があった",
    "none": "🌀 ほぼなかった",
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


def month_text():
    return date.today().strftime(
        "%Y-%m"
    )


def parse_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def format_minutes(minutes):
    minutes = int(minutes)

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    rest = minutes % 60

    if rest == 0:
        return f"{hours}時間"

    return (
        f"{hours}時間"
        f"{rest}分"
    )


def recovery_stars(level):
    level = int(level)

    return (
        "★" * level
        + "☆" * (5 - level)
    )


def create_empty_data():
    return {
        "records": [],
        "day_status": [],
        "settings": {
            "daily_goal_minutes": 30,
        },
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
            "records",
            [],
        )

        data.setdefault(
            "day_status",
            [],
        )

        data.setdefault(
            "settings",
            {},
        )

        data["settings"].setdefault(
            "daily_goal_minutes",
            30,
        )

        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "minutes",
                10,
            )

            record.setdefault(
                "activity",
                "☕ ぼーっとした",
            )

            record.setdefault(
                "recovery",
                3,
            )

            record.setdefault(
                "memo",
                "",
            )

            record.setdefault(
                "record_date",
                today_text(),
            )

            record.setdefault(
                "created_at",
                now_text(),
            )

            record.setdefault(
                "favorite",
                False,
            )

        for status in data["day_status"]:
            status.setdefault(
                "id",
                create_id(),
            )

            status.setdefault(
                "record_date",
                today_text(),
            )

            status.setdefault(
                "status",
                "margin",
            )

            status.setdefault(
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

def add_record(
    data,
    minutes,
    activity,
    recovery,
    memo="",
    record_date=None,
):
    if record_date is None:
        record_date = date.today()

    data["records"].append(
        {
            "id": create_id(),
            "minutes": int(
                minutes
            ),
            "activity": activity,
            "recovery": int(
                recovery
            ),
            "memo": memo,
            "record_date": str(
                record_date
            ),
            "created_at": now_text(),
            "favorite": False,
        }
    )

    set_day_status(
        data,
        str(record_date),
        "margin",
        save=False,
    )

    save_data(data)


def get_record(
    data,
    record_id,
):
    return next(
        (
            record
            for record in data["records"]
            if record.get(
                "id"
            ) == record_id
        ),
        None,
    )


def update_record(
    data,
    record_id,
    minutes,
    activity,
    recovery,
    memo,
    record_date,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["minutes"] = int(
        minutes
    )

    record["activity"] = activity

    record["recovery"] = int(
        recovery
    )

    record["memo"] = memo

    record["record_date"] = str(
        record_date
    )

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get(
            "id"
        ) != record_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    record_id,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["favorite"] = not (
        record.get(
            "favorite",
            False,
        )
    )

    save_data(data)


def set_day_status(
    data,
    record_date,
    status,
    save=True,
):
    existing = next(
        (
            item
            for item in data[
                "day_status"
            ]
            if item.get(
                "record_date"
            ) == record_date
        ),
        None,
    )

    if existing:
        existing[
            "status"
        ] = status

    else:
        data[
            "day_status"
        ].append(
            {
                "id": create_id(),
                "record_date": (
                    record_date
                ),
                "status": status,
                "created_at": (
                    now_text()
                ),
            }
        )

    if save:
        save_data(data)


def update_daily_goal(
    data,
    minutes,
):
    data[
        "settings"
    ][
        "daily_goal_minutes"
    ] = int(
        minutes
    )

    save_data(data)


# =========================================================
# 集計
# =========================================================

def total_minutes(records):
    return sum(
        int(
            record.get(
                "minutes",
                0,
            )
        )
        for record in records
    )


def average_recovery(records):
    if not records:
        return 0

    return round(
        sum(
            int(
                record.get(
                    "recovery",
                    0,
                )
            )
            for record in records
        )
        / len(records),
        1,
    )


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
            rgba(70, 170, 110, 0.07);

        border:
            1px solid
            rgba(70, 170, 110, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 180, 120, 0.18),
                rgba(160, 210, 150, 0.07)
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

    .margin-card {
        padding: 28px;
        border-radius: 24px;
        margin-top: 15px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 180, 120, 0.12),
                rgba(120, 200, 180, 0.06)
            );
    }

    .margin-number {
        font-size: 2.5rem;
        font-weight: 800;
    }

    .memory-card {
        padding: 24px;
        border-radius: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 170, 120, 0.10),
                rgba(180, 200, 120, 0.06)
            );
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ
# =========================================================

data = load_data()

records = data[
    "records"
]

today = date.today()

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    ) == str(today)
]

current_month = (
    today.strftime(
        "%Y-%m"
    )
)

month_records = [
    record
    for record in records
    if record.get(
        "record_date",
        "",
    ).startswith(
        current_month
    )
]

daily_goal = int(
    data[
        "settings"
    ].get(
        "daily_goal_minutes",
        30,
    )
)


# =========================================================
# Session State
# =========================================================

defaults = {
    "quick_minutes": None,
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

        <h1>🌿 今日の余白</h1>

        <p>
            何もしなかった時間も、
            今日を生きた時間。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日のダッシュボード
# =========================================================

today_minutes = total_minutes(
    today_records
)

today_recovery = (
    average_recovery(
        today_records
    )
)

month_minutes = total_minutes(
    month_records
)

month_days = len(
    {
        record.get(
            "record_date"
        )
        for record in month_records
    }
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌿 今日の余白",
    format_minutes(
        today_minutes
    ),
)

col2.metric(
    "🎯 今日の目安",
    format_minutes(
        daily_goal
    ),
)

col3.metric(
    "😌 今日の回復度",
    (
        f"{today_recovery} / 5"
        if today_records
        else "-"
    ),
)

col4.metric(
    "🌱 今月余白があった日",
    f"{month_days}日",
)


# =========================================================
# 今日の余白メーター
# =========================================================

st.divider()

st.subheader(
    "🌿 今日の余白メーター"
)

progress = min(
    today_minutes
    / max(
        daily_goal,
        1,
    ),
    1.0,
)

st.progress(
    progress
)

st.markdown(
    f"""
    <div class="margin-card">

        <div>
            今日の余白
        </div>

        <div class="margin-number">
            {format_minutes(today_minutes)}
        </div>

        <div>
            目安：
            {format_minutes(daily_goal)}
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)

if today_minutes == 0:
    st.caption(
        "まだ余白の記録はありません。"
        "5分でも十分です。🌱"
    )

elif today_minutes < daily_goal:
    st.success(
        f"🌿 今日も"
        f"{format_minutes(today_minutes)}"
        "の余白がありました。"
    )

else:
    st.success(
        "🌿 今日も余白を"
        "ちゃんと持てました。"
    )


# =========================================================
# クイック記録
# =========================================================

st.divider()

st.subheader(
    "⚡ 今、余白できた！"
)

st.caption(
    "時間を選んで、"
    "過ごし方だけサッと記録。"
)

quick_cols = st.columns(
    len(
        QUICK_MINUTES
    )
)

for index, minutes in enumerate(
    QUICK_MINUTES
):
    with quick_cols[index]:
        if st.button(
            f"{minutes}分",
            key=(
                "quick_"
                + str(minutes)
            ),
            use_container_width=True,
        ):
            st.session_state[
                "quick_minutes"
            ] = minutes

            st.rerun()


if st.session_state[
    "quick_minutes"
]:
    quick_minutes = (
        st.session_state[
            "quick_minutes"
        ]
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### 🌿 "
            f"{quick_minutes}分の余白"
        )

        quick_activity = st.selectbox(
            "どう過ごした？",
            ACTIVITIES,
            key="quick_activity",
        )

        quick_recovery = st.slider(
            "😌 回復度",
            1,
            5,
            3,
            key="quick_recovery",
        )

        st.caption(
            recovery_stars(
                quick_recovery
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🌿 記録する",
                type="primary",
                use_container_width=True,
            ):
                add_record(
                    data,
                    quick_minutes,
                    quick_activity,
                    quick_recovery,
                )

                st.session_state[
                    "quick_minutes"
                ] = None

                st.rerun()

        with col2:
            if st.button(
                "キャンセル",
                use_container_width=True,
            ):
                st.session_state[
                    "quick_minutes"
                ] = None

                st.rerun()


# =========================================================
# 詳細記録
# =========================================================

st.divider()

with st.expander(
    "✍️ 余白を詳しく記録"
):
    with st.form(
        "detail_form",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns(2)

        with col1:
            detail_date = st.date_input(
                "日付",
                value=date.today(),
            )

            detail_minutes = (
                st.number_input(
                    "⏱️ 余白時間（分）",
                    min_value=1,
                    max_value=1440,
                    value=15,
                    step=5,
                )
            )

        with col2:
            detail_activity = (
                st.selectbox(
                    "☕ どう過ごした？",
                    ACTIVITIES,
                )
            )

            detail_recovery = (
                st.slider(
                    "😌 回復度",
                    1,
                    5,
                    3,
                )
            )

        detail_memo = st.text_area(
            "💬 余白の一言",
            placeholder=(
                "公園のベンチで"
                "ぼーっとした。"
                "風が気持ちよかった。"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🌿 記録する",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            add_record(
                data,
                detail_minutes,
                detail_activity,
                detail_recovery,
                detail_memo.strip(),
                detail_date,
            )

            st.rerun()


# =========================================================
# 今日の内訳
# =========================================================

if today_records:
    st.divider()

    st.subheader(
        "☕ 今日の余白"
    )

    activity_summary = {}

    for record in today_records:
        activity = record.get(
            "activity",
            "✨ その他",
        )

        activity_summary[
            activity
        ] = (
            activity_summary.get(
                activity,
                0,
            )
            + int(
                record.get(
                    "minutes",
                    0,
                )
            )
        )

    for activity, minutes in sorted(
        activity_summary.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        st.write(
            f"{activity}　"
            f"**{format_minutes(minutes)}**"
        )


# =========================================================
# 今日の振り返り
# =========================================================

st.divider()

st.subheader(
    "🌙 今日を振り返る"
)

today_status = next(
    (
        item
        for item in data[
            "day_status"
        ]
        if item.get(
            "record_date"
        ) == str(today)
    ),
    None,
)

if today_status:
    status_key = today_status.get(
        "status",
        "margin",
    )

    st.info(
        "今日の記録："
        + DAY_STATUS.get(
            status_key,
            ""
        )
    )

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "🌿 余白があった",
        use_container_width=True,
    ):
        set_day_status(
            data,
            str(today),
            "margin",
        )

        st.rerun()

with col2:
    if st.button(
        "🌀 ほぼなかった",
        use_container_width=True,
    ):
        set_day_status(
            data,
            str(today),
            "none",
        )

        st.rerun()

st.caption(
    "「余白がなかった」も、"
    "失敗ではなく今日の記録です。"
)


# =========================================================
# 今週の余白
# =========================================================

st.divider()

st.subheader(
    "📅 今週の余白"
)

week_start = (
    today
    - timedelta(
        days=today.weekday()
    )
)

week_dates = [
    week_start
    + timedelta(
        days=index
    )
    for index in range(7)
]

week_rows = []

weekdays = [
    "月",
    "火",
    "水",
    "木",
    "金",
    "土",
    "日",
]

for index, day_value in enumerate(
    week_dates
):
    day_records = [
        record
        for record in records
        if record.get(
            "record_date"
        ) == str(
            day_value
        )
    ]

    week_rows.append(
        {
            "曜日": (
                f"{weekdays[index]}"
                f" {day_value.month}/"
                f"{day_value.day}"
            ),
            "余白時間": total_minutes(
                day_records
            ),
        }
    )

week_df = pd.DataFrame(
    week_rows
)

st.bar_chart(
    week_df.set_index(
        "曜日"
    )
)

week_total = int(
    week_df[
        "余白時間"
    ].sum()
)

st.caption(
    "🌿 今週の合計："
    + format_minutes(
        week_total
    )
)


# =========================================================
# 自分に合っていた余白
# =========================================================

if records:
    st.divider()

    st.subheader(
        "😌 自分に合っていた余白"
    )

    activity_rows = []

    for activity in ACTIVITIES:
        activity_records = [
            record
            for record in records
            if record.get(
                "activity"
            ) == activity
        ]

        if not activity_records:
            continue

        activity_rows.append(
            {
                "過ごし方": activity,
                "回数": len(
                    activity_records
                ),
                "平均回復度": (
                    average_recovery(
                        activity_records
                    )
                ),
                "合計時間": (
                    total_minutes(
                        activity_records
                    )
                ),
            }
        )

    if activity_rows:
        activity_df = pd.DataFrame(
            activity_rows
        )

        activity_df = (
            activity_df.sort_values(
                [
                    "平均回復度",
                    "回数",
                ],
                ascending=[
                    False,
                    False,
                ],
            )
        )

        st.dataframe(
            activity_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "平均回復度":
                    st.column_config.ProgressColumn(
                        "平均回復度",
                        min_value=0,
                        max_value=5,
                        format="%.1f",
                    ),
                "合計時間":
                    st.column_config.NumberColumn(
                        "合計時間（分）"
                    ),
            },
        )


# =========================================================
# 今月のダッシュボード
# =========================================================

st.divider()

st.subheader(
    "📊 今月の余白"
)

month_average = 0

if month_days > 0:
    month_average = round(
        month_minutes
        / month_days,
        1,
    )

month_recovery = (
    average_recovery(
        month_records
    )
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌿 合計",
    format_minutes(
        month_minutes
    ),
)

col2.metric(
    "☕ 余白があった日の平均",
    f"{month_average}分",
)

col3.metric(
    "😌 平均回復度",
    (
        f"{month_recovery} / 5"
        if month_records
        else "-"
    ),
)

col4.metric(
    "🌱 記録日",
    f"{month_days}日",
)


# =========================================================
# 月間日別グラフ
# =========================================================

if month_records:
    daily_summary = {}

    for record in month_records:
        record_date = record.get(
            "record_date"
        )

        daily_summary[
            record_date
        ] = (
            daily_summary.get(
                record_date,
                0,
            )
            + int(
                record.get(
                    "minutes",
                    0,
                )
            )
        )

    daily_df = pd.DataFrame(
        [
            {
                "日付": key,
                "余白時間": value,
            }
            for key, value
            in sorted(
                daily_summary.items()
            )
        ]
    )

    st.line_chart(
        daily_df.set_index(
            "日付"
        )
    )


# =========================================================
# 余白あり / なし
# =========================================================

if data["day_status"]:
    st.divider()

    st.subheader(
        "🌿 余白があった日"
    )

    current_statuses = [
        item
        for item in data[
            "day_status"
        ]
        if item.get(
            "record_date",
            "",
        ).startswith(
            current_month
        )
    ]

    margin_days = len(
        [
            item
            for item in current_statuses
            if item.get(
                "status"
            ) == "margin"
        ]
    )

    none_days = len(
        [
            item
            for item in current_statuses
            if item.get(
                "status"
            ) == "none"
        ]
    )

    status_df = pd.DataFrame(
        [
            {
                "状態": "🌿 余白あり",
                "日数": margin_days,
            },
            {
                "状態": "🌀 ほぼなし",
                "日数": none_days,
            },
        ]
    )

    st.bar_chart(
        status_df.set_index(
            "状態"
        )
    )


# =========================================================
# 過去の余白
# =========================================================

memo_records = [
    record
    for record in records
    if record.get(
        "memo",
        ""
    ).strip()
]

if memo_records:
    st.divider()

    st.subheader(
        "🔮 過去の余白"
    )

    if st.button(
        "🌿 過去の余白をひとつ見る",
        use_container_width=True,
    ):
        st.session_state[
            "random_margin_id"
        ] = random.choice(
            memo_records
        ).get(
            "id"
        )

    random_id = st.session_state.get(
        "random_margin_id"
    )

    if random_id:
        memory = get_record(
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
                today
                - memory_date
            ).days

            st.markdown(
                f"""
                <div class="memory-card">

                    <h3>
                        🌿 {days_ago}日前の余白
                    </h3>

                    <p>
                        {memory.get("memo", "")}
                    </p>

                    <strong>
                        {memory.get("activity", "")}
                        ・
                        {format_minutes(
                            memory.get("minutes", 0)
                        )}
                        ・
                        {recovery_stars(
                            memory.get("recovery", 3)
                        )}
                    </strong>

                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 余白の記録"
)

search_text = st.text_input(
    "🔎 記録を検索",
    placeholder=(
        "メモや過ごし方から検索"
    ),
)

activity_filter = st.selectbox(
    "過ごし方",
    ["すべて"] + ACTIVITIES,
    key="history_activity",
)

filtered_records = []

for record in records:
    if (
        activity_filter
        != "すべて"
        and record.get(
            "activity"
        )
        != activity_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                record.get(
                    "activity",
                    "",
                ),
                record.get(
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

    filtered_records.append(
        record
    )


if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    for record in sorted(
        filtered_records,
        key=lambda value: (
            value.get(
                "record_date",
                "",
            ),
            value.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        record_id = record.get(
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
                    f"### "
                    f"{record.get('activity', '')}"
                )

            with col2:
                icon = (
                    "⭐"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    icon,
                    key=(
                        "favorite_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            st.write(
                f"🌿 "
                f"{format_minutes(record.get('minutes', 0))}"
                f"　😌 "
                f"{recovery_stars(record.get('recovery', 3))}"
            )

            st.caption(
                record.get(
                    "record_date",
                    ""
                )
            )

            if record.get(
                "memo",
                "",
            ):
                st.write(
                    "💬 "
                    + record.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 記録を編集・削除"
):
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
        key=lambda value: (
            value.get(
                "record_date",
                "",
            ),
            value.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        title = (
            f"{record.get('record_date', '')}"
            f" ｜ "
            f"{record.get('activity', '')}"
            f" ｜ "
            f"{format_minutes(record.get('minutes', 0))}"
        )

        with st.expander(
            title
        ):
            edit_date = st.date_input(
                "日付",
                value=parse_date(
                    record.get(
                        "record_date"
                    )
                ),
                key=(
                    "edit_date_"
                    + record_id
                ),
            )

            edit_minutes = st.number_input(
                "余白時間（分）",
                min_value=1,
                max_value=1440,
                value=int(
                    record.get(
                        "minutes",
                        10,
                    )
                ),
                key=(
                    "edit_minutes_"
                    + record_id
                ),
            )

            current_activity = (
                record.get(
                    "activity",
                    ACTIVITIES[0],
                )
            )

            activity_index = (
                ACTIVITIES.index(
                    current_activity
                )
                if current_activity
                in ACTIVITIES
                else 0
            )

            edit_activity = st.selectbox(
                "過ごし方",
                ACTIVITIES,
                index=activity_index,
                key=(
                    "edit_activity_"
                    + record_id
                ),
            )

            edit_recovery = st.slider(
                "回復度",
                1,
                5,
                int(
                    record.get(
                        "recovery",
                        3,
                    )
                ),
                key=(
                    "edit_recovery_"
                    + record_id
                ),
            )

            edit_memo = st.text_area(
                "一言",
                value=record.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + record_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    update_record(
                        data,
                        record_id,
                        edit_minutes,
                        edit_activity,
                        edit_recovery,
                        edit_memo.strip(),
                        edit_date,
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "🗑️ 削除",
                    key=(
                        "delete_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    delete_record(
                        data,
                        record_id,
                    )

                    st.rerun()


# =========================================================
# 設定
# =========================================================

st.divider()

with st.expander(
    "⚙️ 設定"
):
    goal_value = st.number_input(
        "🌿 1日の余白の目安（分）",
        min_value=1,
        max_value=600,
        value=daily_goal,
        step=5,
    )

    st.caption(
        "これはノルマではなく、"
        "あくまで目安です。"
    )

    if st.button(
        "💾 設定を保存",
        use_container_width=True,
    ):
        update_daily_goal(
            data,
            goal_value,
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
            "today_margin_"
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
    "何もしなかった時間も、"
    "今日を生きた時間。🌿"
)
