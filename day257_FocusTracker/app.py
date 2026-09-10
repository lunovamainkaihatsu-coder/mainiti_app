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
    page_title="今の集中度",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "focus_data.json",
)

CATEGORIES = [
    "🤖 AI・プログラミング",
    "📚 勉強",
    "🎨 イラスト",
    "✍️ 文章",
    "💼 仕事",
    "🧹 家事",
    "📖 読書",
    "🎮 趣味",
    "✨ その他",
]

SLEEPINESS = [
    "😎 全然眠くない",
    "🙂 少し眠い",
    "🥱 眠い",
    "😵 かなり眠い",
]

PLACES = [
    "🏠 自宅",
    "☕ カフェ",
    "🏢 職場",
    "📚 図書館",
    "🚃 移動中",
    "🌳 外",
    "✨ その他",
]

TIME_PERIODS = [
    "🌅 朝",
    "☀️ 昼",
    "🌆 夕方",
    "🌙 夜",
    "🌌 深夜",
]

MOODS = [
    "😄 とても良い",
    "🙂 良い",
    "😐 普通",
    "😕 モヤモヤ",
    "😢 落ち込み",
    "🔥 やる気",
    "😌 穏やか",
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
                "focus",
                50,
            )

            record.setdefault(
                "task",
                "",
            )

            record.setdefault(
                "category",
                "✨ その他",
            )

            record.setdefault(
                "sleepiness",
                "🙂 少し眠い",
            )

            record.setdefault(
                "place",
                "🏠 自宅",
            )

            record.setdefault(
                "time_period",
                "🌅 朝",
            )

            record.setdefault(
                "mood",
                "😐 普通",
            )

            record.setdefault(
                "memo",
                "",
            )

            record.setdefault(
                "record_date",
                str(date.today()),
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
            for record in data[
                "records"
            ]
            if record.get(
                "id"
            )
            == record_id
        ),
        None,
    )


def parse_date(
    text,
):
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


def format_date(
    text,
):
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


def format_datetime(
    text,
):
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


def detect_time_period():
    hour = datetime.now().hour

    if 5 <= hour < 11:
        return "🌅 朝"

    if 11 <= hour < 16:
        return "☀️ 昼"

    if 16 <= hour < 19:
        return "🌆 夕方"

    if 19 <= hour < 24:
        return "🌙 夜"

    return "🌌 深夜"


def focus_level_text(
    focus,
):
    if focus >= 90:
        return "🔥 超集中"

    if focus >= 75:
        return "🟢 かなり集中"

    if focus >= 60:
        return "🙂 集中できている"

    if focus >= 40:
        return "🟡 まずまず"

    if focus >= 20:
        return "🟠 集中しづらい"

    return "🔴 かなり低い"


def average_focus(
    records,
):
    if not records:
        return 0

    return round(
        sum(
            int(
                record.get(
                    "focus",
                    0,
                )
            )
            for record in records
        )
        / len(records),
        1,
    )


def grouped_average(
    records,
    key,
):
    if not records:
        return pd.DataFrame()

    rows = []

    for record in records:
        rows.append(
            {
                "条件": record.get(
                    key,
                    "不明",
                ),
                "集中度": int(
                    record.get(
                        "focus",
                        0,
                    )
                ),
            }
        )

    df = pd.DataFrame(
        rows
    )

    result = (
        df.groupby(
            "条件",
            as_index=False,
        )
        .agg(
            平均集中度=(
                "集中度",
                "mean",
            ),
            記録回数=(
                "集中度",
                "count",
            ),
        )
    )

    result[
        "平均集中度"
    ] = (
        result[
            "平均集中度"
        ]
        .round(1)
    )

    return result.sort_values(
        "平均集中度",
        ascending=False,
    )


# =========================================================
# CRUD
# =========================================================

