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
    page_title="今日の予定外",
    page_icon="⚡",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "unexpected.json",
)

CATEGORIES = [
    "💼 仕事",
    "👥 人",
    "🏠 家庭",
    "🚗 移動",
    "📞 連絡",
    "💰 お金",
    "🩹 体調",
    "🌦️ 天候",
    "🛒 用事",
    "✨ その他",
]

CONTROL_LEVELS = [
    "🟢 自分で避けられた",
    "🟡 少しは調整できた",
    "🔴 自分ではどうにもならなかった",
]

RESULTS = [
    "😊 むしろ良かった",
    "😐 どちらでもない",
    "😣 困った",
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


def today_text():
    return str(date.today())


def parse_date(value):
    if not value:
        return date.today()

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def stars(value):
    value = max(
        1,
        min(int(value), 5),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def minutes_text(minutes):
    minutes = int(minutes or 0)

    hours = minutes // 60
    remaining = minutes % 60

    if hours and remaining:
        return (
            f"{hours}時間"
            f"{remaining}分"
        )

    if hours:
        return f"{hours}時間"

    return f"{remaining}分"


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

        # 古いデータがあっても動くように補完
        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "title",
                "",
            )

            record.setdefault(
                "category",
                "✨ その他",
            )

            record.setdefault(
                "impact_minutes",
                0,
            )

            record.setdefault(
                "impact_level",
                3,
            )

            record.setdefault(
                "control",
                CONTROL_LEVELS[2],
            )

            record.setdefault(
                "result",
                RESULTS[1],
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
                "favorite",
                False,
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


def add_record(
    data,
    title,
    category,
    impact_minutes,
    impact_level,
    control,
    result,
    memo,
    record_date,
):
    data["records"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "impact_minutes": int(
                impact_minutes
            ),
            "impact_level": int(
                impact_level
            ),
            "control": control,
            "result": result,
            "memo": memo,
            "record_date": str(
                record_date
            ),
            "favorite": False,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def update_record(
    data,
    record_id,
    title,
    category,
    impact_minutes,
    impact_level,
    control,
    result,
    memo,
    record_date,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["title"] = title
    record["category"] = category
    record["impact_minutes"] = int(
        impact_minutes
    )
    record["impact_level"] = int(
        impact_level
    )
    record["control"] = control
    record["result"] = result
    record["memo"] = memo
    record["record_date"] = str(
        record_date
    )
    record["updated_at"] = now_text()

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

    record["favorite"] = not record.get(
        "favorite",
        False,
    )

    record["updated_at"] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get("id")
        != record_id
    ]

    save_data(data)


# =========================================================
# 分析関数
# =========================================================

def average(values):
    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


def total_minutes(records):
    return sum(
        int(
            record.get(
                "impact_minutes",
                0,
            )
        )
        for record in records
    )


def percentage(
    part,
    whole,
):
    if not whole:
        return 0

    return round(
        part / whole * 100
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
            rgba(255, 165, 70, 0.07);

        border:
            1px solid
            rgba(255, 165, 70, 0.18);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 170, 60, 0.20),
                rgba(255, 215, 100, 0.08)
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
records = data["records"]

today = date.today()

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    ) == today_text()
]

current_month = today.strftime(
    "%Y-%m"
)

month_records = [
    record
    for record in records
    if (
        record.get(
            "record_date",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            ⚡ 今日の予定外
        </h1>

        <p>
            計画通りにいかなかった日も、
            「何が起きたか」を残してみよう。
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

today_uncontrollable = [
    record
    for record in today_records
    if record.get(
        "control"
    )
    == CONTROL_LEVELS[2]
]

today_positive = [
    record
    for record in today_records
    if record.get(
        "result"
    )
    == RESULTS[0]
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "⚡ 今日の予定外",
    f"{len(today_records)}件",
)

col2.metric(
    "⏱️ 影響時間",
    minutes_text(
        today_minutes
    ),
)

col3.metric(
    "🔴 制御できなかった",
    f"{len(today_uncontrollable)}件",
)

col4.metric(
    "😊 良い予定外",
    f"{len(today_positive)}件",
)


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "⚡ 予定外を記録"
)

st.caption(
    "大きな出来事じゃなくてもOK。"
    "予定になかったことを残してみよう。"
)

with st.form(
    "new_unexpected_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "⚡ 今日、何が起きた？",
        placeholder=(
            "例：急な仕事が入った"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        impact_minutes = (
            st.number_input(
                "⏱️ 影響時間（分）",
                min_value=0,
                max_value=1440,
                value=30,
                step=5,
            )
        )

        impact_level = st.slider(
            "💥 影響度",
            1,
            5,
            3,
        )

        st.caption(
            stars(
                impact_level
            )
        )

    with col2:
        control = st.selectbox(
            "🎛️ コントロールできた？",
            CONTROL_LEVELS,
            index=2,
        )

        result = st.selectbox(
            "✨ 結果は？",
            RESULTS,
            index=1,
        )

        record_date = (
            st.date_input(
                "📅 日付",
                value=today,
            )
        )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "例：予定していた勉強が"
            "後ろにずれた"
        ),
    )

    submitted = (
        st.form_submit_button(
            "⚡ 予定外を記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "何が起きたか入力してね。"
            )

        else:
            add_record(
                data=data,
                title=title.strip(),
                category=category,
                impact_minutes=(
                    impact_minutes
                ),
                impact_level=(
                    impact_level
                ),
                control=control,
                result=result,
                memo=memo.strip(),
                record_date=(
                    record_date
                ),
            )

            st.session_state[
                "unexpected_added"
            ] = True

            st.rerun()


if st.session_state.pop(
    "unexpected_added",
    False,
):
    st.success(
        "⚡ 記録しました！"
        " 予定が崩れたことではなく、"
        "何が起きたかを見ていこう。"
    )


# =========================================================
# 今日の予定外
# =========================================================

st.divider()

st.subheader(
    "📅 今日の予定外"
)

if not today_records:
    st.info(
        "今日はまだ予定外の記録がありません。"
    )

else:
    for record in sorted(
        today_records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
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
                [7, 1]
            )

            with col1:
                st.markdown(
                    "### "
                    + record.get(
                        "category",
                        "",
                    )
                    + " "
                    + record.get(
                        "title",
                        "",
                    )
                )

            with col2:
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
                        "today_favorite_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    "⏱️ **影響時間：** "
                    + minutes_text(
                        record.get(
                            "impact_minutes",
                            0,
                        )
                    )
                )

                st.write(
                    "💥 **影響度：** "
                    + stars(
                        record.get(
                            "impact_level",
                            3,
                        )
                    )
                )

            with col2:
                st.write(
                    "🎛️ **コントロール：** "
                    + record.get(
                        "control",
                        "",
                    )
                )

                st.write(
                    "✨ **結果：** "
                    + record.get(
                        "result",
                        "",
                    )
                )

            if record.get(
                "memo"
            ):
                st.caption(
                    "📝 "
                    + record.get(
                        "memo",
                        "",
                    )
                )

    st.markdown(
        "#### ⏱️ 今日への影響"
    )

    st.metric(
        "予定外による合計影響時間",
        minutes_text(
            today_minutes
        ),
    )


# =========================================================
# 今月のダッシュボード
# =========================================================

st.divider()

st.subheader(
    f"📊 {today.month}月の予定外"
)

if not month_records:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    month_minutes = total_minutes(
        month_records
    )

    unexpected_days = len(
        {
            record.get(
                "record_date"
            )
            for record in month_records
        }
    )

    avg_minutes = round(
        month_minutes
        / len(month_records),
        1,
    )

    uncontrollable_records = [
        record
        for record in month_records
        if record.get(
            "control"
        )
        == CONTROL_LEVELS[2]
    ]

    uncontrollable_rate = (
        percentage(
            len(
                uncontrollable_records
            ),
            len(month_records),
        )
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "⚡ 発生",
        f"{len(month_records)}件",
    )

    col2.metric(
        "⏱️ 影響時間",
        minutes_text(
            month_minutes
        ),
    )

    col3.metric(
        "📅 予定外があった日",
        f"{unexpected_days}日",
    )

    col4.metric(
        "📊 1件平均",
        f"{avg_minutes}分",
    )

    st.caption(
        "🔴 自分では制御できなかった予定外："
        f"{uncontrollable_rate}%"
    )


# =========================================================
# カテゴリー分析
# =========================================================

if month_records:
    st.markdown(
        "### 🏷️ カテゴリー別"
    )

    category_rows = []

    for category in CATEGORIES:
        category_records = [
            record
            for record in month_records
            if record.get(
                "category"
            )
            == category
        ]

        if not category_records:
            continue

        category_rows.append(
            {
                "カテゴリー": category,
                "件数": len(
                    category_records
                ),
                "影響時間（分）": (
                    total_minutes(
                        category_records
                    )
                ),
                "平均影響度": (
                    average(
                        [
                            int(
                                record.get(
                                    "impact_level",
                                    3,
                                )
                            )
                            for record
                            in category_records
                        ]
                    )
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    col1, col2 = st.columns(2)

    with col1:
        st.caption(
            "⚡ 発生件数"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )["件数"]
        )

    with col2:
        st.caption(
            "⏱️ 影響時間"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )["影響時間（分）"]
        )

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 日別影響時間
# =========================================================

if month_records:
    st.markdown(
        "### 📈 日別の影響時間"
    )

    daily_data = {}

    for record in month_records:
        record_date = record.get(
            "record_date",
            "",
        )

        daily_data[
            record_date
        ] = (
            daily_data.get(
                record_date,
                0,
            )
            + int(
                record.get(
                    "impact_minutes",
                    0,
                )
            )
        )

    daily_rows = [
        {
            "日付": day,
            "影響時間（分）": minutes,
        }
        for day, minutes
        in sorted(
            daily_data.items()
        )
    ]

    daily_df = pd.DataFrame(
        daily_rows
    )

    st.bar_chart(
        daily_df.set_index(
            "日付"
        )
    )


# =========================================================
# 予定外の正体
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "🧠 今月の予定外の正体"
    )

    category_groups = {}

    for category in CATEGORIES:
        group = [
            record
            for record in month_records
            if record.get(
                "category"
            )
            == category
        ]

        if group:
            category_groups[
                category
            ] = group

    most_common_category = max(
        category_groups,
        key=lambda category: len(
            category_groups[
                category
            ]
        ),
    )

    most_time_category = max(
        category_groups,
        key=lambda category: (
            total_minutes(
                category_groups[
                    category
                ]
            )
        ),
    )

    highest_impact_category = max(
        category_groups,
        key=lambda category: (
            average(
                [
                    int(
                        record.get(
                            "impact_level",
                            3,
                        )
                    )
                    for record
                    in category_groups[
                        category
                    ]
                ]
            )
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "⚡ 最も多い",
            most_common_category,
            (
                f"{len(category_groups[most_common_category])}"
                "件"
            ),
        )

        st.metric(
            "💥 平均影響度が最大",
            highest_impact_category,
            (
                str(
                    average(
                        [
                            int(
                                record.get(
                                    "impact_level",
                                    3,
                                )
                            )
                            for record
                            in category_groups[
                                highest_impact_category
                            ]
                        ]
                    )
                )
                + " / 5"
            ),
        )

    with col2:
        st.metric(
            "⏱️ 最も時間を使った",
            most_time_category,
            minutes_text(
                total_minutes(
                    category_groups[
                        most_time_category
                    ]
                )
            ),
        )

        st.metric(
            "🔴 制御できなかった割合",
            f"{uncontrollable_rate}%",
        )

    uncontrollable_minutes = (
        total_minutes(
            uncontrollable_records
        )
    )

    st.info(
        "💡 今月、予定外に使った時間は "
        f"**{minutes_text(month_minutes)}**。"
        "そのうち "
        f"**{minutes_text(uncontrollable_minutes)}** "
        "は、自分ではどうにもならなかった"
        "予定外でした。"
    )


# =========================================================
# 結果分析
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "✨ 予定外は悪かった？"
    )

    result_rows = []

    for result in RESULTS:
        count = len(
            [
                record
                for record in month_records
                if record.get(
                    "result"
                )
                == result
            ]
        )

        result_rows.append(
            {
                "結果": result,
                "件数": count,
            }
        )

    result_df = pd.DataFrame(
        result_rows
    )

    st.bar_chart(
        result_df.set_index(
            "結果"
        )
    )

    positive_count = len(
        [
            record
            for record in month_records
            if record.get(
                "result"
            )
            == RESULTS[0]
        ]
    )

    if positive_count:
        st.success(
            "😊 今月の予定外のうち "
            f"{positive_count}件は、"
            "結果的に「むしろ良かった」"
            "出来事でした。"
        )


# =========================================================
# コントロール分析
# =========================================================

if month_records:
    st.divider()

    st.subheader(
        "🎛️ コントロール度"
    )

    control_rows = []

    for control in CONTROL_LEVELS:
        control_records = [
            record
            for record in month_records
            if record.get(
                "control"
            )
            == control
        ]

        control_rows.append(
            {
                "コントロール": control,
                "件数": len(
                    control_records
                ),
                "影響時間（分）": (
                    total_minutes(
                        control_records
                    )
                ),
            }
        )

    control_df = pd.DataFrame(
        control_rows
    )

    st.bar_chart(
        control_df.set_index(
            "コントロール"
        )["件数"]
    )

    st.dataframe(
        control_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    record
    for record in records
    if record.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 印象に残った予定外"
    )

    for record in sorted(
        favorites,
        key=lambda item: (
            item.get(
                "record_date",
                ""
            )
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
            st.markdown(
                "### ⭐ "
                + record.get(
                    "title",
                    "",
                )
            )

            st.caption(
                record.get(
                    "record_date",
                    "",
                )
                + " ｜ "
                + record.get(
                    "category",
                    "",
                )
            )

            st.write(
                "⏱️ "
                + minutes_text(
                    record.get(
                        "impact_minutes",
                        0,
                    )
                )
            )

            st.write(
                record.get(
                    "result",
                    "",
                )
            )

            if record.get(
                "memo"
            ):
                st.write(
                    "📝 "
                    + record.get(
                        "memo",
                        "",
                    )
                )

            if st.button(
                "⭐ お気に入りから外す",
                key=(
                    "favorite_remove_"
                    + record_id
                ),
            ):
                toggle_favorite(
                    data,
                    record_id,
                )

                st.rerun()


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 予定外履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "仕事、渋滞、電話……"
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
    control_filter = st.selectbox(
        "コントロール",
        ["すべて"]
        + CONTROL_LEVELS,
        key="history_control",
    )

with col3:
    result_filter = st.selectbox(
        "結果",
        ["すべて"] + RESULTS,
        key="history_result",
    )


filtered_records = []

for record in records:
    if (
        category_filter
        != "すべて"
        and record.get(
            "category"
        )
        != category_filter
    ):
        continue

    if (
        control_filter
        != "すべて"
        and record.get(
            "control"
        )
        != control_filter
    ):
        continue

    if (
        result_filter
        != "すべて"
        and record.get(
            "result"
        )
        != result_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                record.get(
                    "title",
                    "",
                ),
                record.get(
                    "category",
                    "",
                ),
                record.get(
                    "memo",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text
            .strip()
            .lower()
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
    history_rows = []

    for record in sorted(
        filtered_records,
        key=lambda item: (
            item.get(
                "record_date",
                ""
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        history_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "予定外": record.get(
                    "title",
                    "",
                ),
                "カテゴリー": record.get(
                    "category",
                    "",
                ),
                "影響時間": minutes_text(
                    record.get(
                        "impact_minutes",
                        0,
                    )
                ),
                "影響度": stars(
                    record.get(
                        "impact_level",
                        3,
                    )
                ),
                "コントロール": (
                    record.get(
                        "control",
                        "",
                    )
                ),
                "結果": record.get(
                    "result",
                    "",
                ),
                "⭐": (
                    "⭐"
                    if record.get(
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
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
        key=lambda item: (
            item.get(
                "record_date",
                ""
            ),
            item.get(
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

        with st.expander(
            record.get(
                "record_date",
                "",
            )
            + " ｜ "
            + record.get(
                "title",
                "",
            )
        ):
            edit_title = st.text_input(
                "予定外",
                value=record.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + record_id
                ),
            )

            current_category = (
                record.get(
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
                        + record_id
                    ),
                )
            )

            edit_minutes = (
                st.number_input(
                    "影響時間（分）",
                    min_value=0,
                    max_value=1440,
                    value=int(
                        record.get(
                            "impact_minutes",
                            0,
                        )
                    ),
                    step=5,
                    key=(
                        "edit_minutes_"
                        + record_id
                    ),
                )
            )

            edit_impact = st.slider(
                "影響度",
                1,
                5,
                int(
                    record.get(
                        "impact_level",
                        3,
                    )
                ),
                key=(
                    "edit_impact_"
                    + record_id
                ),
            )

            old_control = record.get(
                "control",
                CONTROL_LEVELS[2],
            )

            control_index = (
                CONTROL_LEVELS.index(
                    old_control
                )
                if old_control
                in CONTROL_LEVELS
                else 2
            )

            edit_control = (
                st.selectbox(
                    "コントロール",
                    CONTROL_LEVELS,
                    index=control_index,
                    key=(
                        "edit_control_"
                        + record_id
                    ),
                )
            )

            old_result = record.get(
                "result",
                RESULTS[1],
            )

            result_index = (
                RESULTS.index(
                    old_result
                )
                if old_result
                in RESULTS
                else 1
            )

            edit_result = (
                st.selectbox(
                    "結果",
                    RESULTS,
                    index=result_index,
                    key=(
                        "edit_result_"
                        + record_id
                    ),
                )
            )

            edit_memo = st.text_area(
                "メモ",
                value=record.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + record_id
                ),
            )

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
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "予定外の出来事を入力してね。"
                        )

                    else:
                        update_record(
                            data=data,
                            record_id=record_id,
                            title=(
                                edit_title.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            impact_minutes=(
                                edit_minutes
                            ),
                            impact_level=(
                                edit_impact
                            ),
                            control=(
                                edit_control
                            ),
                            result=(
                                edit_result
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                            record_date=(
                                edit_date
                            ),
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ お気に入り解除"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_favorite_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            confirm_delete = (
                st.checkbox(
                    "削除を確認",
                    key=(
                        "confirm_delete_"
                        + record_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + record_id
                ),
                disabled=(
                    not confirm_delete
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
            "unexpected_today_"
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
    "⚡ 計画通りにいかなかったことより、"
    "その日に何が起きたのかを見てみよう。"
)
