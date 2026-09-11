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
    page_title="今のエネルギー何％？",
    page_icon="⚡",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "energy_data.json",
)

MOODS = [
    "😄 とても良い",
    "🙂 良い",
    "😌 穏やか",
    "😐 普通",
    "😕 モヤモヤ",
    "😢 落ち込み",
    "😣 しんどい",
]

TIME_PERIODS = [
    "🌅 朝",
    "☀️ 昼",
    "🌆 夕方",
    "🌙 夜",
    "🌌 深夜",
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
                "physical",
                50,
            )

            record.setdefault(
                "mental",
                50,
            )

            record.setdefault(
                "sleepiness",
                50,
            )

            record.setdefault(
                "stress",
                50,
            )

            record.setdefault(
                "energy",
                50,
            )

            record.setdefault(
                "mood",
                "😐 普通",
            )

            record.setdefault(
                "time_period",
                "🌅 朝",
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


def calculate_energy(
    physical,
    mental,
    sleepiness,
    stress,
):
    energy = (
        physical * 0.35
        + mental * 0.35
        + (100 - sleepiness) * 0.15
        + (100 - stress) * 0.15
    )

    return round(
        energy
    )


def energy_status(
    energy,
):
    if energy >= 80:
        return {
            "title": "🔥 攻めてもOK",
            "message": (
                "今日はエネルギー十分。"
                "大事なことや少し重めの作業にも向いています。"
            ),
            "actions": [
                "集中が必要な作業を進める",
                "少し難しい勉強に挑戦する",
                "勢いがあるうちに重要タスクを終わらせる",
            ],
        }

    if energy >= 60:
        return {
            "title": "🙂 普通に進めよう",
            "message": (
                "まずまず動ける状態。"
                "無理しすぎず、予定どおり進めてみよう。"
            ),
            "actions": [
                "今日の優先タスクを進める",
                "30〜60分の集中時間をつくる",
                "疲れを感じたら小休憩する",
            ],
        }

    if energy >= 40:
        return {
            "title": "🌿 軽めに進もう",
            "message": (
                "少しエネルギー低め。"
                "小さく進めることを優先しよう。"
            ),
            "actions": [
                "10分だけ勉強する",
                "軽い片付けをする",
                "重い予定は後回しにする",
            ],
        }

    if energy >= 20:
        return {
            "title": "🛋️ かなり省エネで",
            "message": (
                "今日は無理をすると消耗しやすい状態。"
                "最低限だけで十分です。"
            ),
            "actions": [
                "必要最低限のことだけやる",
                "短い作業と休憩を繰り返す",
                "早めに休める準備をする",
            ],
        }

    return {
        "title": "💤 回復優先",
        "message": (
            "かなりエネルギーが低い状態。"
            "今日は回復を一番に考えよう。"
        ),
        "actions": [
            "できるだけ休む",
            "予定を減らせるなら減らす",
            "睡眠や食事など基本的な回復を優先する",
        ],
    }


def average_energy(records):
    if not records:
        return 0

    return round(
        sum(
            int(
                record.get(
                    "energy",
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
                "エネルギー": int(
                    record.get(
                        "energy",
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
            平均エネルギー=(
                "エネルギー",
                "mean",
            ),
            記録回数=(
                "エネルギー",
                "count",
            ),
        )
    )

    result[
        "平均エネルギー"
    ] = result[
        "平均エネルギー"
    ].round(1)

    return result.sort_values(
        "平均エネルギー",
        ascending=False,
    )


# =========================================================
# CRUD
# =========================================================

def add_record(
    data,
    physical,
    mental,
    sleepiness,
    stress,
    mood,
    time_period,
    memo,
    record_date,
):
    energy = calculate_energy(
        physical,
        mental,
        sleepiness,
        stress,
    )

    data["records"].append(
        {
            "id": create_id(),
            "physical": int(
                physical
            ),
            "mental": int(
                mental
            ),
            "sleepiness": int(
                sleepiness
            ),
            "stress": int(
                stress
            ),
            "energy": int(
                energy
            ),
            "mood": mood,
            "time_period": time_period,
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
    physical,
    mental,
    sleepiness,
    stress,
    mood,
    time_period,
    memo,
    record_date,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    energy = calculate_energy(
        physical,
        mental,
        sleepiness,
        stress,
    )

    record["physical"] = int(
        physical
    )

    record["mental"] = int(
        mental
    )

    record["sleepiness"] = int(
        sleepiness
    )

    record["stress"] = int(
        stress
    )

    record["energy"] = int(
        energy
    )

    record["mood"] = mood

    record["time_period"] = (
        time_period
    )

    record["memo"] = memo

    record["record_date"] = str(
        record_date
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
        if record.get("id")
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
        background: rgba(255, 190, 70, 0.08);
        border: 1px solid rgba(255, 190, 70, 0.18);
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
                rgba(255, 185, 60, 0.18),
                rgba(100, 210, 160, 0.10)
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

    .energy-card {
        padding: 28px;
        border-radius: 24px;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 70, 0.14),
                rgba(110, 130, 255, 0.08)
            );
    }

    .energy-label {
        font-size: 0.95rem;
        font-weight: 700;
        opacity: 0.7;
    }

    .energy-number {
        font-size: 3.2rem;
        font-weight: 900;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    .status-card {
        padding: 24px;
        border-radius: 22px;
        margin-top: 12px;
        margin-bottom: 16px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 210, 160, 0.12),
                rgba(110, 130, 255, 0.08)
            );
    }

    .status-title {
        font-size: 1.5rem;
        font-weight: 900;
        margin-bottom: 8px;
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

today_average = average_energy(
    today_records
)

month_average = average_energy(
    month_records
)

today_highest = max(
    [
        int(
            record.get(
                "energy",
                0,
            )
        )
        for record in today_records
    ],
    default=0,
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>⚡ 今のエネルギー何％？</h1>

        <p>
            今の自分に、無理のないペースを選ばせる。
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
    "⚡ 今日の平均",
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
# エネルギー入力
# =========================================================

st.divider()

st.subheader(
    "⚡ 今の状態をチェック"
)

with st.form(
    "energy_form"
):
    physical = st.slider(
        "💪 体力",
        min_value=0,
        max_value=100,
        value=60,
        step=5,
        help=(
            "身体的にどれくらい動けそうか"
        ),
    )

    mental = st.slider(
        "🧠 気力",
        min_value=0,
        max_value=100,
        value=60,
        step=5,
        help=(
            "何かをやろうと思える気力"
        ),
    )

    sleepiness = st.slider(
        "🥱 眠気",
        min_value=0,
        max_value=100,
        value=30,
        step=5,
        help=(
            "100に近いほど強い眠気"
        ),
    )

    stress = st.slider(
        "😣 ストレス",
        min_value=0,
        max_value=100,
        value=30,
        step=5,
        help=(
            "100に近いほど強いストレス"
        ),
    )

    preview_energy = calculate_energy(
        physical,
        mental,
        sleepiness,
        stress,
    )

    preview_status = energy_status(
        preview_energy
    )

    st.markdown(
        f"""
        <div class="energy-card">

            <div class="energy-label">
                総合エネルギー
            </div>

            <div class="energy-number">
                {preview_energy}%
            </div>

            <div>
                {preview_status["title"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(
        2
    )

    with col1:
        mood = st.selectbox(
            "🙂 今の気分",
            MOODS,
        )

    with col2:
        current_period = (
            detect_time_period()
        )

        time_period = st.selectbox(
            "🕒 時間帯",
            TIME_PERIODS,
            index=TIME_PERIODS.index(
                current_period
            ),
        )

    record_date = st.date_input(
        "📅 記録日",
        value=date.today(),
    )

    memo = st.text_area(
        "💬 メモ",
        placeholder=(
            "例：今日は少し疲れている。"
            "やるなら軽めにしたい。"
        ),
        height=100,
    )

    submitted = st.form_submit_button(
        "⚡ この状態を記録",
        use_container_width=True,
        type="primary",
    )

    if submitted:
        add_record(
            data,
            physical,
            mental,
            sleepiness,
            stress,
            mood,
            time_period,
            memo.strip(),
            record_date,
        )

        st.rerun()


# =========================================================
# 最新の状態
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🌿 今のペース提案"
    )

    latest_record = sorted(
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
    )[0]

    latest_energy = int(
        latest_record.get(
            "energy",
            0,
        )
    )

    latest_status = energy_status(
        latest_energy
    )

    st.markdown(
        f"""
        <div class="status-card">

            <div class="status-title">
                {latest_status["title"]}
            </div>

            <div>
                エネルギー：
                <strong>{latest_energy}%</strong>
            </div>

            <div style="margin-top: 10px;">
                {latest_status["message"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "**おすすめの動き方**"
    )

    for action in latest_status[
        "actions"
    ]:
        st.write(
            f"・{action}"
        )


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "🌱 今日のエネルギーログ"
)

if not today_records:
    st.info(
        "今日はまだ記録がありません。"
    )

else:
    sorted_today = sorted(
        today_records,
        key=lambda record: record.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    for record in sorted_today:
        energy = int(
            record.get(
                "energy",
                0,
            )
        )

        status = energy_status(
            energy
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### ⚡ {energy}% ｜ "
                f"{status['title']}"
            )

            st.progress(
                energy / 100
            )

            col1, col2 = st.columns(
                2
            )

            with col1:
                st.write(
                    f"💪 体力："
                    f"{record.get('physical', 0)}%"
                )

                st.write(
                    f"🧠 気力："
                    f"{record.get('mental', 0)}%"
                )

                st.write(
                    f"🙂 気分："
                    f"{record.get('mood', '')}"
                )

            with col2:
                st.write(
                    f"🥱 眠気："
                    f"{record.get('sleepiness', 0)}%"
                )

                st.write(
                    f"😣 ストレス："
                    f"{record.get('stress', 0)}%"
                )

                st.write(
                    f"🕒 "
                    f"{record.get('time_period', '')}"
                )

            if record.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 {record.get('memo', '')}"
                )

            st.caption(
                format_datetime(
                    record.get(
                        "created_at",
                        "",
                    )
                )
            )


# =========================================================
# 時間帯別分析
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🕒 時間帯別エネルギー"
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

        chart_df = (
            period_df[
                [
                    "条件",
                    "平均エネルギー",
                ]
            ]
            .set_index(
                "条件"
            )
        )

        st.bar_chart(
            chart_df
        )

        best = period_df.iloc[0]

        st.success(
            f"🏆 今のところ最もエネルギーが高いのは"
            f「{best['条件']}」で、"
            f"平均 {best['平均エネルギー']}% です。"
        )


# =========================================================
# 日別推移
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📈 エネルギーの推移"
    )

    rows = []

    for record in records:
        rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
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
        rows
    )

    daily_df = (
        trend_df.groupby(
            "日付",
            as_index=False,
        )[
            "エネルギー"
        ]
        .mean()
    )

    daily_df[
        "エネルギー"
    ] = daily_df[
        "エネルギー"
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
# 各項目の平均
# =========================================================

if records:
    st.divider()

    st.subheader(
        "🔍 今月の状態"
    )

    source = (
        month_records
        if month_records
        else records
    )

    avg_physical = round(
        sum(
            int(
                record.get(
                    "physical",
                    0,
                )
            )
            for record in source
        )
        / len(source),
        1,
    )

    avg_mental = round(
        sum(
            int(
                record.get(
                    "mental",
                    0,
                )
            )
            for record in source
        )
        / len(source),
        1,
    )

    avg_sleepiness = round(
        sum(
            int(
                record.get(
                    "sleepiness",
                    0,
                )
            )
            for record in source
        )
        / len(source),
        1,
    )

    avg_stress = round(
        sum(
            int(
                record.get(
                    "stress",
                    0,
                )
            )
            for record in source
        )
        / len(source),
        1,
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

    col1.metric(
        "💪 平均体力",
        f"{avg_physical}%",
    )

    col2.metric(
        "🧠 平均気力",
        f"{avg_mental}%",
    )

    col3.metric(
        "🥱 平均眠気",
        f"{avg_sleepiness}%",
    )

    col4.metric(
        "😣 平均ストレス",
        f"{avg_stress}%",
    )


# =========================================================
# 過去ログ
# =========================================================

st.divider()

st.subheader(
    "📚 過去のエネルギーログ"
)

search_text = st.text_input(
    "🔎 メモを検索",
    placeholder=(
        "例：疲れ、勉強、仕事..."
    ),
)

period_filter = st.selectbox(
    "時間帯で絞る",
    [
        "すべて",
        *TIME_PERIODS,
    ],
)

filtered_records = records.copy()

if search_text.strip():
    keyword = (
        search_text.strip().lower()
    )

    filtered_records = [
        record
        for record in filtered_records
        if keyword
        in record.get(
            "memo",
            "",
        ).lower()
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
                "エネルギー": int(
                    record.get(
                        "energy",
                        0,
                    )
                ),
                "体力": int(
                    record.get(
                        "physical",
                        0,
                    )
                ),
                "気力": int(
                    record.get(
                        "mental",
                        0,
                    )
                ),
                "眠気": int(
                    record.get(
                        "sleepiness",
                        0,
                    )
                ),
                "ストレス": int(
                    record.get(
                        "stress",
                        0,
                    )
                ),
                "時間帯": record.get(
                    "time_period",
                    "",
                ),
                "気分": record.get(
                    "mood",
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
            "エネルギー": (
                st.column_config.ProgressColumn(
                    "エネルギー",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                )
            ),
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
                f"### ⚡ "
                f"{record.get('energy', 0)}%"
            )

            st.caption(
                f"{format_date(record.get('record_date', ''))}"
                f" ｜ "
                f"{record.get('time_period', '')}"
            )

            with st.expander(
                "✏️ 編集"
            ):
                edit_physical = st.slider(
                    "体力",
                    0,
                    100,
                    int(
                        record.get(
                            "physical",
                            50,
                        )
                    ),
                    5,
                    key=(
                        "edit_physical_"
                        + record_id
                    ),
                )

                edit_mental = st.slider(
                    "気力",
                    0,
                    100,
                    int(
                        record.get(
                            "mental",
                            50,
                        )
                    ),
                    5,
                    key=(
                        "edit_mental_"
                        + record_id
                    ),
                )

                edit_sleepiness = st.slider(
                    "眠気",
                    0,
                    100,
                    int(
                        record.get(
                            "sleepiness",
                            50,
                        )
                    ),
                    5,
                    key=(
                        "edit_sleepiness_"
                        + record_id
                    ),
                )

                edit_stress = st.slider(
                    "ストレス",
                    0,
                    100,
                    int(
                        record.get(
                            "stress",
                            50,
                        )
                    ),
                    5,
                    key=(
                        "edit_stress_"
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
                        else 3
                    ),
                    key=(
                        "edit_mood_"
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

                edit_energy = (
                    calculate_energy(
                        edit_physical,
                        edit_mental,
                        edit_sleepiness,
                        edit_stress,
                    )
                )

                st.info(
                    f"変更後の総合エネルギー："
                    f"{edit_energy}%"
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
                        edit_physical,
                        edit_mental,
                        edit_sleepiness,
                        edit_stress,
                        edit_mood,
                        edit_period,
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
            "energy_meter_"
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
    "今の自分に、無理のないペースを選ばせる。⚡🌿"
)