def add_record(
    data,
    focus,
    task,
    category,
    sleepiness,
    place,
    time_period,
    mood,
    memo,
    record_date,
):
    data[
        "records"
    ].append(
        {
            "id": create_id(),
            "focus": int(
                focus
            ),
            "task": task,
            "category": category,
            "sleepiness": sleepiness,
            "place": place,
            "time_period": time_period,
            "mood": mood,
            "memo": memo,
            "record_date": str(
                record_date
            ),
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_record(
    data,
    record_id,
    focus,
    task,
    category,
    sleepiness,
    place,
    time_period,
    mood,
    memo,
    record_date,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record[
        "focus"
    ] = int(
        focus
    )

    record[
        "task"
    ] = task

    record[
        "category"
    ] = category

    record[
        "sleepiness"
    ] = sleepiness

    record[
        "place"
    ] = place

    record[
        "time_period"
    ] = time_period

    record[
        "mood"
    ] = mood

    record[
        "memo"
    ] = memo

    record[
        "record_date"
    ] = str(
        record_date
    )

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
        padding: 28px;
        border-radius: 24px;
        margin-bottom: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 120, 255, 0.16),
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

    .focus-box {
        padding: 24px;
        border-radius: 22px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 130, 255, 0.11),
                rgba(100, 220, 180, 0.07)
            );
    }

    .focus-number {
        font-size: 2.7rem;
        font-weight: 900;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    .focus-label {
        font-weight: 700;
        opacity: 0.78;
    }

    .best-condition {
        padding: 25px;
        border-radius: 22px;
        margin-bottom: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 70, 0.12),
                rgba(110, 130, 255, 0.08)
            );
    }

    .best-title {
        font-size: 0.9rem;
        opacity: 0.7;
        font-weight: 700;
    }

    .best-value {
        font-size: 1.45rem;
        font-weight: 900;
        margin-top: 8px;
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

today_text = str(
    date.today()
)

current_month = date.today().strftime(
    "%Y-%m"
)

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    )
    == today_text
]

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

today_average = average_focus(
    today_records
)

month_average = average_focus(
    month_records
)

