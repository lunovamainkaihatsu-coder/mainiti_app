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
    page_title="今日は何点？",
    page_icon="💯",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "scores.json",
)

MOODS = [
    "😄 最高",
    "🙂 良い",
    "😐 普通",
    "😮‍💨 疲れた",
    "😢 しんどい",
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
        "records": []
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
    return target.strftime(
        "%Y-%m"
    )


def previous_month_key(target):
    year = target.year
    month = target.month

    if month == 1:
        return f"{year - 1}-12"

    return (
        f"{year}-"
        f"{month - 1:02d}"
    )


def get_weekday(text):
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

    return weekdays[
        target.weekday()
    ]


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
                "score",
                70,
            )

            record.setdefault(
                "mood",
                "😐 普通",
            )

            record.setdefault(
                "good",
                "",
            )

            record.setdefault(
                "could_improve",
                "",
            )

            record.setdefault(
                "tomorrow",
                "",
            )

            record.setdefault(
                "comment",
                "",
            )

            record.setdefault(
                "favorite",
                False,
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
# CRUD
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


def get_record_by_date(
    data,
    record_date,
):
    date_text = str(record_date)

    return next(
        (
            record
            for record in data["records"]
            if record.get(
                "record_date"
            ) == date_text
        ),
        None,
    )


def add_record(
    data,
    record_date,
    score,
    mood,
    good,
    could_improve,
    tomorrow,
    comment,
):
    data["records"].append(
        {
            "id": create_id(),
            "record_date": str(
                record_date
            ),
            "score": int(
                score
            ),
            "mood": mood,
            "good": good,
            "could_improve": (
                could_improve
            ),
            "tomorrow": tomorrow,
            "comment": comment,
            "favorite": False,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_record(
    data,
    record_id,
    record_date,
    score,
    mood,
    good,
    could_improve,
    tomorrow,
    comment,
    favorite,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record["record_date"] = str(
        record_date
    )

    record["score"] = int(
        score
    )

    record["mood"] = mood

    record["good"] = good

    record["could_improve"] = (
        could_improve
    )

    record["tomorrow"] = tomorrow

    record["comment"] = comment

    record["favorite"] = bool(
        favorite
    )

    record["updated_at"] = (
        now_text()
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
    record = get_record_by_id(
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

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# 集計
# =========================================================

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


def average_score(records):
    if not records:
        return 0

    return round(
        sum(
            int(
                record.get(
                    "score",
                    0,
                )
            )
            for record in records
        )
        / len(records),
        1,
    )


def score_message(score):
    if score >= 90:
        return (
            "🌟 かなり満足できた一日！"
        )

    if score >= 80:
        return (
            "✨ いい一日だったね！"
        )

    if score >= 70:
        return (
            "🙂 ちゃんと進めた一日。"
        )

    if score >= 60:
        return (
            "🌿 まずまず。"
            "できたことも見てみよう。"
        )

    if score >= 40:
        return (
            "☕ 今日は少し大変だったかも。"
        )

    return (
        "🛋️ 今日は回復優先でもOK。"
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
        background: rgba(100, 130, 255, 0.07);
        border: 1px solid rgba(100, 130, 255, 0.15);
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        margin-bottom: 24px;
        background:
            linear-gradient(
                135deg,
                rgba(100, 130, 255, 0.17),
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

    .score-box {
        text-align: center;
        padding: 28px;
        border-radius: 24px;
        margin: 15px 0;
        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 80, 0.13),
                rgba(100, 130, 255, 0.09)
            );
    }

    .score-number {
        font-size: 3rem;
        font-weight: 900;
    }

    .score-message {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
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
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>💯 今日は何点？</h1>

        <p>
            100点じゃなくても、
            今日には今日の点数がある。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今月のダッシュボード
# =========================================================

month_average = average_score(
    month_records
)

month_best = max(
    [
        int(
            record.get(
                "score",
                0,
            )
        )
        for record in month_records
    ],
    default=0,
)

over_80_count = sum(
    1
    for record in month_records
    if int(
        record.get(
            "score",
            0,
        )
    ) >= 80
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "💯 今月の平均点",
    (
        f"{month_average}点"
        if month_records
        else "-"
    ),
)

col2.metric(
    "🏆 今月の最高点",
    (
        f"{month_best}点"
        if month_records
        else "-"
    ),
)

col3.metric(
    "🔥 記録日数",
    f"{len(month_records)}日",
)

col4.metric(
    "✨ 80点以上",
    f"{over_80_count}日",
)


# =========================================================
# 先月比較
# =========================================================

if previous_records:
    previous_average = average_score(
        previous_records
    )

    difference = round(
        month_average
        - previous_average,
        1,
    )

    st.divider()

    st.subheader(
        "📈 先月との比較"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "先月平均",
        f"{previous_average}点",
    )

    col2.metric(
        "今月平均",
        f"{month_average}点",
    )

    if difference > 0:
        delta_text = (
            f"+{difference}点 ↗"
        )

    elif difference < 0:
        delta_text = (
            f"{difference}点 ↘"
        )

    else:
        delta_text = "±0点 →"

    col3.metric(
        "変化",
        delta_text,
    )


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "✍️ 今日を振り返る"
)

today_record = get_record_by_date(
    data,
    today,
)

if today_record:
    score = int(
        today_record.get(
            "score",
            0,
        )
    )

    st.markdown(
        f"""
        <div class="score-box">

            <div>
                今日の点数
            </div>

            <div class="score-number">
                {score} / 100
            </div>

            <div class="score-message">
                {score_message(score)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "今日はすでに記録済みです。"
        "下の編集欄から変更できます。"
    )

else:
    with st.form(
        "today_score_form"
    ):
        score = st.slider(
            "💯 今日の点数",
            min_value=0,
            max_value=100,
            value=70,
            step=1,
        )

        mood = st.selectbox(
            "🙂 今日の気分",
            MOODS,
            index=1,
        )

        good = st.text_area(
            "✨ よかったこと",
            placeholder=(
                "例：予定していた"
                "勉強ができた"
            ),
        )

        could_improve = st.text_area(
            "🤔 惜しかったこと",
            placeholder=(
                "例：少しスマホを"
                "見すぎた"
            ),
        )

        tomorrow = st.text_area(
            "🌱 明日ひとつやること",
            placeholder=(
                "例：朝にコードを"
                "30分読む"
            ),
        )

        comment = st.text_input(
            "💬 今日を一言で",
            placeholder=(
                "例：完璧じゃないけど、"
                "ちゃんと進んだ。"
            ),
        )

        submitted = (
            st.form_submit_button(
                "💯 今日の点数を記録",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            add_record(
                data,
                today,
                score,
                mood,
                good.strip(),
                could_improve.strip(),
                tomorrow.strip(),
                comment.strip(),
            )

            st.rerun()


# =========================================================
# ベストデイ
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🏆 ベストデイ"
    )

    best_record = max(
        records,
        key=lambda record: int(
            record.get(
                "score",
                0,
            )
        ),
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### 💯 "
            f"{best_record.get('score', 0)}点"
        )

        st.caption(
            format_date(
                best_record.get(
                    "record_date",
                    "",
                )
            )
        )

        st.write(
            best_record.get(
                "mood",
                "",
            )
        )

        if best_record.get(
            "good",
            "",
        ):
            st.write(
                "**✨ よかったこと**"
            )

            st.write(
                best_record.get(
                    "good",
                    "",
                )
            )

        if best_record.get(
            "comment",
            "",
        ):
            st.write(
                "**💬 今日を一言で**"
            )

            st.write(
                best_record.get(
                    "comment",
                    "",
                )
            )


# =========================================================
# 点数推移
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "📈 今月の点数推移"
    )

    trend_rows = []

    for record in month_records:
        trend_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "点数": int(
                    record.get(
                        "score",
                        0,
                    )
                ),
            }
        )

    trend_df = pd.DataFrame(
        trend_rows
    )

    trend_df = (
        trend_df
        .sort_values("日付")
        .set_index("日付")
    )

    st.line_chart(
        trend_df
    )


# =========================================================
# 曜日別平均
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📅 曜日別平均点"
    )

    weekday_rows = []

    for record in records:
        weekday_rows.append(
            {
                "曜日": get_weekday(
                    record.get(
                        "record_date",
                        "",
                    )
                ),
                "点数": int(
                    record.get(
                        "score",
                        0,
                    )
                ),
            }
        )

    weekday_df = pd.DataFrame(
        weekday_rows
    )

    weekday_average = (
        weekday_df.groupby(
            "曜日",
            as_index=False,
        )["点数"]
        .mean()
    )

    weekday_average[
        "点数"
    ] = (
        weekday_average[
            "点数"
        ]
        .round(1)
    )

    weekday_order = [
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日",
    ]

    weekday_average[
        "曜日"
    ] = pd.Categorical(
        weekday_average[
            "曜日"
        ],
        categories=weekday_order,
        ordered=True,
    )

    weekday_average = (
        weekday_average
        .sort_values("曜日")
    )

    st.bar_chart(
        weekday_average.set_index(
            "曜日"
        )
    )

    if not weekday_average.empty:
        best_weekday = (
            weekday_average
            .sort_values(
                "点数",
                ascending=False,
            )
            .iloc[0]
        )

        st.success(
            "🏆 平均点が一番高い曜日は"
            f"「{best_weekday['曜日']}曜日」"
            f"で、{best_weekday['点数']}点！"
        )


# =========================================================
# 履歴検索
# =========================================================

st.divider()

st.subheader(
    "📚 過去の記録"
)

search_text = st.text_input(
    "🔎 記録を検索",
    placeholder=(
        "よかったこと・"
        "惜しかったこと・"
        "一言など"
    ),
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

filter_col1, filter_col2 = (
    st.columns(2)
)

with filter_col1:
    month_filter = st.selectbox(
        "月",
        ["すべて"] + month_options,
    )

with filter_col2:
    score_filter = st.selectbox(
        "点数",
        [
            "すべて",
            "90点以上",
            "80点以上",
            "60点未満",
            "⭐ お気に入り",
        ],
    )

filtered_records = []

for record in records:
    if (
        month_filter != "すべて"
        and not record.get(
            "record_date",
            "",
        ).startswith(
            month_filter
        )
    ):
        continue

    record_score = int(
        record.get(
            "score",
            0,
        )
    )

    if (
        score_filter == "90点以上"
        and record_score < 90
    ):
        continue

    if (
        score_filter == "80点以上"
        and record_score < 80
    ):
        continue

    if (
        score_filter == "60点未満"
        and record_score >= 60
    ):
        continue

    if (
        score_filter == "⭐ お気に入り"
        and not record.get(
            "favorite",
            False,
        )
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                record.get(
                    "good",
                    "",
                ),
                record.get(
                    "could_improve",
                    "",
                ),
                record.get(
                    "tomorrow",
                    "",
                ),
                record.get(
                    "comment",
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

filtered_records = sorted(
    filtered_records,
    key=lambda record: (
        record.get(
            "record_date",
            "",
        )
    ),
    reverse=True,
)

if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    for record in filtered_records:
        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            top_col1, top_col2 = (
                st.columns(
                    [5, 1]
                )
            )

            with top_col1:
                st.markdown(
                    f"### 💯 "
                    f"{record.get('score', 0)}点"
                )

                st.caption(
                    format_date(
                        record.get(
                            "record_date",
                            "",
                        )
                    )
                )

            with top_col2:
                favorite_icon = (
                    "⭐"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    favorite_icon,
                    key=(
                        "fav_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            st.write(
                record.get(
                    "mood",
                    "",
                )
            )

            if record.get(
                "good",
                "",
            ):
                st.write(
                    "**✨ よかったこと**"
                )
                st.write(
                    record.get(
                        "good",
                        "",
                    )
                )

            if record.get(
                "could_improve",
                "",
            ):
                st.write(
                    "**🤔 惜しかったこと**"
                )
                st.write(
                    record.get(
                        "could_improve",
                        "",
                    )
                )

            if record.get(
                "tomorrow",
                "",
            ):
                st.write(
                    "**🌱 明日ひとつやること**"
                )
                st.write(
                    record.get(
                        "tomorrow",
                        "",
                    )
                )

            if record.get(
                "comment",
                "",
            ):
                st.caption(
                    "💬 "
                    + record.get(
                        "comment",
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
    edit_records = sorted(
        records,
        key=lambda record: (
            record.get(
                "record_date",
                "",
            )
        ),
        reverse=True,
    )

    if not edit_records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in edit_records:
        record_id = record.get(
            "id",
            "",
        )

        title = (
            f"{record.get('record_date', '')}"
            f" ｜ "
            f"{record.get('score', 0)}点"
        )

        with st.expander(
            title
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

            edit_score = st.slider(
                "今日の点数",
                0,
                100,
                int(
                    record.get(
                        "score",
                        70,
                    )
                ),
                1,
                key=(
                    "edit_score_"
                    + record_id
                ),
            )

            current_mood = record.get(
                "mood",
                "😐 普通",
            )

            mood_index = (
                MOODS.index(
                    current_mood
                )
                if current_mood in MOODS
                else 2
            )

            edit_mood = st.selectbox(
                "今日の気分",
                MOODS,
                index=mood_index,
                key=(
                    "edit_mood_"
                    + record_id
                ),
            )

            edit_good = st.text_area(
                "よかったこと",
                value=record.get(
                    "good",
                    "",
                ),
                key=(
                    "edit_good_"
                    + record_id
                ),
            )

            edit_improve = st.text_area(
                "惜しかったこと",
                value=record.get(
                    "could_improve",
                    "",
                ),
                key=(
                    "edit_improve_"
                    + record_id
                ),
            )

            edit_tomorrow = st.text_area(
                "明日ひとつやること",
                value=record.get(
                    "tomorrow",
                    "",
                ),
                key=(
                    "edit_tomorrow_"
                    + record_id
                ),
            )

            edit_comment = st.text_input(
                "今日を一言で",
                value=record.get(
                    "comment",
                    "",
                ),
                key=(
                    "edit_comment_"
                    + record_id
                ),
            )

            edit_favorite = st.checkbox(
                "⭐ お気に入り",
                value=record.get(
                    "favorite",
                    False,
                ),
                key=(
                    "edit_favorite_"
                    + record_id
                ),
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    existing = (
                        get_record_by_date(
                            data,
                            edit_date,
                        )
                    )

                    if (
                        existing
                        and existing.get(
                            "id"
                        ) != record_id
                    ):
                        st.warning(
                            "その日付には"
                            "すでに記録があります。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_date,
                            edit_score,
                            edit_mood,
                            edit_good.strip(),
                            edit_improve.strip(),
                            edit_tomorrow.strip(),
                            edit_comment.strip(),
                            edit_favorite,
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
            "today_score_"
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
    "100点じゃなくても、今日には今日の点数がある。💯🌱"
)
