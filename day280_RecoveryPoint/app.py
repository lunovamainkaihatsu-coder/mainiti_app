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
    page_title="今日の回復ポイント",
    page_icon="🌿",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "recovery.json")

CATEGORIES = [
    "😴 睡眠・休息",
    "🚶 運動・散歩",
    "🚿 お風呂・ケア",
    "🍚 食事",
    "🎮 娯楽",
    "🎵 音楽",
    "👥 人との時間",
    "🌳 外出・自然",
    "🧘 リラックス",
    "📱 SNS・スマホ",
    "✨ その他",
]

CONDITIONS = [
    "😴 眠い",
    "🪫 疲れている",
    "😣 ストレス",
    "🧠 頭が疲れた",
    "😔 気分が落ちている",
    "💪 身体が疲れた",
]


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def today_text():
    return str(date.today())


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def format_datetime(value):
    dt = parse_datetime(value)

    if not dt:
        return "-"

    return dt.strftime("%Y/%m/%d %H:%M")


def recovery_point(record):
    return (
        int(record.get("after_energy", 0))
        - int(record.get("before_energy", 0))
    )


def efficiency(record):
    minutes = int(record.get("minutes", 0))

    if minutes <= 0:
        return None

    return round(
        recovery_point(record) / minutes * 10,
        1,
    )


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
    minutes = int(minutes)

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    remain = minutes % 60

    if remain:
        return f"{hours}時間{remain}分"

    return f"{hours}時間"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {"records": []}


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)

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
    os.makedirs(DATA_DIR, exist_ok=True)

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

        data.setdefault("records", [])

        # 過去データ補完
        for record in data["records"]:
            record.setdefault("id", create_id())
            record.setdefault("activity", "")
            record.setdefault("category", "✨ その他")
            record.setdefault("before_energy", 50)
            record.setdefault("after_energy", 50)
            record.setdefault("minutes", 10)
            record.setdefault("conditions", [])
            record.setdefault("memo", "")
            record.setdefault("favorite", False)
            record.setdefault("record_date", today_text())
            record.setdefault("created_at", now_text())
            record.setdefault(
                "updated_at",
                record.get("created_at", now_text()),
            )

        return data

    except (json.JSONDecodeError, OSError, ValueError):
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
    activity,
    category,
    before_energy,
    after_energy,
    minutes,
    conditions,
    memo,
):
    record = {
        "id": create_id(),
        "activity": activity,
        "category": category,
        "before_energy": int(before_energy),
        "after_energy": int(after_energy),
        "minutes": int(minutes),
        "conditions": conditions,
        "memo": memo,
        "favorite": False,
        "record_date": today_text(),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["records"].append(record)
    save_data(data)

    return record["id"]


def update_record(
    data,
    record_id,
    activity,
    category,
    before_energy,
    after_energy,
    minutes,
    conditions,
    memo,
):
    record = get_record(data, record_id)

    if not record:
        return

    record["activity"] = activity
    record["category"] = category
    record["before_energy"] = int(before_energy)
    record["after_energy"] = int(after_energy)
    record["minutes"] = int(minutes)
    record["conditions"] = conditions
    record["memo"] = memo
    record["updated_at"] = now_text()

    save_data(data)


def toggle_favorite(data, record_id):
    record = get_record(data, record_id)

    if not record:
        return

    record["favorite"] = not record.get("favorite", False)
    record["updated_at"] = now_text()

    save_data(data)


def delete_record(data, record_id):
    data["records"] = [
        record
        for record in data["records"]
        if record.get("id") != record_id
    ]

    save_data(data)


# =========================================================
# 集計
# =========================================================

def activity_stats(records):
    groups = {}

    for record in records:
        activity = record.get("activity", "").strip()

        if not activity:
            continue

        groups.setdefault(activity, []).append(record)

    rows = []

    for activity, items in groups.items():
        points = [
            recovery_point(item)
            for item in items
        ]

        efficiencies = [
            efficiency(item)
            for item in items
            if efficiency(item) is not None
        ]

        minutes = [
            int(item.get("minutes", 0))
            for item in items
        ]

        negative_count = len(
            [
                point
                for point in points
                if point < 0
            ]
        )

        rows.append(
            {
                "activity": activity,
                "count": len(items),
                "avg_point": average(points),
                "avg_efficiency": average(efficiencies),
                "avg_minutes": average(minutes),
                "best_point": max(points) if points else 0,
                "negative_count": negative_count,
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
        background: rgba(80, 180, 120, 0.07);
        border: 1px solid rgba(80, 180, 120, 0.16);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 180, 120, 0.20),
                rgba(120, 210, 180, 0.08)
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

today_records = [
    record
    for record in records
    if record.get("record_date") == today_text()
]

current_month = date.today().strftime("%Y-%m")

month_records = [
    record
    for record in records
    if (
        record.get("record_date", "")
        or ""
    ).startswith(current_month)
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🌿 今日の回復ポイント</h1>
        <p>
            何をすると、自分は本当に回復する？
            感覚ではなく、実際の変化を残してみよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日のダッシュボード
# =========================================================

today_points = sum(
    recovery_point(record)
    for record in today_records
)

today_minutes = sum(
    int(record.get("minutes", 0))
    for record in today_records
)

best_today = None

if today_records:
    best_today = max(
        today_records,
        key=recovery_point,
    )


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🌿 今日の記録",
    f"{len(today_records)}回",
)

col2.metric(
    "🔋 今日の回復",
    f"{today_points:+d}pt",
)

col3.metric(
    "⏱️ 回復時間",
    format_minutes(today_minutes),
)

col4.metric(
    "🏆 今日一番",
    (
        best_today.get("activity", "")
        if best_today
        else "-"
    ),
    (
        f"{recovery_point(best_today):+d}pt"
        if best_today
        else None
    ),
)


# =========================================================
# 回復記録
# =========================================================

st.divider()

st.subheader("🌿 回復を記録")

with st.form(
    "recovery_form",
    clear_on_submit=True,
):
    activity = st.text_input(
        "🌿 何をした？",
        placeholder="例：20分昼寝した",
    )

    category = st.selectbox(
        "🏷️ カテゴリー",
        CATEGORIES,
    )

    col1, col2 = st.columns(2)

    with col1:
        before_energy = st.slider(
            "🪫 やる前",
            0,
            100,
            30,
            help="回復行動をする前のエネルギー",
        )

    with col2:
        after_energy = st.slider(
            "🔋 やった後",
            0,
            100,
            60,
            help="回復行動をした後のエネルギー",
        )

    preview_point = (
        after_energy - before_energy
    )

    if preview_point > 0:
        st.success(
            f"✨ 回復予測：{preview_point:+d}pt"
        )

    elif preview_point < 0:
        st.warning(
            f"📉 変化：{preview_point:+d}pt"
        )

    else:
        st.info("変化：±0pt")

    minutes = st.number_input(
        "⏱️ かかった時間（分）",
        min_value=1,
        max_value=1440,
        value=20,
        step=5,
    )

    conditions = st.multiselect(
        "🧠 やる前はどんな状態だった？",
        CONDITIONS,
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "例：昼食後。かなり眠かった。"
        ),
    )

    submitted = st.form_submit_button(
        "🌿 回復を記録",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if not activity.strip():
            st.warning(
                "何をしたか入力してね。"
            )

        else:
            record_id = add_record(
                data=data,
                activity=activity.strip(),
                category=category,
                before_energy=before_energy,
                after_energy=after_energy,
                minutes=minutes,
                conditions=conditions,
                memo=memo.strip(),
            )

            st.session_state[
                "just_recorded"
            ] = record_id

            st.rerun()


# =========================================================
# 保存直後
# =========================================================

just_recorded = st.session_state.pop(
    "just_recorded",
    None,
)

if just_recorded:
    record = get_record(
        data,
        just_recorded,
    )

    if record:
        point = recovery_point(record)
        eff = efficiency(record)

        if point > 0:
            st.success(
                f"✨ {point:+d}pt 回復！ "
                f"{record.get('before_energy')}% → "
                f"{record.get('after_energy')}%"
            )

        elif point < 0:
            st.warning(
                f"📉 {point:+d}pt。"
                "回復しなかったことも大事なデータです。"
            )

        else:
            st.info(
                "🔋 今回は±0pt。"
                "これも立派な回復データです。"
            )

        if eff is not None:
            st.caption(
                f"⚡ 10分あたり {eff:+.1f}pt"
            )


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader("🔋 今日の回復")

if not today_records:
    st.info(
        "今日はまだ回復記録がありません。"
    )

else:
    for record in sorted(
        today_records,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    ):
        record_id = record.get("id", "")
        point = recovery_point(record)
        eff = efficiency(record)

        with st.container(border=True):
            col1, col2 = st.columns(
                [7, 1]
            )

            with col1:
                st.subheader(
                    record.get(
                        "activity",
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
                        "today_fav_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )
                    st.rerun()

            st.caption(
                record.get(
                    "category",
                    "",
                )
                + " ｜ "
                + format_datetime(
                    record.get(
                        "created_at"
                    )
                )
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Before",
                f"{record.get('before_energy', 0)}%",
            )

            col2.metric(
                "After",
                f"{record.get('after_energy', 0)}%",
            )

            col3.metric(
                "回復",
                f"{point:+d}pt",
            )

            st.write(
                f"⏱️ **{record.get('minutes', 0)}分**"
            )

            if eff is not None:
                st.write(
                    f"⚡ **10分効率：{eff:+.1f}pt**"
                )

            if record.get("conditions"):
                st.write("🧠 **開始時の状態**")
                st.write(
                    "　".join(
                        record.get(
                            "conditions",
                            [],
                        )
                    )
                )

            if record.get("memo"):
                st.write("📝 **メモ**")
                st.write(
                    record.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 回復ランキング
# =========================================================

st.divider()

st.subheader(
    "🏆 自分の回復ランキング"
)

stats = activity_stats(records)

if not stats:
    st.info(
        "記録が増えると、"
        "自分専用の回復ランキングができます。"
    )

else:
    ranked = sorted(
        stats,
        key=lambda item: item[
            "avg_point"
        ],
        reverse=True,
    )

    for index, item in enumerate(
        ranked[:10],
        start=1,
    ):
        with st.container(border=True):
            st.write(
                f"**{index}位　"
                f"{item['activity']}**"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "平均回復",
                f"{item['avg_point']:+.1f}pt",
            )

            col2.metric(
                "記録回数",
                f"{item['count']}回",
            )

            col3.metric(
                "平均時間",
                format_minutes(
                    round(
                        item[
                            "avg_minutes"
                        ]
                    )
                ),
            )


# =========================================================
# 回復効率ランキング
# =========================================================

st.divider()

st.subheader(
    "⚡ 回復効率ランキング"
)

efficiency_stats = [
    item
    for item in stats
    if item["avg_efficiency"]
    is not None
]

if not efficiency_stats:
    st.caption(
        "データが増えると表示されます。"
    )

else:
    efficiency_stats.sort(
        key=lambda item: item[
            "avg_efficiency"
        ],
        reverse=True,
    )

    efficiency_df = pd.DataFrame(
        [
            {
                "行動": item["activity"],
                "10分あたり回復pt": (
                    item[
                        "avg_efficiency"
                    ]
                ),
                "平均回復pt": (
                    item["avg_point"]
                ),
                "回数": item["count"],
            }
            for item
            in efficiency_stats
        ]
    )

    st.dataframe(
        efficiency_df,
        hide_index=True,
        use_container_width=True,
    )

    chart_df = (
        efficiency_df[
            [
                "行動",
                "10分あたり回復pt",
            ]
        ]
        .set_index("行動")
    )

    st.bar_chart(chart_df)


# =========================================================
# 今の状態なら何が効く？
# =========================================================

st.divider()

st.subheader(
    "🔍 今の自分なら何する？"
)

selected_conditions = st.multiselect(
    "今の状態",
    CONDITIONS,
    key="recommend_conditions",
)

available_minutes = st.number_input(
    "使える時間（分）",
    min_value=1,
    max_value=1440,
    value=30,
    step=5,
)

if st.button(
    "🌿 過去の自分から探す",
    use_container_width=True,
):
    candidate_records = []

    for record in records:
        record_conditions = set(
            record.get(
                "conditions",
                [],
            )
        )

        condition_match = (
            not selected_conditions
            or bool(
                record_conditions.intersection(
                    selected_conditions
                )
            )
        )

        time_match = (
            int(
                record.get(
                    "minutes",
                    0,
                )
            )
            <= available_minutes
        )

        if condition_match and time_match:
            candidate_records.append(
                record
            )

    candidate_stats = activity_stats(
        candidate_records
    )

    if not candidate_stats:
        st.info(
            "まだ条件に合う過去データがありません。"
        )

    else:
        candidate_stats.sort(
            key=lambda item: (
                item["avg_point"],
                item["avg_efficiency"],
            ),
            reverse=True,
        )

        st.success(
            "🌿 過去の記録では、"
            "このあたりが効いています。"
        )

        for index, item in enumerate(
            candidate_stats[:3],
            start=1,
        ):
            with st.container(
                border=True
            ):
                st.write(
                    f"**{index}位　"
                    f"{item['activity']}**"
                )

                st.write(
                    f"平均回復："
                    f"{item['avg_point']:+.1f}pt"
                )

                st.write(
                    f"平均時間："
                    f"{format_minutes(round(item['avg_minutes']))}"
                )

                st.write(
                    f"記録：{item['count']}回"
                )


# =========================================================
# 状態別の回復
# =========================================================

st.divider()

st.subheader(
    "🧠 状態別に何が効いた？"
)

condition_choice = st.selectbox(
    "状態を選択",
    CONDITIONS,
)

condition_records = [
    record
    for record in records
    if condition_choice
    in record.get(
        "conditions",
        [],
    )
]

condition_stats = activity_stats(
    condition_records
)

if not condition_stats:
    st.info(
        "この状態の記録はまだありません。"
    )

else:
    condition_stats.sort(
        key=lambda item: item[
            "avg_point"
        ],
        reverse=True,
    )

    for index, item in enumerate(
        condition_stats[:5],
        start=1,
    ):
        st.write(
            f"**{index}位 "
            f"{item['activity']}** "
            f"— 平均 "
            f"{item['avg_point']:+.1f}pt "
            f"({item['count']}回)"
        )


# =========================================================
# 回復しなかった行動
# =========================================================

negative_stats = [
    item
    for item in stats
    if item[
        "negative_count"
    ] > 0
]

if negative_stats:
    st.divider()

    st.subheader(
        "🤔 回復しなかったこともある"
    )

    negative_stats.sort(
        key=lambda item: (
            item["negative_count"]
            / item["count"]
        ),
        reverse=True,
    )

    for item in negative_stats[:5]:
        rate = round(
            item["negative_count"]
            / item["count"]
            * 100
        )

        with st.container(border=True):
            st.write(
                "**"
                + item["activity"]
                + "**"
            )

            st.write(
                f"{item['count']}回中 "
                f"{item['negative_count']}回で"
                "エネルギーが低下"
            )

            st.caption(
                f"低下率 {rate}% ｜ "
                f"全体平均 "
                f"{item['avg_point']:+.1f}pt"
            )


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の回復"
)

if not month_records:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    month_points = [
        recovery_point(record)
        for record in month_records
    ]

    month_minutes = sum(
        int(
            record.get(
                "minutes",
                0,
            )
        )
        for record in month_records
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "🌿 回復行動",
        f"{len(month_records)}回",
    )

    col2.metric(
        "🔋 総回復",
        f"{sum(month_points):+d}pt",
    )

    col3.metric(
        "📈 平均回復",
        f"{average(month_points):+.1f}pt",
    )

    col4.metric(
        "⏱️ 回復時間",
        format_minutes(
            month_minutes
        ),
    )

    # 日別
    daily = {}

    for record in month_records:
        record_date = record.get(
            "record_date",
            "",
        )

        daily.setdefault(
            record_date,
            0,
        )

        daily[
            record_date
        ] += recovery_point(record)

    daily_df = pd.DataFrame(
        [
            {
                "日付": day,
                "回復pt": point,
            }
            for day, point
            in sorted(
                daily.items()
            )
        ]
    )

    if not daily_df.empty:
        st.markdown(
            "### 📅 日別回復ポイント"
        )

        st.line_chart(
            daily_df.set_index(
                "日付"
            )
        )

    # カテゴリー
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
                "回数": len(
                    category_records
                ),
                "平均回復": average(
                    [
                        recovery_point(
                            record
                        )
                        for record
                        in category_records
                    ]
                ),
            }
        )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        )

        st.markdown(
            "### 🏷️ カテゴリー別"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )[["平均回復"]]
        )