today_highest = (
    max(
        [
            int(
                record.get(
                    "focus",
                    0,
                )
            )
            for record in today_records
        ],
        default=0,
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🧠 今の集中度</h1>

        <p>
            集中できない自分を責めるより、
            集中できる条件を探してみよう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

col1.metric(
    "🧠 今日の平均",
    (
        f"{today_average}%"
        if today_records
        else "-"
    ),
)

col2.metric(
    "🔥 今日の最高",
    (
        f"{today_highest}%"
        if today_records
        else "-"
    ),
)

col3.metric(
    "📊 今月平均",
    (
        f"{month_average}%"
        if month_records
        else "-"
    ),
)

col4.metric(
    "📝 今月の記録",
    f"{len(month_records)}回",
)


# =========================================================
# 今の集中度を記録
# =========================================================

st.divider()

st.subheader(
    "✍️ 今の集中度を記録"
)

with st.form(
    "add_focus_form"
):
    focus = st.slider(
        "🧠 集中度",
        min_value=0,
        max_value=100,
        value=60,
        step=5,
    )

    st.markdown(
        f"""
        <div class="focus-box">

            <div class="focus-label">
                今の集中度
            </div>

            <div class="focus-number">
                {focus}%
            </div>

            <div>
                {focus_level_text(focus)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    task = st.text_input(
        "今なにをしている？",
        placeholder=(
            "例：Pythonの勉強"
        ),
    )

    col1, col2 = st.columns(
        2
    )

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        sleepiness = st.selectbox(
            "眠気",
            SLEEPINESS,
        )

        mood = st.selectbox(
            "気分",
            MOODS,
        )

    with col2:
        place = st.selectbox(
            "場所",
            PLACES,
        )

        detected_period = (
            detect_time_period()
        )

        time_period = st.selectbox(
            "時間帯",
            TIME_PERIODS,
            index=TIME_PERIODS.index(
                detected_period
            ),
        )

        record_date = st.date_input(
            "記録日",
            value=date.today(),
        )

    memo = st.text_area(
        "メモ",
        placeholder=(
            "例：始めるまでは重かったけど、"
            "10分くらいで集中に入れた。"
        ),
        height=100,
    )

    submitted = (
        st.form_submit_button(
            "🧠 集中度を記録",
            use_container_width=True,
        )
    )

    if submitted:
        if not task.strip():
            st.error(
                "作業内容を入力してください。"
            )

        else:
            add_record(
                data,
                focus,
                task.strip(),
                category,
                sleepiness,
                place,
                time_period,
                mood,
                memo.strip(),
                record_date,
            )

            st.rerun()


# =========================================================
# 今日の履歴
# =========================================================

st.divider()

st.subheader(
    "🌱 今日の集中ログ"
)

if not today_records:
    st.info(
        "今日はまだ記録がありません。"
    )

else:
    today_sorted = sorted(
        today_records,
        key=lambda record: record.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    for record in today_sorted:
        with st.container(
            border=True,
        ):
            focus_value = int(
                record.get(
                    "focus",
                    0,
                )
            )

            st.markdown(
                f"### 🧠 {focus_value}% "
                f"｜ {record.get('task', '')}"
            )

            st.progress(
                focus_value / 100
            )

            st.caption(
                f"{focus_level_text(focus_value)}"
                f" ｜ "
                f"{record.get('category', '')}"
            )

            col1, col2 = st.columns(
                2
            )

            with col1:
                st.write(
                    f"😴 {record.get('sleepiness', '')}"
                )

                st.write(
                    f"📍 {record.get('place', '')}"
                )

            with col2:
                st.write(
                    f"🕒 {record.get('time_period', '')}"
                )

                st.write(
                    f"🙂 {record.get('mood', '')}"
                )

            if record.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 {record.get('memo', '')}"
                )

            st.caption(
                "記録："
                + format_datetime(
                    record.get(
                        "created_at",
                        "",
                    )
                )
            )


# =========================================================
# 集中しやすい条件
# =========================================================

if len(records) >= 3:
    st.divider()

    st.subheader(
        "🏆 集中しやすい条件"
    )

    period_analysis = (
        grouped_average(
            records,
            "time_period",
        )
    )

    place_analysis = (
        grouped_average(
            records,
            "place",
        )
    )

    category_analysis = (
        grouped_average(
            records,
            "category",
        )
    )

    best_col1, best_col2, best_col3 = st.columns(
        3
    )

    if not period_analysis.empty:
        best_period = (
            period_analysis.iloc[0]
        )

        with best_col1:
            st.markdown(
                f"""
                <div class="best-condition">

                    <div class="best-title">
                        🕒 集中しやすい時間帯
                    </div>

                    <div class="best-value">
                        {best_period['条件']}
                    </div>

                    <div>
                        平均 {best_period['平均集中度']}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    if not place_analysis.empty:
        best_place = (
            place_analysis.iloc[0]
        )

        with best_col2:
            st.markdown(
                f"""
                <div class="best-condition">

                    <div class="best-title">
                        📍 集中しやすい場所
                    </div>

                    <div class="best-value">
                        {best_place['条件']}
                    </div>

                    <div>
                        平均 {best_place['平均集中度']}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    if not category_analysis.empty:
        best_category = (
            category_analysis.iloc[0]
        )

        with best_col3:
            st.markdown(
                f"""
                <div class="best-condition">

                    <div class="best-title">
                        📚 集中しやすい作業
                    </div>

                    <div class="best-value">
                        {best_category['条件']}
                    </div>

                    <div>
                        平均 {best_category['平均集中度']}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption(
        "※ 記録回数が少ないうちは参考値として見てね。"
    )


# =========================================================
# 時間帯別分析
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🕒 時間帯別の集中度"
    )

    period_df = grouped_average(
        records,
        "time_period",
    )

    if not period_df.empty:
        st.dataframe(
            period_df,
            use_container_width=True,
            hide_index=True,
        )

        period_chart = (
            period_df[
                [
                    "条件",
                    "平均集中度",
                ]
            ]
            .set_index(
                "条件"
            )
        )

        st.bar_chart(
            period_chart
        )


# =========================================================
# 場所別分析
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📍 場所別の集中度"
    )

    place_df = grouped_average(
        records,
        "place",
    )

    if not place_df.empty:
        st.dataframe(
            place_df,
            use_container_width=True,
            hide_index=True,
        )

        place_chart = (
            place_df[
                [
                    "条件",
                    "平均集中度",
                ]
            ]
            .set_index(
                "条件"
            )
        )

        st.bar_chart(
            place_chart
        )


# =========================================================
# カテゴリー別分析
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📚 作業カテゴリー別"
    )

    category_df = grouped_average(
        records,
        "category",
    )

    if not category_df.empty:
        st.dataframe(
            category_df,
            use_container_width=True,
            hide_index=True,
        )

        category_chart = (
            category_df[
                [
                    "条件",
                    "平均集中度",
                ]
            ]
            .set_index(
                "条件"
            )
        )

        st.bar_chart(
            category_chart
        )


# =========================================================
# 日別推移
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📈 集中度の推移"
    )

    trend_rows = [
        {
            "日付": record.get(
                "record_date",
                "",
            ),
            "集中度": int(
                record.get(
                    "focus",
                    0,
                )
            ),
        }
        for record in records
    ]

    trend_df = pd.DataFrame(
        trend_rows
    )

    daily_df = (
        trend_df.groupby(
            "日付",
            as_index=False,
        )[
            "集中度"
        ]
        .mean()
    )

    daily_df[
        "集中度"
    ] = daily_df[
        "集中度"
    ].round(1)

    daily_df = daily_df.sort_values(
        "日付"
    )

    st.line_chart(
        daily_df.set_index(
            "日付"
        )
    )


# =========================================================
# 過去ログ
# =========================================================

st.divider()

st.subheader(
    "📚 過去の集中ログ"
)

search_text = st.text_input(
    "🔎 作業内容・メモを検索",
    placeholder=(
        "例：Python、イラスト..."
    ),
)

