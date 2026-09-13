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
    page_title="今月の自分ダッシュボード",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "monthly_dashboard.json",
)


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
        "records": []
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

        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "record_date",
                str(date.today()),
            )

            record.setdefault(
                "mood",
                50,
            )

            record.setdefault(
                "focus",
                50,
            )

            record.setdefault(
                "energy",
                50,
            )

            record.setdefault(
                "achievements",
                0,
            )

            record.setdefault(
                "learnings",
                0,
            )

            record.setdefault(
                "small_wins",
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
# 補助関数
# =========================================================

def get_record_by_id(
    data,
    record_id,
):
    return next(
        (
            record
            for record in data["records"]
            if record.get("id") == record_id
        ),
        None,
    )


def parse_date(text):
    try:
        return datetime.strptime(
            text,
            "%Y-%m-%d",
        ).date()

    except (
        ValueError,
        TypeError,
    ):
        return date.today()


def format_date(text):
    target = parse_date(
        text
    )

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

    return target.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def format_datetime(text):
    try:
        target = datetime.fromisoformat(
            text
        )

        return target.strftime(
            "%Y/%m/%d %H:%M"
        )

    except (
        ValueError,
        TypeError,
    ):
        return ""


def month_key(target_date):
    return target_date.strftime(
        "%Y-%m"
    )


def previous_month_key(target_date):
    year = target_date.year
    month = target_date.month

    if month == 1:
        return f"{year - 1}-12"

    return f"{year}-{month - 1:02d}"


def records_for_month(
    records,
    target_month,
):
    return [
        record
        for record in records
        if record.get(
            "record_date",
            "",
        ).startswith(
            target_month
        )
    ]


def average_value(
    records,
    key,
):
    if not records:
        return 0

    return round(
        sum(
            int(
                record.get(
                    key,
                    0,
                )
            )
            for record in records
        )
        / len(records),
        1,
    )


def total_value(
    records,
    key,
):
    return sum(
        int(
            record.get(
                key,
                0,
            )
        )
        for record in records
    )


def unique_record_days(
    records,
):
    return len(
        {
            record.get(
                "record_date",
                "",
            )
            for record in records
            if record.get(
                "record_date"
            )
        }
    )


def delta_text(
    current,
    previous,
    suffix="",
):
    if previous == 0:
        if current == 0:
            return "±0"

        return "新規"

    diff = round(
        current - previous,
        1,
    )

    if diff > 0:
        return f"+{diff}{suffix}"

    if diff < 0:
        return f"{diff}{suffix}"

    return f"±0{suffix}"


def best_metric(
    mood,
    focus,
    energy,
):
    values = {
        "🙂 気分": mood,
        "🧠 集中度": focus,
        "⚡ エネルギー": energy,
    }

    name = max(
        values,
        key=values.get,
    )

    return (
        name,
        values[name],
    )


def lowest_metric(
    mood,
    focus,
    energy,
):
    values = {
        "🙂 気分": mood,
        "🧠 集中度": focus,
        "⚡ エネルギー": energy,
    }

    name = min(
        values,
        key=values.get,
    )

    return (
        name,
        values[name],
    )


# =========================================================
# CRUD
# =========================================================

def add_record(
    data,
    record_date,
    mood,
    focus,
    energy,
    achievements,
    learnings,
    small_wins,
    memo,
):
    data["records"].append(
        {
            "id": create_id(),
            "record_date": str(
                record_date
            ),
            "mood": int(
                mood
            ),
            "focus": int(
                focus
            ),
            "energy": int(
                energy
            ),
            "achievements": int(
                achievements
            ),
            "learnings": int(
                learnings
            ),
            "small_wins": int(
                small_wins
            ),
            "memo": memo,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_record(
    data,
    record_id,
    record_date,
    mood,
    focus,
    energy,
    achievements,
    learnings,
    small_wins,
    memo,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record[
        "record_date"
    ] = str(
        record_date
    )

    record[
        "mood"
    ] = int(
        mood
    )

    record[
        "focus"
    ] = int(
        focus
    )

    record[
        "energy"
    ] = int(
        energy
    )

    record[
        "achievements"
    ] = int(
        achievements
    )

    record[
        "learnings"
    ] = int(
        learnings
    )

    record[
        "small_wins"
    ] = int(
        small_wins
    )

    record[
        "memo"
    ] = memo

    record[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data[
        "records"
    ] = [
        record
        for record in data[
            "records"
        ]
        if record.get(
            "id"
        )
        != record_id
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
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(100, 130, 255, 0.07);
        border: 1px solid rgba(100, 130, 255, 0.15);
        border-radius: 16px;
        padding: 15px;
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 130, 255, 0.18),
                rgba(120, 220, 180, 0.11)
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

    .summary-card {
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 16px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 80, 0.12),
                rgba(110, 130, 255, 0.08)
            );
    }

    .summary-title {
        font-size: 0.9rem;
        font-weight: 700;
        opacity: 0.7;
    }

    .summary-value {
        font-size: 1.5rem;
        font-weight: 900;
        margin-top: 8px;
    }

    .monthly-note {
        padding: 26px;
        border-radius: 22px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 16px;

        background:
            linear-gradient(
                135deg,
                rgba(110, 130, 255, 0.10),
                rgba(255, 180, 200, 0.08)
            );
    }

    .monthly-note-text {
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

records = data[
    "records"
]

today = date.today()

current_month = month_key(
    today
)

previous_month = previous_month_key(
    today
)

month_records = records_for_month(
    records,
    current_month,
)

previous_records = records_for_month(
    records,
    previous_month,
)


# =========================================================
# 今月集計
# =========================================================

mood_avg = average_value(
    month_records,
    "mood",
)

focus_avg = average_value(
    month_records,
    "focus",
)

energy_avg = average_value(
    month_records,
    "energy",
)

achievement_total = total_value(
    month_records,
    "achievements",
)

learning_total = total_value(
    month_records,
    "learnings",
)

small_win_total = total_value(
    month_records,
    "small_wins",
)

record_days = unique_record_days(
    month_records
)


# =========================================================
# 先月集計
# =========================================================

previous_mood = average_value(
    previous_records,
    "mood",
)

previous_focus = average_value(
    previous_records,
    "focus",
)

previous_energy = average_value(
    previous_records,
    "energy",
)

previous_record_days = (
    unique_record_days(
        previous_records
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    f"""
    <div class="hero">

        <h1>📊 今月の自分ダッシュボード</h1>

        <p>
            {today.year}年{today.month}月の自分を、
            数字と一言で振り返ろう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# メインダッシュボード
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

col1.metric(
    "🙂 気分平均",
    (
        f"{mood_avg}点"
        if month_records
        else "-"
    ),
    delta=(
        delta_text(
            mood_avg,
            previous_mood,
            "点",
        )
        if previous_records
        else None
    ),
)

col2.metric(
    "🧠 集中度平均",
    (
        f"{focus_avg}%"
        if month_records
        else "-"
    ),
    delta=(
        delta_text(
            focus_avg,
            previous_focus,
            "%",
        )
        if previous_records
        else None
    ),
)

col3.metric(
    "⚡ エネルギー平均",
    (
        f"{energy_avg}%"
        if month_records
        else "-"
    ),
    delta=(
        delta_text(
            energy_avg,
            previous_energy,
            "%",
        )
        if previous_records
        else None
    ),
)

col4.metric(
    "🔥 記録日数",
    f"{record_days}日",
    delta=(
        delta_text(
            record_days,
            previous_record_days,
            "日",
        )
        if previous_records
        else None
    ),
)


# =========================================================
# 行動カウント
# =========================================================

st.divider()

st.subheader(
    "🌱 今月積み重ねたもの"
)

col1, col2, col3 = st.columns(
    3
)

col1.metric(
    "🏆 できたこと",
    f"{achievement_total}個",
)

col2.metric(
    "📚 学んだこと",
    f"{learning_total}個",
)

col3.metric(
    "🌱 小さな勝ち",
    f"{small_win_total}個",
)


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "✍️ 今日の自分を記録"
)

with st.form(
    "add_record_form"
):
    col1, col2, col3 = st.columns(
        3
    )

    with col1:
        mood = st.slider(
            "🙂 気分",
            min_value=0,
            max_value=100,
            value=60,
            step=5,
        )

    with col2:
        focus = st.slider(
            "🧠 集中度",
            min_value=0,
            max_value=100,
            value=60,
            step=5,
        )

    with col3:
        energy = st.slider(
            "⚡ エネルギー",
            min_value=0,
            max_value=100,
            value=60,
            step=5,
        )

    count_col1, count_col2, count_col3 = st.columns(
        3
    )

    with count_col1:
        achievements = st.number_input(
            "🏆 今日できたこと",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
        )

    with count_col2:
        learnings = st.number_input(
            "📚 今日学んだこと",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
        )

    with count_col3:
        small_wins = st.number_input(
            "🌱 今日の小さな勝ち",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
        )

    record_date = st.date_input(
        "📅 記録日",
        value=date.today(),
    )

    memo = st.text_area(
        "💬 今日のひとこと",
        placeholder=(
            "例：忙しかったけど、"
            "少しずつ前には進めた。"
        ),
        height=100,
    )

    submitted = st.form_submit_button(
        "📊 今日の記録を保存",
        use_container_width=True,
        type="primary",
    )

    if submitted:
        add_record(
            data,
            record_date,
            mood,
            focus,
            energy,
            achievements,
            learnings,
            small_wins,
            memo.strip(),
        )

        st.rerun()


# =========================================================
# 今月まとめ
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "🏆 今月のまとめ"
    )

    best_name, best_value = best_metric(
        mood_avg,
        focus_avg,
        energy_avg,
    )

    low_name, low_value = lowest_metric(
        mood_avg,
        focus_avg,
        energy_avg,
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:
        st.markdown(
            f"""
            <div class="summary-card">

                <div class="summary-title">
                    🏆 今月もっとも高いもの
                </div>

                <div class="summary-value">
                    {best_name}
                </div>

                <div>
                    {best_value}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="summary-card">

                <div class="summary-title">
                    📉 今月もっとも低いもの
                </div>

                <div class="summary-value">
                    {low_name}
                </div>

                <div>
                    {low_value}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="summary-card">

                <div class="summary-title">
                    🔥 今月の記録日数
                </div>

                <div class="summary-value">
                    {record_days}日
                </div>

                <div>
                    今月の積み重ね
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 今月のベストメモ
# =========================================================

if month_records:
    memo_records = [
        record
        for record in month_records
        if record.get(
            "memo",
            "",
        ).strip()
    ]

    if memo_records:
        best_memo_record = max(
            memo_records,
            key=lambda record: (
                int(
                    record.get(
                        "mood",
                        0,
                    )
                )
                + int(
                    record.get(
                        "focus",
                        0,
                    )
                )
                + int(
                    record.get(
                        "energy",
                        0,
                    )
                )
            ),
        )

        st.markdown(
            f"""
            <div class="monthly-note">

                <div style="
                    font-size: 0.9rem;
                    opacity: 0.7;
                    margin-bottom: 8px;
                    font-weight: 700;
                ">
                    ✨ 今月のベストメモ
                </div>

                <div class="monthly-note-text">
                    「{best_memo_record.get('memo', '')}」
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 今月の推移
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "📈 今月の推移"
    )

    trend_rows = []

    for record in month_records:
        trend_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "気分": int(
                    record.get(
                        "mood",
                        0,
                    )
                ),
                "集中度": int(
                    record.get(
                        "focus",
                        0,
                    )
                ),
                "エネルギー": int(
                    record.get(
                        "energy",
                        0,
                    )
                ),
            }
        )

    trend_df = pd.DataFrame(
        trend_rows
    )

    daily_trend = (
        trend_df.groupby(
            "日付",
            as_index=False,
        )[
            [
                "気分",
                "集中度",
                "エネルギー",
            ]
        ]
        .mean()
    )

    daily_trend = daily_trend.sort_values(
        "日付"
    )

    st.line_chart(
        daily_trend.set_index(
            "日付"
        )
    )


# =========================================================
# 行動グラフ
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "📊 今月積み重ねたもの"
    )

    activity_df = pd.DataFrame(
        {
            "項目": [
                "できたこと",
                "学んだこと",
                "小さな勝ち",
            ],
            "件数": [
                achievement_total,
                learning_total,
                small_win_total,
            ],
        }
    )

    st.bar_chart(
        activity_df.set_index(
            "項目"
        )
    )


# =========================================================
# 先月比較
# =========================================================

if previous_records:
    st.divider()

    st.subheader(
        "🔄 先月との比較"
    )

    comparison_df = pd.DataFrame(
        [
            {
                "項目": "🙂 気分",
                "先月": previous_mood,
                "今月": mood_avg,
                "変化": (
                    mood_avg
                    - previous_mood
                ),
            },
            {
                "項目": "🧠 集中度",
                "先月": previous_focus,
                "今月": focus_avg,
                "変化": (
                    focus_avg
                    - previous_focus
                ),
            },
            {
                "項目": "⚡ エネルギー",
                "先月": previous_energy,
                "今月": energy_avg,
                "変化": (
                    energy_avg
                    - previous_energy
                ),
            },
            {
                "項目": "🔥 記録日数",
                "先月": previous_record_days,
                "今月": record_days,
                "変化": (
                    record_days
                    - previous_record_days
                ),
            },
        ]
    )

    comparison_df[
        "変化"
    ] = comparison_df[
        "変化"
    ].round(1)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 記録履歴"
)

month_options = sorted(
    {
        record.get(
            "record_date",
            "",
        )[:7]
        for record in records
        if record.get(
            "record_date"
        )
    },
    reverse=True,
)

selected_month = st.selectbox(
    "表示する月",
    (
        month_options
        if month_options
        else [current_month]
    ),
)

history_records = records_for_month(
    records,
    selected_month,
)

history_records = sorted(
    history_records,
    key=lambda record: (
        record.get(
            "record_date",
            "",
        ),
        record.get(
            "created_at",
            "",
        ),
    ),
    reverse=True,
)

if not history_records:
    st.info(
        "この月の記録はありません。"
    )

else:
    history_rows = []

    for record in history_records:
        history_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "気分": int(
                    record.get(
                        "mood",
                        0,
                    )
                ),
                "集中度": int(
                    record.get(
                        "focus",
                        0,
                    )
                ),
                "エネルギー": int(
                    record.get(
                        "energy",
                        0,
                    )
                ),
                "できたこと": int(
                    record.get(
                        "achievements",
                        0,
                    )
                ),
                "学び": int(
                    record.get(
                        "learnings",
                        0,
                    )
                ),
                "小さな勝ち": int(
                    record.get(
                        "small_wins",
                        0,
                    )
                ),
                "ひとこと": record.get(
                    "memo",
                    "",
                ),
            }
        )

    history_df = pd.DataFrame(
        history_rows
    )

    st.dataframe(
        history_df,
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
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    else:
        edit_records = sorted(
            records,
            key=lambda record: (
                record.get(
                    "record_date",
                    "",
                ),
                record.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        for record in edit_records:
            record_id = record.get(
                "id",
                "",
            )

            st.markdown(
                f"### 📊 "
                f"{format_date(record.get('record_date', ''))}"
            )

            st.caption(
                f"🙂 {record.get('mood', 0)}"
                f" ｜ "
                f"🧠 {record.get('focus', 0)}"
                f" ｜ "
                f"⚡ {record.get('energy', 0)}"
            )

            with st.expander(
                "✏️ 編集"
            ):
                edit_date = st.date_input(
                    "記録日",
                    value=parse_date(
                        record.get(
                            "record_date",
                            "",
                        )
                    ),
                    key=(
                        "edit_date_"
                        + record_id
                    ),
                )

                col1, col2, col3 = st.columns(
                    3
                )

                with col1:
                    edit_mood = st.slider(
                        "気分",
                        0,
                        100,
                        int(
                            record.get(
                                "mood",
                                50,
                            )
                        ),
                        5,
                        key=(
                            "edit_mood_"
                            + record_id
                        ),
                    )

                with col2:
                    edit_focus = st.slider(
                        "集中度",
                        0,
                        100,
                        int(
                            record.get(
                                "focus",
                                50,
                            )
                        ),
                        5,
                        key=(
                            "edit_focus_"
                            + record_id
                        ),
                    )

                with col3:
                    edit_energy = st.slider(
                        "エネルギー",
                        0,
                        100,
                        int(
                            record.get(
                                "energy",
                                50,
                            )
                        ),
                        5,
                        key=(
                            "edit_energy_"
                            + record_id
                        ),
                    )

                count_col1, count_col2, count_col3 = st.columns(
                    3
                )

                with count_col1:
                    edit_achievements = st.number_input(
                        "できたこと",
                        min_value=0,
                        max_value=50,
                        value=int(
                            record.get(
                                "achievements",
                                0,
                            )
                        ),
                        key=(
                            "edit_achievements_"
                            + record_id
                        ),
                    )

                with count_col2:
                    edit_learnings = st.number_input(
                        "学んだこと",
                        min_value=0,
                        max_value=50,
                        value=int(
                            record.get(
                                "learnings",
                                0,
                            )
                        ),
                        key=(
                            "edit_learnings_"
                            + record_id
                        ),
                    )

                with count_col3:
                    edit_small_wins = st.number_input(
                        "小さな勝ち",
                        min_value=0,
                        max_value=50,
                        value=int(
                            record.get(
                                "small_wins",
                                0,
                            )
                        ),
                        key=(
                            "edit_small_wins_"
                            + record_id
                        ),
                    )

                edit_memo = st.text_area(
                    "ひとこと",
                    value=record.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + record_id
                    ),
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    update_record(
                        data,
                        record_id,
                        edit_date,
                        edit_mood,
                        edit_focus,
                        edit_energy,
                        edit_achievements,
                        edit_learnings,
                        edit_small_wins,
                        edit_memo.strip(),
                    )

                    st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この記録を削除",
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

            st.divider()


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
            "monthly_self_dashboard_"
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
    "1か月を振り返ると、自分が思っているより進んでいる。📊🌱"
)
