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
    page_title="今日、助かった！",
    page_icon="🙌",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "helped.json")

HELP_TYPES = [
    "👤 人",
    "🤖 AI",
    "💡 過去の自分",
    "📱 アプリ",
    "🛠️ 道具・仕組み",
    "📚 知識",
    "🍀 偶然",
    "✨ その他",
]

RESCUE_TYPES = [
    "⏰ 時間不足",
    "😣 ストレス",
    "🧠 考える負担",
    "💰 出費",
    "😴 疲労",
    "🤦 ミス",
    "📅 忘れ",
    "🚨 トラブル",
    "✨ その他",
]

RATING_LABELS = {
    1: "⭐ ちょっと助かった",
    2: "⭐⭐ まあ助かった",
    3: "⭐⭐⭐ 助かった！",
    4: "⭐⭐⭐⭐ かなり助かった！",
    5: "⭐⭐⭐⭐⭐ めちゃくちゃ助かった！",
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


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


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime("%Y/%m/%d")


def format_datetime(value):
    parsed = parse_datetime(value)

    if not parsed:
        return "-"

    return parsed.strftime("%Y/%m/%d %H:%M")


def average(values):
    values = [
        value
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(sum(values) / len(values), 1)


def format_minutes(minutes):
    minutes = int(minutes or 0)

    if minutes <= 0:
        return "0分"

    hours = minutes // 60
    remain = minutes % 60

    if hours and remain:
        return f"{hours}時間{remain}分"

    if hours:
        return f"{hours}時間"

    return f"{remain}分"


def stars(rating):
    rating = int(rating or 0)
    return "⭐" * rating


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "records": [],
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

    if not os.path.exists(DATA_FILE):
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
            "records",
            [],
        )

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
                "help_type",
                "✨ その他",
            )
            record.setdefault(
                "rating",
                3,
            )
            record.setdefault(
                "rescued_from",
                "✨ その他",
            )
            record.setdefault(
                "result",
                "",
            )
            record.setdefault(
                "saved_minutes",
                0,
            )
            record.setdefault(
                "saved_money",
                0,
            )
            record.setdefault(
                "reusable",
                False,
            )
            record.setdefault(
                "favorite",
                False,
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
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# CRUD
# =========================================================

def get_record(data, record_id):
    return next(
        (
            record
            for record in data["records"]
            if record.get("id") == record_id
        ),
        None,
    )


def add_record(
    data,
    title,
    help_type,
    rating,
    rescued_from,
    result,
    saved_minutes,
    saved_money,
    reusable,
    memo,
    record_date,
):
    record = {
        "id": create_id(),
        "title": title,
        "help_type": help_type,
        "rating": int(rating),
        "rescued_from": rescued_from,
        "result": result,
        "saved_minutes": int(saved_minutes),
        "saved_money": int(saved_money),
        "reusable": bool(reusable),
        "favorite": False,
        "memo": memo,
        "record_date": str(record_date),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["records"].append(record)
    save_data(data)


def update_record(
    data,
    record_id,
    title,
    help_type,
    rating,
    rescued_from,
    result,
    saved_minutes,
    saved_money,
    reusable,
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
    record["help_type"] = help_type
    record["rating"] = int(rating)
    record["rescued_from"] = rescued_from
    record["result"] = result
    record["saved_minutes"] = int(saved_minutes)
    record["saved_money"] = int(saved_money)
    record["reusable"] = bool(reusable)
    record["memo"] = memo
    record["record_date"] = str(record_date)
    record["updated_at"] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get("id") != record_id
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

    record["favorite"] = not record.get(
        "favorite",
        False,
    )

    record["updated_at"] = now_text()

    save_data(data)


def toggle_reusable(
    data,
    record_id,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["reusable"] = not record.get(
        "reusable",
        False,
    )

    record["updated_at"] = now_text()

    save_data(data)


# =========================================================
# 集計関数
# =========================================================

def records_for_month(records):
    prefix = date.today().strftime("%Y-%m")

    return [
        record
        for record in records
        if (
            record.get(
                "record_date",
                "",
            )
            or ""
        ).startswith(prefix)
    ]


def records_for_today(records):
    today = today_text()

    return [
        record
        for record in records
        if record.get("record_date") == today
    ]


def grouped_title_stats(records):
    stats = {}

    for record in records:
        title = record.get(
            "title",
            "",
        ).strip()

        if not title:
            continue

        key = title.lower()

        if key not in stats:
            stats[key] = {
                "title": title,
                "count": 0,
                "ratings": [],
                "saved_minutes": 0,
                "saved_money": 0,
            }

        stats[key]["count"] += 1
        stats[key]["ratings"].append(
            int(record.get("rating", 0))
        )
        stats[key]["saved_minutes"] += int(
            record.get(
                "saved_minutes",
                0,
            )
        )
        stats[key]["saved_money"] += int(
            record.get(
                "saved_money",
                0,
            )
        )

    rows = []

    for value in stats.values():
        rows.append(
            {
                "助けてくれたもの": value["title"],
                "回数": value["count"],
                "平均助かり度": average(
                    value["ratings"]
                ),
                "節約時間": value["saved_minutes"],
                "節約金額": value["saved_money"],
            }
        )

    return rows


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
        background: rgba(255, 180, 70, 0.08);
        border: 1px solid rgba(255, 180, 70, 0.18);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 70, 0.18),
                rgba(110, 200, 160, 0.10)
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

    .mvp-box {
        padding: 25px;
        border-radius: 22px;
        background: rgba(255, 190, 70, 0.09);
        margin: 15px 0;
    }

    .big-stars {
        font-size: 1.6rem;
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

today_records = records_for_today(
    records
)

month_records = records_for_month(
    records
)

favorites = [
    record
    for record in records
    if record.get(
        "favorite",
        False,
    )
]

reusable_records = [
    record
    for record in records
    if record.get(
        "reusable",
        False,
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🙌 今日、助かった！</h1>
        <p>
            今日助かったことは、
            明日の自分を助けるヒントになる。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

total_minutes = sum(
    int(record.get("saved_minutes", 0))
    for record in records
)

total_money = sum(
    int(record.get("saved_money", 0))
    for record in records
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🙌 今日助かった",
    f"{len(today_records)}回",
)

col2.metric(
    "📚 総記録",
    f"{len(records)}回",
)

col3.metric(
    "⏰ 浮いた時間",
    format_minutes(total_minutes),
)

col4.metric(
    "💰 節約",
    f"¥{total_money:,}",
)


# =========================================================
# 新規記録
# =========================================================

st.divider()

st.subheader(
    "🙌 今日、何に助けられた？"
)

with st.form(
    "new_record_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "✨ 助けてくれたもの",
        placeholder=(
            "例：昨日作っておいた買い物リスト"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        help_type = st.selectbox(
            "🙌 種類",
            HELP_TYPES,
        )

        rating = st.select_slider(
            "⭐ 助かり度",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda value: (
                RATING_LABELS[value]
            ),
        )

    with col2:
        rescued_from = st.selectbox(
            "🛟 何から助けられた？",
            RESCUE_TYPES,
        )

        record_date = st.date_input(
            "📅 日付",
            value=date.today(),
            max_value=date.today(),
        )

    result = st.text_area(
        "🌱 どう助かった？",
        placeholder=(
            "例：買い忘れせずに済んだ"
        ),
    )

    st.markdown(
        "#### 🎁 助かった結果"
    )

    col1, col2 = st.columns(2)

    with col1:
        saved_minutes = st.number_input(
            "⏰ 浮いた時間（分・任意）",
            min_value=0,
            max_value=1440,
            value=0,
            step=5,
        )

    with col2:
        saved_money = st.number_input(
            "💰 節約できた金額（円・任意）",
            min_value=0,
            max_value=10000000,
            value=0,
            step=100,
        )

    reusable = st.checkbox(
        "⭐ また使いたい・また役立ちそう"
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "次回の自分に残したいことがあれば"
        ),
    )

    submitted = st.form_submit_button(
        "🙌 助かった！を記録",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if not title.strip():
            st.warning(
                "助けてくれたものを入力してね。"
            )
        else:
            add_record(
                data=data,
                title=title.strip(),
                help_type=help_type,
                rating=rating,
                rescued_from=rescued_from,
                result=result.strip(),
                saved_minutes=saved_minutes,
                saved_money=saved_money,
                reusable=reusable,
                memo=memo.strip(),
                record_date=record_date,
            )

            st.rerun()


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "🌞 今日の「助かった！」"
)

if not today_records:
    st.info(
        "今日はまだ記録がありません。"
        "小さな「助かった！」も残してみよう。"
    )

else:
    today_sorted = sorted(
        today_records,
        key=lambda record: (
            record.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for record in today_sorted:
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
                st.subheader(
                    record.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if record.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
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

            st.write(
                f"{record.get('help_type', '')}"
                f" ｜ "
                f"{record.get('rescued_from', '')}"
            )

            st.markdown(
                f"<div class='big-stars'>"
                f"{stars(record.get('rating', 0))}"
                f"</div>",
                unsafe_allow_html=True,
            )

            if record.get("result"):
                st.write(
                    "🌱 "
                    + record.get(
                        "result",
                        "",
                    )
                )

            result_parts = []

            if int(
                record.get(
                    "saved_minutes",
                    0,
                )
            ) > 0:
                result_parts.append(
                    "⏰ "
                    + format_minutes(
                        record.get(
                            "saved_minutes",
                            0,
                        )
                    )
                )

            if int(
                record.get(
                    "saved_money",
                    0,
                )
            ) > 0:
                result_parts.append(
                    f"💰 ¥"
                    f"{int(record.get('saved_money', 0)):,}"
                )

            if result_parts:
                st.success(
                    " ｜ ".join(
                        result_parts
                    )
                )

            if record.get(
                "reusable",
                False,
            ):
                st.info(
                    "⭐ また使いたい方法"
                )

            if record.get("memo"):
                st.caption(
                    "📝 "
                    + record.get(
                        "memo",
                        "",
                    )
                )

            if st.button(
                (
                    "⭐ また使いたいから外す"
                    if record.get(
                        "reusable",
                        False,
                    )
                    else "⭐ また使いたい"
                ),
                key=(
                    "today_reuse_"
                    + record_id
                ),
                use_container_width=True,
            ):
                toggle_reusable(
                    data,
                    record_id,
                )
                st.rerun()


# =========================================================
# 今月
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の「助かった！」"
)

month_minutes = sum(
    int(record.get("saved_minutes", 0))
    for record in month_records
)

month_money = sum(
    int(record.get("saved_money", 0))
    for record in month_records
)

month_ratings = [
    int(record.get("rating", 0))
    for record in month_records
]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🙌 記録",
    f"{len(month_records)}回",
)

col2.metric(
    "⭐ 平均助かり度",
    (
        f"{average(month_ratings):.1f}/5"
        if month_ratings
        else "-"
    ),
)

col3.metric(
    "⏰ 浮いた時間",
    format_minutes(month_minutes),
)

col4.metric(
    "💰 節約",
    f"¥{month_money:,}",
)


# =========================================================
# 今月の種類分析
# =========================================================

if month_records:
    type_counts = {}

    for record in month_records:
        help_type = record.get(
            "help_type",
            "✨ その他",
        )

        type_counts[help_type] = (
            type_counts.get(
                help_type,
                0,
            )
            + 1
        )

    most_help_type = max(
        type_counts,
        key=type_counts.get,
    )

    st.info(
        "🙌 今月もっとも助けてくれた種類："
        f" **{most_help_type}**"
    )

    type_df = pd.DataFrame(
        [
            {
                "種類": key,
                "回数": value,
            }
            for key, value
            in type_counts.items()
        ]
    ).sort_values(
        "回数",
        ascending=False,
    )

    st.markdown(
        "### 🙌 助けてくれた存在"
    )

    st.bar_chart(
        type_df.set_index(
            "種類"
        )
    )


# =========================================================
# 何から助かった？
# =========================================================

if month_records:
    rescue_counts = {}

    for record in month_records:
        rescue = record.get(
            "rescued_from",
            "✨ その他",
        )

        rescue_counts[rescue] = (
            rescue_counts.get(
                rescue,
                0,
            )
            + 1
        )

    rescue_df = pd.DataFrame(
        [
            {
                "助けられたもの": key,
                "回数": value,
            }
            for key, value
            in rescue_counts.items()
        ]
    ).sort_values(
        "回数",
        ascending=False,
    )

    st.markdown(
        "### 🛟 何から助けられた？"
    )

    st.bar_chart(
        rescue_df.set_index(
            "助けられたもの"
        )
    )


# =========================================================
# 今月のMVP
# =========================================================

month_stats = grouped_title_stats(
    month_records
)

if month_stats:
    st.divider()

    st.subheader(
        "🏆 今月の助かったMVP"
    )

    # 回数・評価・時間節約を軽く加味
    for row in month_stats:
        row["MVPスコア"] = (
            row["回数"] * 10
            + row["平均助かり度"] * 5
            + min(
                row["節約時間"] / 10,
                20,
            )
        )

    month_stats = sorted(
        month_stats,
        key=lambda row: (
            row["MVPスコア"]
        ),
        reverse=True,
    )

    mvp = month_stats[0]

    st.markdown(
        f"""
        <div class="mvp-box">
            <h2>🏆 {mvp["助けてくれたもの"]}</h2>
            <p>
                🙌 {mvp["回数"]}回助かった<br>
                ⭐ 平均 {mvp["平均助かり度"]:.1f} / 5<br>
                ⏰ {format_minutes(mvp["節約時間"])}節約<br>
                💰 ¥{mvp["節約金額"]:,}節約
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# よく助けてくれるもの
# =========================================================

all_stats = grouped_title_stats(
    records
)

if all_stats:
    st.divider()

    st.subheader(
        "🧠 あなたをよく助けるもの"
    )

    stats_df = pd.DataFrame(
        all_stats
    ).sort_values(
        [
            "回数",
            "平均助かり度",
        ],
        ascending=False,
    )

    display_df = stats_df.copy()

    display_df["節約時間"] = (
        display_df["節約時間"]
        .apply(format_minutes)
    )

    display_df["節約金額"] = (
        display_df["節約金額"]
        .apply(
            lambda value: (
                f"¥{int(value):,}"
            )
        )
    )

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "回数": st.column_config.NumberColumn(
                "🙌 回数",
                format="%d回",
            ),
            "平均助かり度": (
                st.column_config.NumberColumn(
                    "⭐ 平均",
                    format="%.1f",
                )
            ),
        },
    )


# =========================================================
# 過去の自分特集
# =========================================================

past_self_records = [
    record
    for record in month_records
    if record.get(
        "help_type"
    ) == "💡 過去の自分"
]

if past_self_records:
    st.divider()

    st.subheader(
        "💡 過去の自分、ありがとう"
    )

    st.write(
        f"今月、過去の自分に"
        f" **{len(past_self_records)}回** "
        "助けられています。"
    )

    for record in sorted(
        past_self_records,
        key=lambda item: (
            item.get(
                "record_date",
                "",
            )
        ),
        reverse=True,
    )[:8]:
        with st.container(
            border=True
        ):
            st.write(
                f"**{record.get('title', '')}**"
            )

            if record.get(
                "result"
            ):
                st.caption(
                    record.get(
                        "result",
                        "",
                    )
                )

    st.success(
        "💡 過去のあなた、"
        "結構いい仕事してます。"
    )


# =========================================================
# また使いたい仕組み
# =========================================================

if reusable_records:
    st.divider()

    st.subheader(
        "⭐ また使いたい「助かった！」"
    )

    reusable_sorted = sorted(
        reusable_records,
        key=lambda record: (
            int(
                record.get(
                    "rating",
                    0,
                )
            ),
            record.get(
                "record_date",
                "",
            ),
        ),
        reverse=True,
    )

    for record in reusable_sorted[:10]:
        with st.container(
            border=True
        ):
            st.write(
                f"**{record.get('title', '')}**"
            )

            st.caption(
                f"{record.get('help_type', '')}"
                f" ｜ "
                f"{stars(record.get('rating', 0))}"
            )

            if record.get("result"):
                st.write(
                    record.get(
                        "result",
                        "",
                    )
                )


# =========================================================
# ランダム再発見
# =========================================================

old_records = [
    record
    for record in records
    if (
        parse_date(
            record.get(
                "record_date"
            )
        )
        and (
            date.today()
            - parse_date(
                record.get(
                    "record_date"
                )
            )
        ).days >= 14
    )
]

if old_records:
    st.divider()

    st.subheader(
        "🎲 こんなことで助かってたよ"
    )

    old_ids = [
        record.get("id")
        for record in old_records
    ]

    rediscovery_id = (
        st.session_state.get(
            "help_rediscovery_id"
        )
    )

    if rediscovery_id not in old_ids:
        rediscovery_id = random.choice(
            old_ids
        )

        st.session_state[
            "help_rediscovery_id"
        ] = rediscovery_id

    rediscovery = get_record(
        data,
        rediscovery_id,
    )

    if rediscovery:
        old_date = parse_date(
            rediscovery.get(
                "record_date"
            )
        )

        days_ago = (
            date.today() - old_date
        ).days

        with st.container(
            border=True
        ):
            st.caption(
                f"{days_ago}日前"
            )

            st.subheader(
                rediscovery.get(
                    "title",
                    "",
                )
            )

            st.write(
                f"{rediscovery.get('help_type', '')}"
                f" ｜ "
                f"{stars(rediscovery.get('rating', 0))}"
            )

            if rediscovery.get(
                "result"
            ):
                st.write(
                    "🌱 "
                    + rediscovery.get(
                        "result",
                        "",
                    )
                )

            if rediscovery.get(
                "memo"
            ):
                st.caption(
                    "📝 "
                    + rediscovery.get(
                        "memo",
                        "",
                    )
                )

            if st.button(
                "⭐ また使いたい",
                key="rediscovery_reuse",
                type="primary",
                use_container_width=True,
            ):
                if not rediscovery.get(
                    "reusable",
                    False,
                ):
                    toggle_reusable(
                        data,
                        rediscovery_id,
                    )

                st.session_state.pop(
                    "help_rediscovery_id",
                    None,
                )

                st.rerun()

        if st.button(
            "🎲 別の記録を見る",
            use_container_width=True,
        ):
            alternatives = [
                record_id
                for record_id in old_ids
                if record_id
                != rediscovery_id
            ]

            if alternatives:
                st.session_state[
                    "help_rediscovery_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 曜日別
# =========================================================

if records:
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
        day: 0
        for day in weekday_names
    }

    for record in records:
        parsed = parse_date(
            record.get(
                "record_date"
            )
        )

        if parsed:
            weekday_counts[
                weekday_names[
                    parsed.weekday()
                ]
            ] += 1

    weekday_df = pd.DataFrame(
        [
            {
                "曜日": day,
                "回数": weekday_counts[day],
            }
            for day in weekday_names
        ]
    )

    st.divider()

    st.subheader(
        "📅 曜日別「助かった！」"
    )

    st.bar_chart(
        weekday_df.set_index(
            "曜日"
        )
    )


# =========================================================
# お気に入り
# =========================================================

if favorites:
    st.divider()

    st.subheader(
        "⭐ 特に覚えておきたい"
    )

    for record in sorted(
        favorites,
        key=lambda item: (
            item.get(
                "record_date",
                "",
            )
        ),
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            st.write(
                f"**{record.get('title', '')}**"
            )

            st.caption(
                f"{format_date(record.get('record_date'))}"
                f" ｜ "
                f"{record.get('help_type', '')}"
                f" ｜ "
                f"{stars(record.get('rating', 0))}"
            )

            if record.get(
                "result"
            ):
                st.write(
                    record.get(
                        "result",
                        "",
                    )
                )


# =========================================================
# 助かった図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 助かった図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "AI、買い物リスト、準備……"
    ),
)

col1, col2, col3 = st.columns(3)

with col1:
    type_filter = st.selectbox(
        "種類",
        ["すべて"] + HELP_TYPES,
        key="library_type",
    )

with col2:
    rating_filter = st.selectbox(
        "助かり度",
        [
            "すべて",
            "⭐5",
            "⭐4以上",
            "⭐3以上",
        ],
        key="library_rating",
    )

with col3:
    reusable_filter = st.selectbox(
        "また使いたい",
        [
            "すべて",
            "⭐ また使いたいのみ",
        ],
        key="library_reusable",
    )


filtered_records = []

for record in records:
    if (
        type_filter != "すべて"
        and record.get(
            "help_type"
        ) != type_filter
    ):
        continue

    rating_value = int(
        record.get(
            "rating",
            0,
        )
    )

    if (
        rating_filter == "⭐5"
        and rating_value != 5
    ):
        continue

    if (
        rating_filter == "⭐4以上"
        and rating_value < 4
    ):
        continue

    if (
        rating_filter == "⭐3以上"
        and rating_value < 3
    ):
        continue

    if (
        reusable_filter
        == "⭐ また使いたいのみ"
        and not record.get(
            "reusable",
            False,
        )
    ):
        continue

    searchable = " ".join(
        [
            record.get(
                "title",
                "",
            ),
            record.get(
                "help_type",
                "",
            ),
            record.get(
                "rescued_from",
                "",
            ),
            record.get(
                "result",
                "",
            ),
            record.get(
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

    filtered_records.append(
        record
    )


if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    library_rows = []

    for record in sorted(
        filtered_records,
        key=lambda item: (
            item.get(
                "record_date",
                "",
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        library_rows.append(
            {
                "日付": format_date(
                    record.get(
                        "record_date"
                    )
                ),
                "助けてくれたもの": (
                    record.get(
                        "title",
                        "",
                    )
                ),
                "種類": (
                    record.get(
                        "help_type",
                        "",
                    )
                ),
                "助かり度": stars(
                    record.get(
                        "rating",
                        0,
                    )
                ),
                "何から": (
                    record.get(
                        "rescued_from",
                        "",
                    )
                ),
                "時間": format_minutes(
                    record.get(
                        "saved_minutes",
                        0,
                    )
                ),
                "節約": (
                    f"¥{int(record.get('saved_money', 0)):,}"
                ),
                "再利用": (
                    "⭐"
                    if record.get(
                        "reusable",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            library_rows
        ),
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
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
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

        with st.expander(
            (
                format_date(
                    record.get(
                        "record_date"
                    )
                )
                + "｜"
                + record.get(
                    "title",
                    "",
                )
            )
        ):
            edit_title = st.text_input(
                "助けてくれたもの",
                value=record.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + record_id
                ),
            )

            old_type = record.get(
                "help_type",
                "✨ その他",
            )

            type_index = (
                HELP_TYPES.index(
                    old_type
                )
                if old_type
                in HELP_TYPES
                else len(
                    HELP_TYPES
                ) - 1
            )

            edit_type = st.selectbox(
                "種類",
                HELP_TYPES,
                index=type_index,
                key=(
                    "edit_type_"
                    + record_id
                ),
            )

            edit_rating = (
                st.select_slider(
                    "助かり度",
                    options=[
                        1,
                        2,
                        3,
                        4,
                        5,
                    ],
                    value=int(
                        record.get(
                            "rating",
                            3,
                        )
                    ),
                    format_func=lambda value: (
                        RATING_LABELS[value]
                    ),
                    key=(
                        "edit_rating_"
                        + record_id
                    ),
                )
            )

            old_rescue = record.get(
                "rescued_from",
                "✨ その他",
            )

            rescue_index = (
                RESCUE_TYPES.index(
                    old_rescue
                )
                if old_rescue
                in RESCUE_TYPES
                else len(
                    RESCUE_TYPES
                ) - 1
            )

            edit_rescue = st.selectbox(
                "何から助けられた？",
                RESCUE_TYPES,
                index=rescue_index,
                key=(
                    "edit_rescue_"
                    + record_id
                ),
            )

            edit_result = st.text_area(
                "どう助かった？",
                value=record.get(
                    "result",
                    "",
                ),
                key=(
                    "edit_result_"
                    + record_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                edit_minutes = (
                    st.number_input(
                        "浮いた時間（分）",
                        min_value=0,
                        max_value=1440,
                        value=int(
                            record.get(
                                "saved_minutes",
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

            with col2:
                edit_money = (
                    st.number_input(
                        "節約金額（円）",
                        min_value=0,
                        max_value=10000000,
                        value=int(
                            record.get(
                                "saved_money",
                                0,
                            )
                        ),
                        step=100,
                        key=(
                            "edit_money_"
                            + record_id
                        ),
                    )
                )

            edit_reusable = (
                st.checkbox(
                    "⭐ また使いたい",
                    value=record.get(
                        "reusable",
                        False,
                    ),
                    key=(
                        "edit_reusable_"
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

            current_date = (
                parse_date(
                    record.get(
                        "record_date"
                    )
                )
                or date.today()
            )

            edit_date = st.date_input(
                "日付",
                value=current_date,
                max_value=date.today(),
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
                    type="primary",
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.warning(
                            "助けてくれたものを入力してね。"
                        )
                    else:
                        update_record(
                            data=data,
                            record_id=record_id,
                            title=edit_title.strip(),
                            help_type=edit_type,
                            rating=edit_rating,
                            rescued_from=edit_rescue,
                            result=edit_result.strip(),
                            saved_minutes=edit_minutes,
                            saved_money=edit_money,
                            reusable=edit_reusable,
                            memo=edit_memo.strip(),
                            record_date=edit_date,
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if record.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_favorite_"
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
                    "この記録を削除する",
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
            "today_helped_"
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
    "🙌 今日助かったことは、"
    "明日の自分を助けるヒントになる。"
)