filter_col1, filter_col2 = st.columns(
    2
)

with filter_col1:
    category_filter = st.selectbox(
        "カテゴリーで絞る",
        [
            "すべて",
            *CATEGORIES,
        ],
        key="history_category",
    )

with filter_col2:
    period_filter = st.selectbox(
        "時間帯で絞る",
        [
            "すべて",
            *TIME_PERIODS,
        ],
        key="history_period",
    )


filtered_records = records.copy()

if search_text.strip():
    keyword = (
        search_text.strip().lower()
    )

    filtered_records = [
        record
        for record in filtered_records
        if (
            keyword
            in record.get(
                "task",
                "",
            ).lower()
            or keyword
            in record.get(
                "memo",
                "",
            ).lower()
        )
    ]

if category_filter != "すべて":
    filtered_records = [
        record
        for record in filtered_records
        if record.get(
            "category"
        )
        == category_filter
    ]

if period_filter != "すべて":
    filtered_records = [
        record
        for record in filtered_records
        if record.get(
            "time_period"
        )
        == period_filter
    ]

filtered_records = sorted(
    filtered_records,
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


if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    history_rows = []

    for record in filtered_records:
        history_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "集中度": int(
                    record.get(
                        "focus",
                        0,
                    )
                ),
                "作業": record.get(
                    "task",
                    "",
                ),
                "カテゴリー": record.get(
                    "category",
                    "",
                ),
                "時間帯": record.get(
                    "time_period",
                    "",
                ),
                "場所": record.get(
                    "place",
                    "",
                ),
                "眠気": record.get(
                    "sleepiness",
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
        column_config={
            "集中度": st.column_config.ProgressColumn(
                "集中度",
                min_value=0,
                max_value=100,
                format="%d%%",
            )
        },
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
                f"### 🧠 {record.get('focus', 0)}% "
                f"｜ {record.get('task', '')}"
            )

            st.caption(
                format_date(
                    record.get(
                        "record_date",
                        "",
                    )
                )
            )

            with st.expander(
                "✏️ 編集"
            ):
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

                edit_task = st.text_input(
                    "作業内容",
                    value=record.get(
                        "task",
                        "",
                    ),
                    key=(
                        "edit_task_"
                        + record_id
                    ),
                )

                current_category = record.get(
                    "category",
                    "✨ その他",
                )

                edit_category = st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=(
                        CATEGORIES.index(
                            current_category
                        )
                        if current_category
                        in CATEGORIES
                        else len(
                            CATEGORIES
                        ) - 1
                    ),
                    key=(
                        "edit_category_"
                        + record_id
                    ),
                )

                current_sleepiness = (
                    record.get(
                        "sleepiness",
                        "🙂 少し眠い",
                    )
                )

                edit_sleepiness = st.selectbox(
                    "眠気",
                    SLEEPINESS,
                    index=(
                        SLEEPINESS.index(
                            current_sleepiness
                        )
                        if current_sleepiness
                        in SLEEPINESS
                        else 1
                    ),
                    key=(
                        "edit_sleepiness_"
                        + record_id
                    ),
                )

                current_place = record.get(
                    "place",
                    "🏠 自宅",
                )

                edit_place = st.selectbox(
                    "場所",
                    PLACES,
                    index=(
                        PLACES.index(
                            current_place
                        )
                        if current_place
                        in PLACES
                        else 0
                    ),
                    key=(
                        "edit_place_"
                        + record_id
                    ),
                )

                current_period = record.get(
                    "time_period",
                    "🌅 朝",
                )

                edit_period = st.selectbox(
                    "時間帯",
                    TIME_PERIODS,
                    index=(
                        TIME_PERIODS.index(
                            current_period
                        )
                        if current_period
                        in TIME_PERIODS
                        else 0
                    ),
                    key=(
                        "edit_period_"
                        + record_id
                    ),
                )

                current_mood = record.get(
                    "mood",
                    "😐 普通",
                )

                edit_mood = st.selectbox(
                    "気分",
                    MOODS,
                    index=(
                        MOODS.index(
                            current_mood
                        )
                        if current_mood
                        in MOODS
                        else 2
                    ),
                    key=(
                        "edit_mood_"
                        + record_id
                    ),
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

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_task.strip():
                        st.error(
                            "作業内容を入力してください。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_focus,
                            edit_task.strip(),
                            edit_category,
                            edit_sleepiness,
                            edit_place,
                            edit_period,
                            edit_mood,
                            edit_memo.strip(),
                            edit_date,
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
            "focus_tracker_"
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
    "集中できる条件は、人それぞれ。自分のパターンを見つけよう。🧠✨"
)