# =========================================================
# 回復図鑑
# =========================================================

st.divider()

st.subheader("📚 回復図鑑")

if not stats:
    st.caption(
        "記録すると回復行動が図鑑になります。"
    )

else:
    encyclopedia_search = st.text_input(
        "🔎 行動を検索",
        placeholder="昼寝、散歩、お風呂……",
    )

    encyclopedia_stats = [
        item
        for item in stats
        if (
            not encyclopedia_search.strip()
            or encyclopedia_search
            .strip()
            .lower()
            in item[
                "activity"
            ].lower()
        )
    ]

    for item in sorted(
        encyclopedia_stats,
        key=lambda row: row[
            "count"
        ],
        reverse=True,
    ):
        related_records = [
            record
            for record in records
            if record.get(
                "activity",
                "",
            )
            == item["activity"]
        ]

        with st.expander(
            f"🌿 {item['activity']} "
            f"｜ {item['count']}回"
        ):
            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "平均回復",
                f"{item['avg_point']:+.1f}pt",
            )

            col2.metric(
                "平均時間",
                format_minutes(
                    round(
                        item[
                            "avg_minutes"
                        ]
                    )
                ),
            )

            col3.metric(
                "最高記録",
                f"{item['best_point']:+d}pt",
            )

            if item[
                "avg_efficiency"
            ] is not None:
                st.write(
                    "⚡ **10分あたり：** "
                    f"{item['avg_efficiency']:+.1f}pt"
                )

            condition_counts = {}

            for record in related_records:
                for condition in record.get(
                    "conditions",
                    [],
                ):
                    condition_counts[
                        condition
                    ] = (
                        condition_counts.get(
                            condition,
                            0,
                        )
                        + 1
                    )

            if condition_counts:
                top_conditions = sorted(
                    condition_counts.items(),
                    key=lambda pair: pair[1],
                    reverse=True,
                )[:3]

                st.write(
                    "🧠 **よく記録された状態**"
                )

                st.write(
                    "　".join(
                        condition
                        for condition, _
                        in top_conditions
                    )
                )

            st.write("**最近の記録**")

            recent = sorted(
                related_records,
                key=lambda record: record.get(
                    "created_at",
                    "",
                ),
                reverse=True,
            )[:5]

            for record in recent:
                st.write(
                    f"{record.get('record_date')}　"
                    f"{recovery_point(record):+d}pt　"
                    f"{record.get('minutes')}分"
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

    st.subheader("⭐ お気に入り")

    for record in sorted(
        favorites,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.container(border=True):
            st.write(
                "⭐ **"
                + record.get(
                    "activity",
                    "",
                )
                + "**"
            )

            st.write(
                f"🔋 "
                f"{record.get('before_energy')}%"
                " → "
                f"{record.get('after_energy')}%"
                f"　"
                f"{recovery_point(record):+d}pt"
            )

            if record.get("memo"):
                st.write(
                    record.get(
                        "memo",
                        "",
                    )
                )

            if st.button(
                "⭐ お気に入り解除",
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

st.subheader("📜 回復履歴")

search_text = st.text_input(
    "🔎 履歴検索",
    placeholder=(
        "昼寝、散歩、疲れている……"
    ),
    key="history_search",
)

category_filter = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="history_category",
)

filtered_records = []

for record in records:
    if (
        category_filter != "すべて"
        and record.get(
            "category"
        )
        != category_filter
    ):
        continue

    searchable = " ".join(
        [
            record.get(
                "activity",
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
            " ".join(
                record.get(
                    "conditions",
                    [],
                )
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

    filtered_records.append(record)


history_rows = []

for record in sorted(
    filtered_records,
    key=lambda item: item.get(
        "created_at",
        "",
    ),
    reverse=True,
):
    history_rows.append(
        {
            "日時": format_datetime(
                record.get(
                    "created_at"
                )
            ),
            "行動": record.get(
                "activity",
                "",
            ),
            "カテゴリー": record.get(
                "category",
                "",
            ),
            "Before": (
                f"{record.get('before_energy')}%"
            ),
            "After": (
                f"{record.get('after_energy')}%"
            ),
            "回復": (
                f"{recovery_point(record):+d}pt"
            ),
            "時間": (
                f"{record.get('minutes')}分"
            ),
            "効率/10分": (
                f"{efficiency(record):+.1f}"
                if efficiency(record)
                is not None
                else "-"
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


if history_rows:
    st.dataframe(
        pd.DataFrame(
            history_rows
        ),
        hide_index=True,
        use_container_width=True,
    )

else:
    st.info(
        "条件に合う記録はありません。"
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander("🛠️ 編集・管理"):
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
        key=lambda item: item.get(
            "created_at",
            "",
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
                "activity",
                "",
            )
        ):
            edit_activity = st.text_input(
                "何をした？",
                value=record.get(
                    "activity",
                    "",
                ),
                key=(
                    "edit_activity_"
                    + record_id
                ),
            )

            old_category = record.get(
                "category",
                "✨ その他",
            )

            category_index = (
                CATEGORIES.index(
                    old_category
                )
                if old_category
                in CATEGORIES
                else len(CATEGORIES) - 1
            )

            edit_category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=category_index,
                key=(
                    "edit_category_"
                    + record_id
                ),
            )

            edit_before = st.slider(
                "Before",
                0,
                100,
                int(
                    record.get(
                        "before_energy",
                        50,
                    )
                ),
                key=(
                    "edit_before_"
                    + record_id
                ),
            )

            edit_after = st.slider(
                "After",
                0,
                100,
                int(
                    record.get(
                        "after_energy",
                        50,
                    )
                ),
                key=(
                    "edit_after_"
                    + record_id
                ),
            )

            edit_minutes = st.number_input(
                "時間（分）",
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

            edit_conditions = st.multiselect(
                "開始時の状態",
                CONDITIONS,
                default=[
                    condition
                    for condition
                    in record.get(
                        "conditions",
                        [],
                    )
                    if condition
                    in CONDITIONS
                ],
                key=(
                    "edit_conditions_"
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

            st.write(
                "**回復ポイント：** "
                f"{edit_after - edit_before:+d}pt"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "update_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_activity.strip():
                        st.warning(
                            "行動名を入力してね。"
                        )

                    else:
                        update_record(
                            data=data,
                            record_id=record_id,
                            activity=(
                                edit_activity.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            before_energy=(
                                edit_before
                            ),
                            after_energy=(
                                edit_after
                            ),
                            minutes=(
                                edit_minutes
                            ),
                            conditions=(
                                edit_conditions
                            ),
                            memo=(
                                edit_memo.strip()
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
                        "manage_fav_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )
                    st.rerun()

            confirm_delete = st.checkbox(
                "削除を確認",
                key=(
                    "confirm_delete_"
                    + record_id
                ),
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

with st.expander("💾 データ管理"):
    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            "recovery_point_"
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
    "🌿 休んだ時間ではなく、"
    "自分が本当に回復した方法を知っていこう。"
)
