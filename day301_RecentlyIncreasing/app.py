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
    page_title="最近これ増えてない？",
    page_icon="📈",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "tracker.json",
)

CATEGORIES = [
    "🍴 食事・飲み物",
    "📱 スマホ・SNS",
    "💰 お金",
    "🏃 運動",
    "📚 学習",
    "💻 仕事・開発",
    "😴 睡眠・休息",
    "🎮 趣味",
    "🏠 生活",
    "✨ その他",
]

STATUSES = [
    "👀 観察中",
    "📦 観察終了",
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
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime("%Y/%m/%d")


def format_value(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0"

    if number.is_integer():
        return f"{int(number):,}"

    return f"{number:,.2f}".rstrip(
        "0"
    ).rstrip(".")


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "topics": [],
        "records": [],
        "insights": [],
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

        if not isinstance(data, dict):
            data = empty_data()

        data.setdefault(
            "topics",
            [],
        )
        data.setdefault(
            "records",
            [],
        )
        data.setdefault(
            "insights",
            [],
        )

        for topic in data["topics"]:
            if not topic.get("id"):
                topic["id"] = create_id()

            topic.setdefault(
                "name",
                "",
            )
            topic.setdefault(
                "category",
                "✨ その他",
            )
            topic.setdefault(
                "unit",
                "回",
            )
            topic.setdefault(
                "memo",
                "",
            )
            topic.setdefault(
                "status",
                "👀 観察中",
            )
            topic.setdefault(
                "created_at",
                now_text(),
            )
            topic.setdefault(
                "updated_at",
                topic.get(
                    "created_at",
                    now_text(),
                ),
            )

        for record in data["records"]:
            if not record.get("id"):
                record["id"] = create_id()

            record.setdefault(
                "topic_id",
                "",
            )
            record.setdefault(
                "date",
                str(date.today()),
            )
            record.setdefault(
                "time",
                "12:00",
            )
            record.setdefault(
                "value",
                0,
            )
            record.setdefault(
                "memo",
                "",
            )
            record.setdefault(
                "created_at",
                now_text(),
            )
            record.setdefault(
                "updated_at",
                record.get(
                    "created_at",
                    now_text(),
                ),
            )

        for insight in data["insights"]:
            if not insight.get("id"):
                insight["id"] = create_id()

            insight.setdefault(
                "topic_id",
                "",
            )
            insight.setdefault(
                "date",
                str(date.today()),
            )
            insight.setdefault(
                "observation",
                "",
            )
            insight.setdefault(
                "reason",
                "",
            )
            insight.setdefault(
                "next",
                "",
            )
            insight.setdefault(
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
# 取得系
# =========================================================

def get_topic(
    data,
    topic_id,
):
    return next(
        (
            topic
            for topic in data["topics"]
            if topic.get("id")
            == topic_id
        ),
        None,
    )


def get_record(
    data,
    record_id,
):
    return next(
        (
            record
            for record in data["records"]
            if record.get("id")
            == record_id
        ),
        None,
    )


def topic_records(
    data,
    topic_id,
):
    return [
        record
        for record in data["records"]
        if record.get("topic_id")
        == topic_id
    ]


def topic_insights(
    data,
    topic_id,
):
    return [
        insight
        for insight in data["insights"]
        if insight.get("topic_id")
        == topic_id
    ]


def topic_label(topic):
    return (
        f"{topic.get('name', '')} "
        f"({topic.get('unit', '')})"
    )


# =========================================================
# 集計
# =========================================================

def total_between(
    records,
    start_date,
    end_date,
):
    total = 0.0

    for record in records:
        record_date = parse_date(
            record.get("date")
        )

        if (
            record_date
            and start_date
            <= record_date
            <= end_date
        ):
            total += safe_float(
                record.get("value")
            )

    return total


def recent_comparison(
    records,
    today_value,
):
    recent_start = (
        today_value
        - timedelta(days=6)
    )

    previous_end = (
        recent_start
        - timedelta(days=1)
    )

    previous_start = (
        previous_end
        - timedelta(days=6)
    )

    recent = total_between(
        records,
        recent_start,
        today_value,
    )

    previous = total_between(
        records,
        previous_start,
        previous_end,
    )

    difference = (
        recent - previous
    )

    if previous == 0:
        percentage = None
    else:
        percentage = (
            difference
            / previous
            * 100
        )

    return {
        "recent": recent,
        "previous": previous,
        "difference": difference,
        "percentage": percentage,
        "recent_start": recent_start,
        "previous_start": previous_start,
        "previous_end": previous_end,
    }


def change_text(
    comparison,
    unit,
):
    recent = comparison["recent"]
    previous = comparison["previous"]
    difference = comparison["difference"]
    percentage = comparison["percentage"]

    if previous == 0:
        if recent == 0:
            return "➡ 変化なし"

        return (
            f"🆕 0 → "
            f"{format_value(recent)}{unit}"
        )

    if difference > 0:
        return (
            f"📈 +{format_value(difference)}{unit}"
            f" / +{percentage:.1f}%"
        )

    if difference < 0:
        return (
            f"📉 {format_value(difference)}{unit}"
            f" / {percentage:.1f}%"
        )

    return "➡ 変化なし"


def percentage_for_ranking(
    comparison,
):
    previous = comparison[
        "previous"
    ]
    recent = comparison[
        "recent"
    ]

    if previous == 0:
        if recent > 0:
            return None

        return 0.0

    return comparison[
        "percentage"
    ]


def daily_dataframe(
    records,
    days=30,
):
    end_date = date.today()

    start_date = (
        end_date
        - timedelta(
            days=days - 1
        )
    )

    totals = {}

    current = start_date

    while current <= end_date:
        totals[current] = 0.0
        current += timedelta(days=1)

    for record in records:
        record_date = parse_date(
            record.get("date")
        )

        if (
            record_date
            and record_date in totals
        ):
            totals[
                record_date
            ] += safe_float(
                record.get("value")
            )

    return pd.DataFrame(
        {
            "日付": list(
                totals.keys()
            ),
            "量": list(
                totals.values()
            ),
        }
    ).set_index(
        "日付"
    )


def first_record_date(
    records,
):
    dates = [
        parse_date(
            record.get("date")
        )
        for record in records
    ]

    dates = [
        value
        for value in dates
        if value
    ]

    if not dates:
        return None

    return min(dates)


# =========================================================
# CRUD
# =========================================================

def add_topic(
    data,
    name,
    category,
    unit,
    memo,
):
    topic = {
        "id": create_id(),
        "name": name,
        "category": category,
        "unit": unit,
        "memo": memo,
        "status": "👀 観察中",
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["topics"].append(
        topic
    )

    save_data(data)

    return topic


def add_record(
    data,
    topic_id,
    record_date,
    record_time,
    value,
    memo,
):
    record = {
        "id": create_id(),
        "topic_id": topic_id,
        "date": str(record_date),
        "time": record_time,
        "value": float(value),
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["records"].append(
        record
    )

    save_data(data)

    return record


def add_insight(
    data,
    topic_id,
    insight_date,
    observation,
    reason,
    next_action,
):
    insight = {
        "id": create_id(),
        "topic_id": topic_id,
        "date": str(insight_date),
        "observation": observation,
        "reason": reason,
        "next": next_action,
        "created_at": now_text(),
    }

    data["insights"].append(
        insight
    )

    save_data(data)


def delete_topic(
    data,
    topic_id,
):
    data["topics"] = [
        topic
        for topic in data["topics"]
        if topic.get("id")
        != topic_id
    ]

    data["records"] = [
        record
        for record in data["records"]
        if record.get("topic_id")
        != topic_id
    ]

    data["insights"] = [
        insight
        for insight in data["insights"]
        if insight.get("topic_id")
        != topic_id
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

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background: rgba(80, 150, 220, 0.06);
        border: 1px solid rgba(80, 150, 220, 0.15);
    }

    .chapter-card {
        text-align: center;
        padding: 32px;
        margin-bottom: 25px;
        border-radius: 26px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 160, 230, .14),
                rgba(100, 200, 150, .10)
            );
    }

    .topic-card {
        padding: 18px;
        border-radius: 18px;
        border:
            1px solid
            rgba(100, 150, 180, .15);
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 準備
# =========================================================

data = load_data()

topics = data["topics"]
records = data["records"]

today = date.today()


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="chapter-card">
        <div style="font-size:1.1rem;">
            🌅 DAY 301
        </div>
        <h1>📈 最近これ増えてない？</h1>
        <h3>NEW CHAPTER</h3>
        <p>
            300の先で、またひとつ作る。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "👀 **「なんとなく増えた気がする」を、"
    "記録から確かめる。**\n\n"
    "増えた・減ったに良い悪いはつけません。"
)


# =========================================================
# タブ
# =========================================================

tab_today, tab_analysis, tab_library, tab_manage = (
    st.tabs(
        [
            "🏠 記録",
            "📊 変化を見る",
            "📚 観察図鑑",
            "🛠️ 管理",
        ]
    )
)


# =========================================================
# TAB 1：記録
# =========================================================

with tab_today:

    st.subheader(
        "👀 新しい観察テーマ"
    )

    with st.form(
        "new_topic",
        clear_on_submit=True,
    ):
        topic_name = st.text_input(
            "何を観察する？",
            placeholder=(
                "例：コーヒー"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            topic_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                )
            )

        with col2:
            topic_unit = (
                st.text_input(
                    "単位",
                    value="回",
                    placeholder=(
                        "回 / 分 / 円 / 個"
                    ),
                )
            )

        topic_memo = st.text_area(
            "なぜ気になった？（任意）",
            placeholder=(
                "最近増えた気がする"
            ),
        )

        if st.form_submit_button(
            "👀 観察を始める",
            type="primary",
            use_container_width=True,
        ):
            if not topic_name.strip():
                st.warning(
                    "テーマ名を入力してね。"
                )

            elif not topic_unit.strip():
                st.warning(
                    "単位を入力してね。"
                )

            else:
                add_topic(
                    data=data,
                    name=topic_name.strip(),
                    category=topic_category,
                    unit=topic_unit.strip(),
                    memo=topic_memo.strip(),
                )

                st.rerun()

    st.divider()

    active_topics = [
        topic
        for topic in topics
        if topic.get(
            "status"
        ) == "👀 観察中"
    ]

    st.subheader(
        "➕ 今日の量を記録"
    )

    if not active_topics:
        st.info(
            "まず観察テーマを"
            "登録してみよう。"
        )

    else:
        topic_options = {
            topic_label(topic):
            topic.get("id")
            for topic in active_topics
        }

        selected_label = (
            st.selectbox(
                "テーマ",
                list(
                    topic_options.keys()
                ),
                key="record_topic",
            )
        )

        selected_topic_id = (
            topic_options[
                selected_label
            ]
        )

        selected_topic = get_topic(
            data,
            selected_topic_id,
        )

        with st.form(
            "new_record",
            clear_on_submit=True,
        ):
            col1, col2 = (
                st.columns(2)
            )

            with col1:
                record_date = (
                    st.date_input(
                        "日付",
                        value=today,
                        max_value=today,
                    )
                )

            with col2:
                record_time = (
                    st.time_input(
                        "時刻",
                        value=(
                            datetime.now()
                            .replace(
                                second=0,
                                microsecond=0,
                            )
                            .time()
                        ),
                    )
                )

            record_value = (
                st.number_input(
                    (
                        "量 "
                        f"（{selected_topic.get('unit')}）"
                    ),
                    min_value=0.0,
                    value=1.0,
                    step=1.0,
                )
            )

            record_memo = (
                st.text_input(
                    "メモ（任意）",
                    placeholder=(
                        "午後に2杯"
                    ),
                )
            )

            if st.form_submit_button(
                "＋ 記録",
                type="primary",
                use_container_width=True,
            ):
                add_record(
                    data=data,
                    topic_id=(
                        selected_topic_id
                    ),
                    record_date=(
                        record_date
                    ),
                    record_time=(
                        record_time.strftime(
                            "%H:%M"
                        )
                    ),
                    value=record_value,
                    memo=record_memo.strip(),
                )

                st.rerun()

        selected_records = (
            topic_records(
                data,
                selected_topic_id,
            )
        )

        today_total = total_between(
            selected_records,
            today,
            today,
        )

        st.success(
            f"📍 今日の合計："
            f"**{format_value(today_total)}"
            f"{selected_topic.get('unit')}**"
        )

    st.divider()

    st.subheader(
        "🕒 今日の記録"
    )

    today_records = [
        record
        for record in records
        if record.get(
            "date"
        ) == str(today)
    ]

    if not today_records:
        st.caption(
            "今日はまだ記録がありません。"
        )

    else:
        today_records = sorted(
            today_records,
            key=lambda item: (
                item.get(
                    "time",
                    ""
                )
            ),
            reverse=True,
        )

        for record in today_records:
            topic = get_topic(
                data,
                record.get(
                    "topic_id"
                ),
            )

            if not topic:
                continue

            with st.container(
                border=True
            ):
                st.write(
                    f"**{topic.get('name')}** "
                    f"— "
                    f"{format_value(record.get('value'))}"
                    f"{topic.get('unit')}"
                )

                st.caption(
                    f"🕒 {record.get('time', '-')}"
                    f" ｜ "
                    f"{topic.get('category')}"
                )

                if record.get(
                    "memo"
                ):
                    st.caption(
                        "💭 "
                        + record.get(
                            "memo"
                        )
                    )


# =========================================================
# TAB 2：分析
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 最近どう？"
    )

    if not topics:
        st.info(
            "記録が増えると、"
            "ここに変化が見えてきます。"
        )

    else:
        comparison_rows = []

        for topic in topics:
            topic_data = (
                topic_records(
                    data,
                    topic.get("id"),
                )
            )

            comparison = (
                recent_comparison(
                    topic_data,
                    today,
                )
            )

            comparison_rows.append(
                {
                    "topic": topic,
                    "comparison": (
                        comparison
                    ),
                }
            )

        for row in comparison_rows:
            topic = row["topic"]
            comparison = (
                row["comparison"]
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### {topic.get('name')}"
                )

                st.caption(
                    f"{topic.get('category')}"
                    f" ｜ 単位："
                    f"{topic.get('unit')}"
                )

                c1, c2 = (
                    st.columns(2)
                )

                c1.metric(
                    "前の7日",
                    (
                        f"{format_value(comparison['previous'])}"
                        f"{topic.get('unit')}"
                    ),
                )

                c2.metric(
                    "最近7日",
                    (
                        f"{format_value(comparison['recent'])}"
                        f"{topic.get('unit')}"
                    ),
                )

                st.write(
                    "**"
                    + change_text(
                        comparison,
                        topic.get(
                            "unit",
                            "",
                        ),
                    )
                    + "**"
                )

        # -----------------------------------------
        # ランキング
        # -----------------------------------------

        st.divider()

        st.subheader(
            "🔥 最近増えているもの"
        )

        increasing = []

        decreasing = []

        changed = []

        for row in comparison_rows:
            topic = row["topic"]
            comparison = (
                row["comparison"]
            )

            percent = (
                percentage_for_ranking(
                    comparison
                )
            )

            difference = (
                comparison[
                    "difference"
                ]
            )

            ranking_row = {
                "topic": topic,
                "comparison": (
                    comparison
                ),
                "percent": percent,
            }

            if difference > 0:
                increasing.append(
                    ranking_row
                )

            elif difference < 0:
                decreasing.append(
                    ranking_row
                )

            if difference != 0:
                changed.append(
                    ranking_row
                )

        def ranking_score(row):
            if row["percent"] is None:
                return float("inf")

            return abs(
                row["percent"]
            )

        increasing.sort(
            key=ranking_score,
            reverse=True,
        )

        decreasing.sort(
            key=ranking_score,
            reverse=True,
        )

        changed.sort(
            key=ranking_score,
            reverse=True,
        )

        if not increasing:
            st.caption(
                "最近増えているテーマは"
                "まだありません。"
            )

        else:
            for index, row in enumerate(
                increasing[:5],
                start=1,
            ):
                topic = row["topic"]
                comparison = (
                    row["comparison"]
                )

                st.write(
                    f"**{index}. "
                    f"{topic.get('name')}**"
                    f"　"
                    f"{change_text(comparison, topic.get('unit'))}"
                )

        st.markdown(
            "#### 📉 最近減っているもの"
        )

        if not decreasing:
            st.caption(
                "最近減っているテーマは"
                "まだありません。"
            )

        else:
            for index, row in enumerate(
                decreasing[:5],
                start=1,
            ):
                topic = row["topic"]
                comparison = (
                    row["comparison"]
                )

                st.write(
                    f"**{index}. "
                    f"{topic.get('name')}**"
                    f"　"
                    f"{change_text(comparison, topic.get('unit'))}"
                )

        st.markdown(
            "#### 🧭 変化が大きいもの"
        )

        if not changed:
            st.caption(
                "もう少し記録すると"
                "変化が見えてきます。"
            )

        else:
            for index, row in enumerate(
                changed[:5],
                start=1,
            ):
                topic = row["topic"]

                st.write(
                    f"**{index}. "
                    f"{topic.get('name')}**"
                    f"　"
                    f"{change_text(row['comparison'], topic.get('unit'))}"
                )

        # -----------------------------------------
        # 詳細
        # -----------------------------------------

        st.divider()

        st.subheader(
            "📈 テーマ詳細"
        )

        detail_options = {
            topic_label(topic):
            topic.get("id")
            for topic in topics
        }

        detail_label = (
            st.selectbox(
                "詳しく見るテーマ",
                list(
                    detail_options.keys()
                ),
                key="detail_topic",
            )
        )

        detail_topic_id = (
            detail_options[
                detail_label
            ]
        )

        detail_topic = get_topic(
            data,
            detail_topic_id,
        )

        detail_records = (
            topic_records(
                data,
                detail_topic_id,
            )
        )

        comparison = (
            recent_comparison(
                detail_records,
                today,
            )
        )

        current_month_start = (
            today.replace(day=1)
        )

        current_month_total = (
            total_between(
                detail_records,
                current_month_start,
                today,
            )
        )

        today_total = (
            total_between(
                detail_records,
                today,
                today,
            )
        )

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "今日",
            (
                f"{format_value(today_total)}"
                f"{detail_topic.get('unit')}"
            ),
        )

        c2.metric(
            "最近7日",
            (
                f"{format_value(comparison['recent'])}"
                f"{detail_topic.get('unit')}"
            ),
        )

        c3.metric(
            "前の7日",
            (
                f"{format_value(comparison['previous'])}"
                f"{detail_topic.get('unit')}"
            ),
        )

        c4.metric(
            "今月",
            (
                f"{format_value(current_month_total)}"
                f"{detail_topic.get('unit')}"
            ),
        )

        chart_df = (
            daily_dataframe(
                detail_records,
                days=30,
            )
        )

        st.markdown(
            "#### 📊 最近30日"
        )

        st.line_chart(
            chart_df
        )

        # -----------------------------------------
        # 気づき
        # -----------------------------------------

        st.markdown(
            "#### 💡 気づいたこと"
        )

        with st.form(
            "new_insight"
        ):
            observation = (
                st.text_area(
                    "何に気づいた？",
                    placeholder=(
                        "先週より増えている"
                    ),
                )
            )

            reason = st.text_area(
                "理由はありそう？（任意）",
                placeholder=(
                    "午後に眠い日が"
                    "多かったかも"
                ),
            )

            next_action = (
                st.text_input(
                    "これからどうする？（任意）",
                    placeholder=(
                        "もう1週間観察する"
                    ),
                )
            )

            if st.form_submit_button(
                "💡 気づきを残す",
                use_container_width=True,
            ):
                if not observation.strip():
                    st.warning(
                        "気づいたことを"
                        "入力してね。"
                    )

                else:
                    add_insight(
                        data=data,
                        topic_id=(
                            detail_topic_id
                        ),
                        insight_date=today,
                        observation=(
                            observation.strip()
                        ),
                        reason=(
                            reason.strip()
                        ),
                        next_action=(
                            next_action.strip()
                        ),
                    )

                    st.rerun()

        insights = topic_insights(
            data,
            detail_topic_id,
        )

        if insights:
            st.markdown(
                "##### 📝 過去の気づき"
            )

            for insight in sorted(
                insights,
                key=lambda item: (
                    item.get(
                        "date",
                        ""
                    ),
                    item.get(
                        "created_at",
                        ""
                    ),
                ),
                reverse=True,
            )[:10]:
                with st.container(
                    border=True
                ):
                    st.write(
                        f"💡 **"
                        f"{insight.get('observation')}"
                        f"**"
                    )

                    st.caption(
                        format_date(
                            insight.get(
                                "date"
                            )
                        )
                    )

                    if insight.get(
                        "reason"
                    ):
                        st.write(
                            "理由："
                            + insight.get(
                                "reason"
                            )
                        )

                    if insight.get(
                        "next"
                    ):
                        st.write(
                            "その時考えたこと："
                            + insight.get(
                                "next"
                            )
                        )

        # -----------------------------------------
        # 最近現れたもの
        # -----------------------------------------

        st.divider()

        st.subheader(
            "👀 最近現れたもの"
        )

        new_topics = []

        for topic in topics:
            topic_data = (
                topic_records(
                    data,
                    topic.get("id"),
                )
            )

            first_date = (
                first_record_date(
                    topic_data
                )
            )

            if not first_date:
                continue

            days_since = (
                today - first_date
            ).days

            if days_since <= 30:
                new_topics.append(
                    (
                        days_since,
                        topic,
                        first_date,
                    )
                )

        new_topics.sort(
            key=lambda item: item[0]
        )

        if not new_topics:
            st.caption(
                "最近30日以内に"
                "記録し始めたテーマは"
                "ありません。"
            )

        else:
            for (
                days_since,
                topic,
                first_date,
            ) in new_topics:
                if days_since == 0:
                    age_text = (
                        "今日から"
                    )
                else:
                    age_text = (
                        f"{days_since}日前から"
                    )

                st.write(
                    f"**{topic.get('name')}** "
                    f"— {age_text}"
                )


# =========================================================
# TAB 3：図鑑
# =========================================================

with tab_library:

    st.subheader(
        "📚 観察図鑑"
    )

    search_text = st.text_input(
        "🔎 テーマ検索",
        key="library_search",
    )

    col1, col2 = st.columns(2)

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
                ["すべて"]
                + STATUSES,
                key=(
                    "library_status"
                ),
            )
        )

    library_rows = []

    for topic in topics:
        if (
            category_filter
            != "すべて"
            and topic.get(
                "category"
            )
            != category_filter
        ):
            continue

        if (
            status_filter
            != "すべて"
            and topic.get(
                "status"
            )
            != status_filter
        ):
            continue

        searchable = " ".join(
            [
                topic.get(
                    "name",
                    "",
                ),
                topic.get(
                    "memo",
                    "",
                ),
                topic.get(
                    "category",
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

        topic_data = topic_records(
            data,
            topic.get("id"),
        )

        comparison = (
            recent_comparison(
                topic_data,
                today,
            )
        )

        library_rows.append(
            {
                "テーマ": (
                    topic.get(
                        "name"
                    )
                ),
                "カテゴリー": (
                    topic.get(
                        "category"
                    )
                ),
                "最近7日": (
                    format_value(
                        comparison[
                            "recent"
                        ]
                    )
                    + topic.get(
                        "unit",
                        "",
                    )
                ),
                "前7日": (
                    format_value(
                        comparison[
                            "previous"
                        ]
                    )
                    + topic.get(
                        "unit",
                        "",
                    )
                ),
                "変化": (
                    change_text(
                        comparison,
                        topic.get(
                            "unit",
                            "",
                        ),
                    )
                ),
                "状態": (
                    topic.get(
                        "status"
                    )
                ),
            }
        )

    if library_rows:
        st.dataframe(
            pd.DataFrame(
                library_rows
            ),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "条件に合うテーマは"
            "ありません。"
        )

    # -----------------------------------------
    # 月間レポート
    # -----------------------------------------

    st.divider()

    st.subheader(
        "📅 月間レポート"
    )

    year = st.number_input(
        "年",
        min_value=2000,
        max_value=2100,
        value=today.year,
        step=1,
        key="monthly_year",
    )

    month = st.selectbox(
        "月",
        list(
            range(1, 13)
        ),
        index=today.month - 1,
        format_func=lambda value: (
            f"{value}月"
        ),
        key="monthly_month",
    )

    month_start = date(
        int(year),
        int(month),
        1,
    )

    if int(month) == 12:
        next_month = date(
            int(year) + 1,
            1,
            1,
        )
    else:
        next_month = date(
            int(year),
            int(month) + 1,
            1,
        )

    month_end = (
        next_month
        - timedelta(days=1)
    )

    previous_month_end = (
        month_start
        - timedelta(days=1)
    )

    previous_month_start = (
        previous_month_end.replace(
            day=1
        )
    )

    monthly_rows = []

    for topic in topics:
        topic_data = topic_records(
            data,
            topic.get("id"),
        )

        current_total = total_between(
            topic_data,
            month_start,
            month_end,
        )

        previous_total = total_between(
            topic_data,
            previous_month_start,
            previous_month_end,
        )

        difference = (
            current_total
            - previous_total
        )

        monthly_rows.append(
            {
                "テーマ": (
                    topic.get("name")
                ),
                "今月": (
                    format_value(
                        current_total
                    )
                    + topic.get(
                        "unit",
                        "",
                    )
                ),
                "前月": (
                    format_value(
                        previous_total
                    )
                    + topic.get(
                        "unit",
                        "",
                    )
                ),
                "差": (
                    (
                        "+"
                        if difference > 0
                        else ""
                    )
                    + format_value(
                        difference
                    )
                    + topic.get(
                        "unit",
                        "",
                    )
                ),
            }
        )

    if monthly_rows:
        st.dataframe(
            pd.DataFrame(
                monthly_rows
            ),
            hide_index=True,
            use_container_width=True,
        )

    # -----------------------------------------
    # 昔との比較
    # -----------------------------------------

    st.divider()

    st.subheader(
        "🎲 昔はどうだった？"
    )

    eligible_topics = []

    for topic in topics:
        topic_data = topic_records(
            data,
            topic.get("id"),
        )

        first_date = first_record_date(
            topic_data
        )

        if (
            first_date
            and (
                today - first_date
            ).days >= 30
        ):
            eligible_topics.append(
                topic
            )

    if not eligible_topics:
        st.caption(
            "30日以上記録すると、"
            "昔との比較ができます。"
        )

    else:
        eligible_ids = [
            topic.get("id")
            for topic in eligible_topics
        ]

        random_topic_id = (
            st.session_state.get(
                "old_topic_id"
            )
        )

        if (
            random_topic_id
            not in eligible_ids
        ):
            random_topic_id = (
                random.choice(
                    eligible_ids
                )
            )

            st.session_state[
                "old_topic_id"
            ] = random_topic_id

        old_topic = get_topic(
            data,
            random_topic_id,
        )

        old_records = topic_records(
            data,
            random_topic_id,
        )

        possible_dates = [
            parse_date(
                record.get(
                    "date"
                )
            )
            for record in old_records
        ]

        possible_dates = [
            value
            for value in possible_dates
            if (
                value
                and (
                    today - value
                ).days >= 30
            )
        ]

        if possible_dates:
            old_end = max(
                possible_dates
            )

            old_start = (
                old_end
                - timedelta(days=6)
            )

            old_total = total_between(
                old_records,
                old_start,
                old_end,
            )

            recent_total = total_between(
                old_records,
                today
                - timedelta(days=6),
                today,
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### 🎲 "
                    f"{old_topic.get('name')}"
                )

                st.write(
                    f"昔の7日間："
                    f"**{format_value(old_total)}"
                    f"{old_topic.get('unit')}**"
                )

                st.write(
                    f"最近7日："
                    f"**{format_value(recent_total)}"
                    f"{old_topic.get('unit')}**"
                )

                st.caption(
                    f"{format_date(old_start)}"
                    f"〜"
                    f"{format_date(old_end)}"
                )

        if st.button(
            "🎲 別のテーマを見る",
            use_container_width=True,
        ):
            alternatives = [
                topic_id
                for topic_id
                in eligible_ids
                if topic_id
                != random_topic_id
            ]

            if alternatives:
                st.session_state[
                    "old_topic_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# TAB 4：管理
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ テーマ管理"
    )

    if not topics:
        st.info(
            "まだテーマがありません。"
        )

    else:
        manage_topic_options = {
            topic_label(topic):
            topic.get("id")
            for topic in topics
        }

        manage_label = st.selectbox(
            "テーマを選択",
            list(
                manage_topic_options.keys()
            ),
            key="manage_topic",
        )

        manage_topic_id = (
            manage_topic_options[
                manage_label
            ]
        )

        manage_topic = get_topic(
            data,
            manage_topic_id,
        )

        edit_name = st.text_input(
            "テーマ名",
            value=manage_topic.get(
                "name",
                "",
            ),
        )

        old_category = (
            manage_topic.get(
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

        edit_category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
            index=category_index,
            key="edit_category",
        )

        edit_unit = st.text_input(
            "単位",
            value=manage_topic.get(
                "unit",
                "回",
            ),
        )

        old_status = manage_topic.get(
            "status",
            "👀 観察中",
        )

        status_index = (
            STATUSES.index(
                old_status
            )
            if old_status
            in STATUSES
            else 0
        )

        edit_status = st.selectbox(
            "状態",
            STATUSES,
            index=status_index,
        )

        edit_memo = st.text_area(
            "メモ",
            value=manage_topic.get(
                "memo",
                "",
            ),
        )

        if st.button(
            "💾 テーマを保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_name.strip():
                st.warning(
                    "テーマ名を入力してね。"
                )

            elif not edit_unit.strip():
                st.warning(
                    "単位を入力してね。"
                )

            else:
                manage_topic[
                    "name"
                ] = edit_name.strip()

                manage_topic[
                    "category"
                ] = edit_category

                manage_topic[
                    "unit"
                ] = edit_unit.strip()

                manage_topic[
                    "status"
                ] = edit_status

                manage_topic[
                    "memo"
                ] = edit_memo.strip()

                manage_topic[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

        st.divider()

        st.subheader(
            "📝 記録の編集・削除"
        )

        manage_records = sorted(
            topic_records(
                data,
                manage_topic_id,
            ),
            key=lambda item: (
                item.get(
                    "date",
                    ""
                ),
                item.get(
                    "time",
                    ""
                ),
            ),
            reverse=True,
        )

        if not manage_records:
            st.caption(
                "このテーマには"
                "まだ記録がありません。"
            )

        else:
            record_options = {}

            for record in manage_records:
                label = (
                    f"{format_date(record.get('date'))}"
                    f" {record.get('time', '')}"
                    f" ｜ "
                    f"{format_value(record.get('value'))}"
                    f"{manage_topic.get('unit')}"
                    f" [{record.get('id')[:6]}]"
                )

                record_options[
                    label
                ] = record.get(
                    "id"
                )

            selected_record_label = (
                st.selectbox(
                    "記録",
                    list(
                        record_options.keys()
                    ),
                    key="manage_record",
                )
            )

            record_id = (
                record_options[
                    selected_record_label
                ]
            )

            record = get_record(
                data,
                record_id,
            )

            edit_record_date = (
                st.date_input(
                    "記録日",
                    value=(
                        parse_date(
                            record.get(
                                "date"
                            )
                        )
                        or today
                    ),
                    max_value=today,
                    key=(
                        "edit_record_date_"
                        + record_id
                    ),
                )
            )

            try:
                old_time = (
                    datetime.strptime(
                        record.get(
                            "time",
                            "12:00",
                        ),
                        "%H:%M",
                    ).time()
                )
            except ValueError:
                old_time = (
                    datetime.now()
                    .replace(
                        second=0,
                        microsecond=0,
                    )
                    .time()
                )

            edit_record_time = (
                st.time_input(
                    "時刻",
                    value=old_time,
                    key=(
                        "edit_record_time_"
                        + record_id
                    ),
                )
            )

            edit_record_value = (
                st.number_input(
                    "量",
                    min_value=0.0,
                    value=safe_float(
                        record.get(
                            "value"
                        )
                    ),
                    step=1.0,
                    key=(
                        "edit_record_value_"
                        + record_id
                    ),
                )
            )

            edit_record_memo = (
                st.text_input(
                    "メモ",
                    value=record.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_record_memo_"
                        + record_id
                    ),
                )
            )

            if st.button(
                "💾 記録を更新",
                use_container_width=True,
            ):
                record[
                    "date"
                ] = str(
                    edit_record_date
                )

                record[
                    "time"
                ] = (
                    edit_record_time
                    .strftime(
                        "%H:%M"
                    )
                )

                record[
                    "value"
                ] = float(
                    edit_record_value
                )

                record[
                    "memo"
                ] = (
                    edit_record_memo
                    .strip()
                )

                record[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

            delete_record_confirm = (
                st.checkbox(
                    "この記録を削除する",
                    key=(
                        "delete_record_confirm_"
                        + record_id
                    ),
                )
            )

            if st.button(
                "🗑️ 記録を削除",
                disabled=(
                    not delete_record_confirm
                ),
                key=(
                    "delete_record_"
                    + record_id
                ),
                use_container_width=True,
            ):
                data["records"] = [
                    item
                    for item
                    in data["records"]
                    if item.get(
                        "id"
                    )
                    != record_id
                ]

                save_data(data)

                st.rerun()

        st.divider()

        st.warning(
            "テーマを削除すると、"
            "紐づく記録と気づきも"
            "すべて削除されます。"
        )

        delete_topic_confirm = (
            st.checkbox(
                "テーマごと削除する",
                key=(
                    "delete_topic_confirm_"
                    + manage_topic_id
                ),
            )
        )

        if st.button(
            "🗑️ テーマを完全削除",
            disabled=(
                not delete_topic_confirm
            ),
            key=(
                "delete_topic_"
                + manage_topic_id
            ),
            use_container_width=True,
        ):
            delete_topic(
                data,
                manage_topic_id,
            )

            st.rerun()

    # -----------------------------------------
    # バックアップ
    # -----------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            "recently_increasing_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:25px 10px;
        opacity:.8;
    ">
        <p>
            👀 <b>
            変化は、気づく前から始まっている。
            </b>
        </p>
        <p>
            📈 記録しておけば、
            「なんとなく」はいつか形になる。
        </p>
        <br>
        <b>DAY 301 — COMPLETE 🌅</b>
    </div>
    """,
    unsafe_allow_html=True,
)
