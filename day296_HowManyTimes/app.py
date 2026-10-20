import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="これ、何回目？",
    page_icon="🔁",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "patterns.json",
)

CATEGORIES = [
    "💡 アイデア",
    "🧠 心・気分",
    "💻 仕事・開発",
    "🏠 生活",
    "💰 お金",
    "🏃 身体・運動",
    "👥 人間関係",
    "📱 モノ・機械",
    "✨ その他",
]

PATTERN_TYPES = [
    "🌱 良いこと",
    "😐 どちらでもない",
    "⚠️ 困りごと",
]

TIME_PERIODS = [
    "🌅 朝",
    "☀️ 昼",
    "🌆 夕方",
    "🌙 夜",
    "🌃 深夜",
]

WEEKDAYS = [
    "月",
    "火",
    "水",
    "木",
    "金",
    "土",
    "日",
]


# =========================================================
# 共通関数
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


def days_ago(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    days = (
        date.today()
        - parsed
    ).days

    if days == 0:
        return "今日"

    if days == 1:
        return "昨日"

    if days < 0:
        return "未来"

    return f"{days}日前"


def interval_text(days):
    if days is None:
        return "-"

    if days == 0:
        return "同日"

    if days == 1:
        return "1日"

    return f"{days:.1f}日"


# =========================================================
# データ管理
# =========================================================

def empty_data():
    return {
        "patterns": [],
        "occurrences": [],
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
            "patterns",
            [],
        )
        data.setdefault(
            "occurrences",
            [],
        )

        for pattern in data[
            "patterns"
        ]:
            if not pattern.get("id"):
                pattern["id"] = (
                    create_id()
                )

            pattern.setdefault(
                "title",
                "",
            )
            pattern.setdefault(
                "category",
                "✨ その他",
            )
            pattern.setdefault(
                "type",
                "😐 どちらでもない",
            )
            pattern.setdefault(
                "description",
                "",
            )
            pattern.setdefault(
                "favorite",
                False,
            )
            pattern.setdefault(
                "created_at",
                now_text(),
            )
            pattern.setdefault(
                "updated_at",
                pattern.get(
                    "created_at",
                    now_text(),
                ),
            )

        for occurrence in data[
            "occurrences"
        ]:
            if not occurrence.get("id"):
                occurrence["id"] = (
                    create_id()
                )

            occurrence.setdefault(
                "pattern_id",
                "",
            )
            occurrence.setdefault(
                "date",
                today_text(),
            )
            occurrence.setdefault(
                "time_period",
                "🌙 夜",
            )
            occurrence.setdefault(
                "situation",
                "",
            )
            occurrence.setdefault(
                "memo",
                "",
            )
            occurrence.setdefault(
                "created_at",
                now_text(),
            )
            occurrence.setdefault(
                "updated_at",
                occurrence.get(
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
# 取得
# =========================================================

def get_pattern(
    data,
    pattern_id,
):
    return next(
        (
            pattern
            for pattern
            in data["patterns"]
            if pattern.get("id")
            == pattern_id
        ),
        None,
    )


def get_occurrence(
    data,
    occurrence_id,
):
    return next(
        (
            occurrence
            for occurrence
            in data["occurrences"]
            if occurrence.get("id")
            == occurrence_id
        ),
        None,
    )


def pattern_occurrences(
    data,
    pattern_id,
):
    occurrences = [
        occurrence
        for occurrence
        in data["occurrences"]
        if occurrence.get(
            "pattern_id"
        ) == pattern_id
    ]

    return sorted(
        occurrences,
        key=lambda row: (
            row.get(
                "date",
                "",
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
    )


# =========================================================
# 分析
# =========================================================

def occurrence_dates(
    occurrences,
):
    dates = []

    for occurrence in occurrences:
        parsed = parse_date(
            occurrence.get(
                "date"
            )
        )

        if parsed:
            dates.append(parsed)

    return sorted(dates)


def intervals(
    occurrences,
):
    dates = occurrence_dates(
        occurrences
    )

    if len(dates) < 2:
        return []

    return [
        (
            dates[index]
            - dates[index - 1]
        ).days
        for index in range(
            1,
            len(dates),
        )
    ]


def average_interval(
    occurrences,
):
    values = intervals(
        occurrences
    )

    if not values:
        return None

    return sum(values) / len(
        values
    )


def last_occurrence_date(
    occurrences,
):
    dates = occurrence_dates(
        occurrences
    )

    if not dates:
        return None

    return dates[-1]


def first_occurrence_date(
    occurrences,
):
    dates = occurrence_dates(
        occurrences
    )

    if not dates:
        return None

    return dates[0]


def recent_occurrence_count(
    occurrences,
    days=30,
):
    start = (
        date.today()
        - timedelta(
            days=days - 1
        )
    )

    count = 0

    for occurrence in occurrences:
        parsed = parse_date(
            occurrence.get(
                "date"
            )
        )

        if (
            parsed
            and start
            <= parsed
            <= date.today()
        ):
            count += 1

    return count


def weekday_counts(
    occurrences,
):
    counts = {
        weekday: 0
        for weekday in WEEKDAYS
    }

    for occurrence in occurrences:
        parsed = parse_date(
            occurrence.get(
                "date"
            )
        )

        if not parsed:
            continue

        weekday = WEEKDAYS[
            parsed.weekday()
        ]

        counts[weekday] += 1

    return counts


def time_period_counts(
    occurrences,
):
    counts = {
        period: 0
        for period in TIME_PERIODS
    }

    for occurrence in occurrences:
        period = occurrence.get(
            "time_period"
        )

        if period in counts:
            counts[period] += 1

    return counts


def trend_analysis(
    occurrences,
):
    values = intervals(
        occurrences
    )

    # ある程度データが必要
    if len(values) < 4:
        return {
            "status": "few",
            "message": (
                "🌱 まだデータが少ないので、"
                "傾向判定は参考程度です。"
            ),
        }

    split = len(values) // 2

    old_values = values[:split]
    recent_values = values[split:]

    if not old_values or not recent_values:
        return {
            "status": "few",
            "message": (
                "🌱 もう少し記録すると"
                "変化が見えてきます。"
            ),
        }

    old_average = (
        sum(old_values)
        / len(old_values)
    )

    recent_average = (
        sum(recent_values)
        / len(recent_values)
    )

    if old_average == 0:
        return {
            "status": "stable",
            "message": (
                "👀 発生間隔は"
                "まだ判定しにくい状態です。"
            ),
        }

    ratio = (
        recent_average
        / old_average
    )

    if ratio <= 0.75:
        return {
            "status": "increasing",
            "message": (
                "📈 最近、発生間隔が"
                "短くなっています。"
            ),
        }

    if ratio >= 1.25:
        return {
            "status": "decreasing",
            "message": (
                "📉 最近、発生間隔が"
                "長くなっています。"
            ),
        }

    return {
        "status": "stable",
        "message": (
            "⚖️ 発生間隔に"
            "大きな変化はなさそうです。"
        ),
    }


def pattern_insight(
    pattern,
    occurrences,
):
    trend = trend_analysis(
        occurrences
    )

    pattern_type = pattern.get(
        "type",
        ""
    )

    status = trend.get(
        "status"
    )

    if status == "few":
        return trend.get(
            "message"
        )

    if (
        pattern_type
        == "⚠️ 困りごと"
        and status
        == "increasing"
    ):
        return (
            "⚠️ 最近、この困りごとの"
            "発生間隔が短くなっています。"
        )

    if (
        pattern_type
        == "⚠️ 困りごと"
        and status
        == "decreasing"
    ):
        return (
            "🌱 以前より、この困りごとの"
            "発生間隔が長くなっています。"
        )

    if (
        pattern_type
        == "🌱 良いこと"
        and status
        == "increasing"
    ):
        return (
            "✨ 最近、この良い出来事が"
            "起こりやすくなっています！"
        )

    if (
        pattern_type
        == "🌱 良いこと"
        and status
        == "decreasing"
    ):
        return (
            "👀 最近、この良い出来事の"
            "間隔が少し長くなっています。"
        )

    return trend.get(
        "message"
    )


# =========================================================
# CRUD
# =========================================================

def add_pattern(
    data,
    title,
    category,
    pattern_type,
    description,
    first_date,
    time_period,
    situation,
    memo,
):
    pattern_id = create_id()

    pattern = {
        "id": pattern_id,
        "title": title,
        "category": category,
        "type": pattern_type,
        "description": description,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["patterns"].append(
        pattern
    )

    occurrence = {
        "id": create_id(),
        "pattern_id": pattern_id,
        "date": str(first_date),
        "time_period": time_period,
        "situation": situation,
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["occurrences"].append(
        occurrence
    )

    save_data(data)


def add_occurrence(
    data,
    pattern_id,
    occurrence_date,
    time_period,
    situation,
    memo,
):
    occurrence = {
        "id": create_id(),
        "pattern_id": pattern_id,
        "date": str(
            occurrence_date
        ),
        "time_period": time_period,
        "situation": situation,
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["occurrences"].append(
        occurrence
    )

    pattern = get_pattern(
        data,
        pattern_id,
    )

    if pattern:
        pattern[
            "updated_at"
        ] = now_text()

    save_data(data)

    return occurrence


def update_pattern(
    data,
    pattern_id,
    title,
    category,
    pattern_type,
    description,
):
    pattern = get_pattern(
        data,
        pattern_id,
    )

    if not pattern:
        return

    pattern["title"] = title
    pattern[
        "category"
    ] = category
    pattern[
        "type"
    ] = pattern_type
    pattern[
        "description"
    ] = description
    pattern[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    pattern_id,
):
    pattern = get_pattern(
        data,
        pattern_id,
    )

    if not pattern:
        return

    pattern[
        "favorite"
    ] = not pattern.get(
        "favorite",
        False,
    )

    pattern[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_occurrence(
    data,
    occurrence_id,
    occurrence_date,
    time_period,
    situation,
    memo,
):
    occurrence = get_occurrence(
        data,
        occurrence_id,
    )

    if not occurrence:
        return

    occurrence[
        "date"
    ] = str(
        occurrence_date
    )
    occurrence[
        "time_period"
    ] = time_period
    occurrence[
        "situation"
    ] = situation
    occurrence[
        "memo"
    ] = memo
    occurrence[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_occurrence(
    data,
    occurrence_id,
):
    data["occurrences"] = [
        occurrence
        for occurrence
        in data["occurrences"]
        if occurrence.get("id")
        != occurrence_id
    ]

    save_data(data)


def delete_pattern(
    data,
    pattern_id,
):
    data["patterns"] = [
        pattern
        for pattern
        in data["patterns"]
        if pattern.get("id")
        != pattern_id
    ]

    data["occurrences"] = [
        occurrence
        for occurrence
        in data["occurrences"]
        if occurrence.get(
            "pattern_id"
        ) != pattern_id
    ]

    save_data(data)


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
        background: rgba(80, 150, 200, 0.07);
        border: 1px solid rgba(80, 150, 200, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 150, 220, 0.18),
                rgba(120, 220, 170, 0.12)
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

    .count-box {
        text-align: center;
        padding: 18px;
        border-radius: 18px;
        background: rgba(100, 160, 220, 0.07);
        margin: 10px 0;
    }

    .count-number {
        font-size: 2.2rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

patterns = data["patterns"]
occurrences = data["occurrences"]

today = date.today()


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🔁 これ、何回目？</h1>
        <p>
            「またか」を記録すると、
            自分でも知らなかった
            パターンが見えてくる。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

st.subheader(
    "🧭 自分のパターン"
)

good_occurrences = 0
neutral_occurrences = 0
problem_occurrences = 0

for occurrence in occurrences:
    pattern = get_pattern(
        data,
        occurrence.get(
            "pattern_id"
        ),
    )

    if not pattern:
        continue

    pattern_type = pattern.get(
        "type"
    )

    if pattern_type == "🌱 良いこと":
        good_occurrences += 1

    elif (
        pattern_type
        == "⚠️ 困りごと"
    ):
        problem_occurrences += 1

    else:
        neutral_occurrences += 1


col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🔁 登録パターン",
    f"{len(patterns)}個",
)

col2.metric(
    "📝 総発生回数",
    f"{len(occurrences)}回",
)

col3.metric(
    "🌱 良いこと",
    f"{good_occurrences}回",
)

col4.metric(
    "⚠️ 困りごと",
    f"{problem_occurrences}回",
)


# =========================================================
# 注目パターン
# =========================================================

if patterns:
    totals = []

    for pattern in patterns:
        pattern_id = pattern.get(
            "id"
        )

        items = pattern_occurrences(
            data,
            pattern_id,
        )

        totals.append(
            (
                pattern,
                len(items),
                recent_occurrence_count(
                    items,
                    30,
                ),
            )
        )

    most_common = max(
        totals,
        key=lambda item: item[1],
    )

    recent_top = max(
        totals,
        key=lambda item: item[2],
    )

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "🔁 最も繰り返している\n\n"
            f"**{most_common[0].get('title', '')}**"
            f" — {most_common[1]}回"
        )

    with col2:
        st.info(
            "🔥 直近30日で多い\n\n"
            f"**{recent_top[0].get('title', '')}**"
            f" — {recent_top[2]}回"
        )


# =========================================================
# 新しいパターン
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい「また」を登録"
)

with st.form(
    "new_pattern_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "🔁 何が繰り返してる？",
        placeholder=(
            "例：寝る前に"
            "アイデアを思いつく"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

    with col2:
        pattern_type = (
            st.selectbox(
                "これはどんなこと？",
                PATTERN_TYPES,
            )
        )

    description = st.text_area(
        "📝 このパターンについて",
        placeholder=(
            "どんな出来事なのか、"
            "簡単にメモしておこう。"
        ),
    )

    st.markdown(
        "#### 1回目の記録"
    )

    col1, col2 = st.columns(2)

    with col1:
        first_date = st.date_input(
            "📅 日付",
            value=today,
            max_value=today,
        )

    with col2:
        first_time_period = (
            st.selectbox(
                "🕐 時間帯",
                TIME_PERIODS,
            )
        )

    first_situation = (
        st.text_input(
            "📍 どんな状況だった？",
            placeholder=(
                "例：ベッドで"
                "スマホを見ていた"
            ),
        )
    )

    first_memo = st.text_area(
        "💭 その時のメモ",
        placeholder=(
            "例：新しいアプリ案を"
            "思いついた"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🔁 パターンを登録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "出来事を入力してね。"
            )

        else:
            add_pattern(
                data=data,
                title=title.strip(),
                category=category,
                pattern_type=(
                    pattern_type
                ),
                description=(
                    description.strip()
                ),
                first_date=(
                    first_date
                ),
                time_period=(
                    first_time_period
                ),
                situation=(
                    first_situation.strip()
                ),
                memo=(
                    first_memo.strip()
                ),
            )

            st.rerun()


# =========================================================
# パターンカード
# =========================================================

st.divider()

st.subheader(
    "👀 観察しているパターン"
)

if not patterns:
    st.info(
        "まだパターンがありません。"
        "まず一つ登録してみよう！"
    )

else:
    sorted_patterns = sorted(
        patterns,
        key=lambda pattern: (
            pattern.get(
                "favorite",
                False,
            ),
            pattern.get(
                "updated_at",
                "",
            ),
        ),
        reverse=True,
    )

    for pattern in sorted_patterns:
        pattern_id = pattern.get(
            "id",
            "",
        )

        items = pattern_occurrences(
            data,
            pattern_id,
        )

        count = len(items)

        last_date = (
            last_occurrence_date(
                items
            )
        )

        average = (
            average_interval(
                items
            )
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [8, 1]
            )

            with col1:
                st.subheader(
                    pattern.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if pattern.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "pattern_fav_"
                        + pattern_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        pattern_id,
                    )
                    st.rerun()

            st.caption(
                pattern.get(
                    "type",
                    ""
                )
                + " ｜ "
                + pattern.get(
                    "category",
                    ""
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "🔁 これまで",
                f"{count}回",
            )

            col2.metric(
                "📅 前回",
                (
                    days_ago(
                        str(last_date)
                    )
                    if last_date
                    else "-"
                ),
            )

            col3.metric(
                "⏱️ 平均間隔",
                (
                    interval_text(
                        average
                    )
                    if average
                    is not None
                    else "-"
                ),
            )

            if count >= 2:
                st.info(
                    pattern_insight(
                        pattern,
                        items,
                    )
                )

            with st.expander(
                "🔁 また起きた！"
            ):
                occurrence_date = (
                    st.date_input(
                        "📅 いつ？",
                        value=today,
                        max_value=today,
                        key=(
                            "occ_date_"
                            + pattern_id
                        ),
                    )
                )

                time_period = (
                    st.selectbox(
                        "🕐 時間帯",
                        TIME_PERIODS,
                        key=(
                            "occ_time_"
                            + pattern_id
                        ),
                    )
                )

                situation = (
                    st.text_input(
                        "📍 状況",
                        placeholder=(
                            "何をしていた？"
                        ),
                        key=(
                            "occ_situation_"
                            + pattern_id
                        ),
                    )
                )

                memo = st.text_area(
                    "💭 メモ",
                    key=(
                        "occ_memo_"
                        + pattern_id
                    ),
                )

                if st.button(
                    "🔁 記録する",
                    key=(
                        "occ_save_"
                        + pattern_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    previous_last = (
                        last_occurrence_date(
                            items
                        )
                    )

                    add_occurrence(
                        data=data,
                        pattern_id=(
                            pattern_id
                        ),
                        occurrence_date=(
                            occurrence_date
                        ),
                        time_period=(
                            time_period
                        ),
                        situation=(
                            situation.strip()
                        ),
                        memo=memo.strip(),
                    )

                    new_count = (
                        count + 1
                    )

                    st.session_state[
                        "last_occurrence_message"
                    ] = {
                        "pattern_id": (
                            pattern_id
                        ),
                        "count": new_count,
                        "previous_last": (
                            str(
                                previous_last
                            )
                            if previous_last
                            else None
                        ),
                        "date": str(
                            occurrence_date
                        ),
                    }

                    st.rerun()

            with st.expander(
                "📊 このパターンを分析"
            ):
                if not items:
                    st.caption(
                        "記録がありません。"
                    )

                else:
                    weekday_data = (
                        weekday_counts(
                            items
                        )
                    )

                    time_data = (
                        time_period_counts(
                            items
                        )
                    )

                    st.write(
                        "**📅 曜日別**"
                    )

                    weekday_df = (
                        pd.DataFrame(
                            {
                                "曜日": list(
                                    weekday_data.keys()
                                ),
                                "回数": list(
                                    weekday_data.values()
                                ),
                            }
                        )
                        .set_index(
                            "曜日"
                        )
                    )

                    st.bar_chart(
                        weekday_df
                    )

                    if sum(
                        weekday_data.values()
                    ) > 0:
                        top_weekday = max(
                            weekday_data,
                            key=(
                                weekday_data.get
                            ),
                        )

                        st.caption(
                            f"📅 最も多いのは"
                            f"{top_weekday}曜日 "
                            f"({weekday_data[top_weekday]}回)"
                        )

                    st.write(
                        "**🕐 時間帯別**"
                    )

                    time_df = (
                        pd.DataFrame(
                            {
                                "時間帯": list(
                                    time_data.keys()
                                ),
                                "回数": list(
                                    time_data.values()
                                ),
                            }
                        )
                        .set_index(
                            "時間帯"
                        )
                    )

                    st.bar_chart(
                        time_df
                    )

                    total_times = sum(
                        time_data.values()
                    )

                    if total_times:
                        top_time = max(
                            time_data,
                            key=time_data.get,
                        )

                        percentage = (
                            time_data[
                                top_time
                            ]
                            / total_times
                            * 100
                        )

                        st.caption(
                            f"👀 {percentage:.0f}%が"
                            f"{top_time}に"
                            "起きています。"
                        )

                    gap_values = intervals(
                        items
                    )

                    if gap_values:
                        st.write(
                            "**⏱️ 発生間隔**"
                        )

                        gap_rows = []

                        dates = (
                            occurrence_dates(
                                items
                            )
                        )

                        for index in range(
                            1,
                            len(dates),
                        ):
                            gap_rows.append(
                                {
                                    "区間": (
                                        f"{index}回目"
                                        f" → "
                                        f"{index + 1}回目"
                                    ),
                                    "日数": (
                                        dates[index]
                                        - dates[
                                            index - 1
                                        ]
                                    ).days,
                                }
                            )

                        st.dataframe(
                            pd.DataFrame(
                                gap_rows
                            ),
                            hide_index=True,
                            use_container_width=True,
                        )


# =========================================================
# 記録直後メッセージ
# =========================================================

last_message = (
    st.session_state.get(
        "last_occurrence_message"
    )
)

if last_message:
    pattern = get_pattern(
        data,
        last_message.get(
            "pattern_id"
        ),
    )

    if pattern:
        st.success(
            "🎉 記録しました！\n\n"
            f"**「{pattern.get('title', '')}」"
            f"は今回で"
            f"{last_message.get('count')}回目！**"
        )

        previous = parse_date(
            last_message.get(
                "previous_last"
            )
        )

        current = parse_date(
            last_message.get(
                "date"
            )
        )

        if previous and current:
            difference = (
                current
                - previous
            ).days

            if difference == 0:
                st.caption(
                    "🔁 前回と同じ日に"
                    "もう一度起きました。"
                )
            else:
                st.caption(
                    f"📅 前回から"
                    f"{difference}日ぶりです。"
                )

    if st.button(
        "OK",
        key="clear_last_message",
    ):
        del st.session_state[
            "last_occurrence_message"
        ]
        st.rerun()


# =========================================================
# ランキング
# =========================================================

if patterns:
    st.divider()

    st.subheader(
        "🏆 パターンランキング"
    )

    ranking_rows = []

    for pattern in patterns:
        items = pattern_occurrences(
            data,
            pattern.get(
                "id"
            ),
        )

        ranking_rows.append(
            {
                "pattern": pattern,
                "total": len(items),
                "recent": (
                    recent_occurrence_count(
                        items,
                        30,
                    )
                ),
            }
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "#### 🔁 累計"
        )

        total_ranking = sorted(
            ranking_rows,
            key=lambda row: row[
                "total"
            ],
            reverse=True,
        )

        for rank, row in enumerate(
            total_ranking[:5],
            start=1,
        ):
            st.write(
                f"**{rank}. "
                f"{row['pattern'].get('title', '')}**"
            )

            st.caption(
                f"{row['total']}回"
            )

    with col2:
        st.markdown(
            "#### 🔥 直近30日"
        )

        recent_ranking = sorted(
            ranking_rows,
            key=lambda row: row[
                "recent"
            ],
            reverse=True,
        )

        for rank, row in enumerate(
            recent_ranking[:5],
            start=1,
        ):
            st.write(
                f"**{rank}. "
                f"{row['pattern'].get('title', '')}**"
            )

            st.caption(
                f"{row['recent']}回"
            )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    pattern
    for pattern
    in patterns
    if pattern.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 観察中"
    )

    for pattern in favorites:
        items = pattern_occurrences(
            data,
            pattern.get(
                "id"
            ),
        )

        st.write(
            f"⭐ **{pattern.get('title', '')}**"
        )

        st.caption(
            f"{pattern.get('type', '')}"
            f" ｜ 累計{len(items)}回"
        )


# =========================================================
# 過去ガチャ
# =========================================================

old_patterns = []

for pattern in patterns:
    items = pattern_occurrences(
        data,
        pattern.get(
            "id"
        ),
    )

    first_date = (
        first_occurrence_date(
            items
        )
    )

    if (
        first_date
        and (
            today
            - first_date
        ).days >= 30
    ):
        old_patterns.append(
            pattern
        )

if old_patterns:
    st.divider()

    st.subheader(
        "🎲 こんなこと繰り返してました"
    )

    old_ids = [
        pattern.get(
            "id"
        )
        for pattern
        in old_patterns
    ]

    random_id = (
        st.session_state.get(
            "random_pattern_id"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_pattern_id"
        ] = random_id

    random_pattern = get_pattern(
        data,
        random_id,
    )

    if random_pattern:
        items = pattern_occurrences(
            data,
            random_id,
        )

        first_date = (
            first_occurrence_date(
                items
            )
        )

        with st.container(
            border=True
        ):
            st.caption(
                random_pattern.get(
                    "type",
                    ""
                )
                + " ｜ "
                + random_pattern.get(
                    "category",
                    ""
                )
            )

            st.subheader(
                random_pattern.get(
                    "title",
                    "",
                )
            )

            st.metric(
                "🔁 これまで",
                f"{len(items)}回",
            )

            if first_date:
                age = (
                    today
                    - first_date
                ).days

                st.caption(
                    f"最初の記録は"
                    f"{age}日前"
                )

        if st.button(
            "🎲 別のパターン",
            use_container_width=True,
        ):
            alternatives = [
                pattern_id
                for pattern_id
                in old_ids
                if pattern_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_pattern_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# パターン図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 パターン図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "アイデア、眠い、忘れる……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="library_category",
        )
    )

with col2:
    type_filter = (
        st.selectbox(
            "種類",
            ["すべて"]
            + PATTERN_TYPES,
            key="library_type",
        )
    )

favorite_only = st.checkbox(
    "⭐ お気に入りだけ",
)

filtered_patterns = []

for pattern in patterns:
    if (
        category_filter
        != "すべて"
        and pattern.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        type_filter
        != "すべて"
        and pattern.get(
            "type"
        ) != type_filter
    ):
        continue

    if (
        favorite_only
        and not pattern.get(
            "favorite",
            False,
        )
    ):
        continue

    searchable = " ".join(
        [
            pattern.get(
                "title",
                "",
            ),
            pattern.get(
                "description",
                "",
            ),
            pattern.get(
                "category",
                "",
            ),
            pattern.get(
                "type",
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

    filtered_patterns.append(
        pattern
    )

if not filtered_patterns:
    st.info(
        "条件に合うパターンは"
        "ありません。"
    )

else:
    rows = []

    for pattern in filtered_patterns:
        items = pattern_occurrences(
            data,
            pattern.get(
                "id"
            ),
        )

        last_date = (
            last_occurrence_date(
                items
            )
        )

        average = (
            average_interval(
                items
            )
        )

        rows.append(
            {
                "出来事": pattern.get(
                    "title",
                    "",
                ),
                "種類": pattern.get(
                    "type",
                    "",
                ),
                "カテゴリー": (
                    pattern.get(
                        "category",
                        "",
                    )
                ),
                "回数": len(items),
                "前回": (
                    days_ago(
                        str(last_date)
                    )
                    if last_date
                    else "-"
                ),
                "平均間隔": (
                    interval_text(
                        average
                    )
                    if average
                    is not None
                    else "-"
                ),
                "⭐": (
                    "⭐"
                    if pattern.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    df = pd.DataFrame(
        rows
    )

    if not df.empty:
        df = df.sort_values(
            "回数",
            ascending=False,
        )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・削除"
):
    if not patterns:
        st.caption(
            "まだパターンがありません。"
        )

    pattern_options = {
        (
            f"{pattern.get('title', '')}"
            f" ｜ {pattern.get('type', '')}"
        ): pattern.get("id")
        for pattern in patterns
    }

    if pattern_options:
        selected_label = (
            st.selectbox(
                "編集するパターン",
                list(
                    pattern_options.keys()
                ),
            )
        )

        selected_id = (
            pattern_options[
                selected_label
            ]
        )

        selected = get_pattern(
            data,
            selected_id,
        )

        if selected:
            st.markdown(
                "#### ✏️ パターン"
            )

            edit_title = st.text_input(
                "出来事",
                value=selected.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_pattern_title_"
                    + selected_id
                ),
            )

            old_category = selected.get(
                "category",
                "✨ その他",
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
                    index=category_index,
                    key=(
                        "edit_pattern_category_"
                        + selected_id
                    ),
                )
            )

            old_type = selected.get(
                "type",
                "😐 どちらでもない",
            )

            type_index = (
                PATTERN_TYPES.index(
                    old_type
                )
                if old_type
                in PATTERN_TYPES
                else 1
            )

            edit_type = st.selectbox(
                "種類",
                PATTERN_TYPES,
                index=type_index,
                key=(
                    "edit_pattern_type_"
                    + selected_id
                ),
            )

            edit_description = (
                st.text_area(
                    "説明",
                    value=selected.get(
                        "description",
                        "",
                    ),
                    key=(
                        "edit_description_"
                        + selected_id
                    ),
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 パターンを保存",
                    key=(
                        "save_pattern_"
                        + selected_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "出来事を入力してね。"
                        )
                    else:
                        update_pattern(
                            data=data,
                            pattern_id=(
                                selected_id
                            ),
                            title=(
                                edit_title.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            pattern_type=(
                                edit_type
                            ),
                            description=(
                                edit_description.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if selected.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_pattern_fav_"
                        + selected_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        selected_id,
                    )
                    st.rerun()

            st.divider()

            st.markdown(
                "#### 📝 発生履歴"
            )

            selected_occurrences = (
                pattern_occurrences(
                    data,
                    selected_id,
                )
            )

            if not selected_occurrences:
                st.caption(
                    "発生履歴はありません。"
                )

            else:
                occurrence_options = {}

                for index, occurrence in enumerate(
                    selected_occurrences,
                    start=1,
                ):
                    label = (
                        f"{index}回目 ｜ "
                        f"{format_date(occurrence.get('date'))}"
                        f" ｜ "
                        f"{occurrence.get('time_period', '')}"
                    )

                    occurrence_options[
                        label
                    ] = occurrence.get(
                        "id"
                    )

                occurrence_label = (
                    st.selectbox(
                        "編集する発生記録",
                        list(
                            occurrence_options.keys()
                        ),
                        key=(
                            "occurrence_select_"
                            + selected_id
                        ),
                    )
                )

                occurrence_id = (
                    occurrence_options[
                        occurrence_label
                    ]
                )

                occurrence = (
                    get_occurrence(
                        data,
                        occurrence_id,
                    )
                )

                if occurrence:
                    current_date = (
                        parse_date(
                            occurrence.get(
                                "date"
                            )
                        )
                        or today
                    )

                    edit_occ_date = (
                        st.date_input(
                            "発生日",
                            value=current_date,
                            max_value=today,
                            key=(
                                "edit_occ_date_"
                                + occurrence_id
                            ),
                        )
                    )

                    old_period = (
                        occurrence.get(
                            "time_period",
                            "🌙 夜",
                        )
                    )

                    period_index = (
                        TIME_PERIODS.index(
                            old_period
                        )
                        if old_period
                        in TIME_PERIODS
                        else 3
                    )

                    edit_occ_period = (
                        st.selectbox(
                            "時間帯",
                            TIME_PERIODS,
                            index=period_index,
                            key=(
                                "edit_occ_period_"
                                + occurrence_id
                            ),
                        )
                    )

                    edit_situation = (
                        st.text_input(
                            "状況",
                            value=occurrence.get(
                                "situation",
                                "",
                            ),
                            key=(
                                "edit_occ_situation_"
                                + occurrence_id
                            ),
                        )
                    )

                    edit_memo = (
                        st.text_area(
                            "メモ",
                            value=occurrence.get(
                                "memo",
                                "",
                            ),
                            key=(
                                "edit_occ_memo_"
                                + occurrence_id
                            ),
                        )
                    )

                    if st.button(
                        "💾 発生記録を保存",
                        key=(
                            "save_occurrence_"
                            + occurrence_id
                        ),
                        use_container_width=True,
                    ):
                        update_occurrence(
                            data=data,
                            occurrence_id=(
                                occurrence_id
                            ),
                            occurrence_date=(
                                edit_occ_date
                            ),
                            time_period=(
                                edit_occ_period
                            ),
                            situation=(
                                edit_situation.strip()
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

                    delete_occ_confirm = (
                        st.checkbox(
                            "この発生記録を削除",
                            key=(
                                "delete_occ_confirm_"
                                + occurrence_id
                            ),
                        )
                    )

                    if st.button(
                        "🗑️ 発生記録を削除",
                        key=(
                            "delete_occ_"
                            + occurrence_id
                        ),
                        disabled=(
                            not delete_occ_confirm
                        ),
                        use_container_width=True,
                    ):
                        delete_occurrence(
                            data,
                            occurrence_id,
                        )

                        st.rerun()

            st.divider()

            st.markdown(
                "#### 🗑️ パターンを完全削除"
            )

            st.warning(
                "パターンを削除すると、"
                "その発生履歴もすべて"
                "削除されます。"
            )

            delete_confirm = (
                st.checkbox(
                    "パターンと履歴を"
                    "すべて削除する",
                    key=(
                        "delete_pattern_confirm_"
                        + selected_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_pattern_"
                    + selected_id
                ),
                disabled=(
                    not delete_confirm
                ),
                use_container_width=True,
            ):
                delete_pattern(
                    data,
                    selected_id,
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
            "how_many_times_"
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
    "🔁 一度なら偶然。"
    "繰り返せば、それは"
    "自分のパターンかもしれない。"
)

st.caption(
    "👀 「またか」を記録すると、"
    "自分でも知らなかった"
    "自分が見えてくる。"
)
