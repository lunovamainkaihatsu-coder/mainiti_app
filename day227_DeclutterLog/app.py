import json
import os
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="捨て活ログ",
    page_icon="🗑️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "declutter_data.json",
)

CATEGORIES = [
    "服",
    "本",
    "書類",
    "家電",
    "PC・ガジェット",
    "キッチン用品",
    "日用品",
    "子ども用品",
    "おもちゃ",
    "趣味",
    "ゲーム",
    "車用品",
    "家具",
    "思い出の品",
    "その他",
]

DISPOSAL_METHODS = [
    "捨てた",
    "売った",
    "譲った",
    "寄付した",
    "リサイクル",
    "その他",
]

MOODS = [
    "😐 特に変わらない",
    "🙂 少しスッキリ",
    "😊 スッキリ",
    "✨ かなりスッキリ",
    "🎉 とても気持ちいい",
]

REASONS = [
    "長期間使っていなかった",
    "壊れていた",
    "サイズが合わない",
    "似た物を持っている",
    "必要なくなった",
    "収納場所を空けたい",
    "引っ越し準備",
    "買い替えた",
    "思い切って整理した",
    "その他",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "records": [],
        "goals": [],
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


def normalize_data(data):
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
        "goals",
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
            "item_name",
            "",
        )

        record.setdefault(
            "category",
            "その他",
        )

        record.setdefault(
            "method",
            "捨てた",
        )

        record.setdefault(
            "quantity",
            1,
        )

        record.setdefault(
            "sale_amount",
            0,
        )

        record.setdefault(
            "reason",
            "その他",
        )

        record.setdefault(
            "reason_detail",
            "",
        )

        record.setdefault(
            "mood",
            "😊 スッキリ",
        )

        record.setdefault(
            "gained",
            "",
        )

        record.setdefault(
            "future_rule",
            "",
        )

        record.setdefault(
            "memo",
            "",
        )

        record.setdefault(
            "favorite",
            False,
        )

        record.setdefault(
            "created_at",
            "",
        )

        record.setdefault(
            "updated_at",
            "",
        )

    for goal in data["goals"]:
        goal.setdefault(
            "id",
            create_id(),
        )

        goal.setdefault(
            "name",
            "",
        )

        goal.setdefault(
            "target_quantity",
            100,
        )

        goal.setdefault(
            "start_date",
            str(date.today()),
        )

        goal.setdefault(
            "deadline",
            "",
        )

        goal.setdefault(
            "active",
            True,
        )

        goal.setdefault(
            "memo",
            "",
        )

        goal.setdefault(
            "created_at",
            "",
        )

        goal.setdefault(
            "updated_at",
            "",
        )

    return data


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE,
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

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE,
            ):
                os.replace(
                    DATA_FILE,
                    broken_file,
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def parse_date(date_text):
    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

    except (
        TypeError,
        ValueError,
    ):
        return None


def format_date(date_text):
    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "未設定"

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
        parsed.weekday()
    ]

    return parsed.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_record_by_id(
    data,
    record_id,
):
    for record in data["records"]:
        if record.get(
            "id"
        ) == record_id:
            return record

    return None


def get_goal_by_id(
    data,
    goal_id,
):
    for goal in data["goals"]:
        if goal.get(
            "id"
        ) == goal_id:
            return goal

    return None


def total_quantity(
    records,
):
    return sum(
        int(
            record.get(
                "quantity",
                0,
            )
        )
        for record in records
    )


def total_sale_amount(
    records,
):
    return sum(
        int(
            record.get(
                "sale_amount",
                0,
            )
        )
        for record in records
    )


def calculate_streak(
    records,
):
    recorded_dates = {
        parse_date(
            record.get(
                "record_date",
                "",
            )
        )
        for record in records
    }

    recorded_dates.discard(
        None
    )

    if not recorded_dates:
        return 0

    current = date.today()

    if current not in recorded_dates:
        current -= timedelta(
            days=1
        )

        if current not in recorded_dates:
            return 0

    streak = 0

    while current in recorded_dates:
        streak += 1
        current -= timedelta(
            days=1
        )

    return streak


def goal_progress(
    goal,
    current_quantity,
):
    target = int(
        goal.get(
            "target_quantity",
            0,
        )
    )

    if target <= 0:
        return 0

    return min(
        current_quantity
        / target
        * 100,
        100,
    )


# =========================================================
# データ操作
# =========================================================

def add_record(
    data,
    values,
):
    record = {
        "id": create_id(),
        "record_date": (
            values["record_date"]
        ),
        "item_name": (
            values["item_name"]
        ),
        "category": (
            values["category"]
        ),
        "method": (
            values["method"]
        ),
        "quantity": int(
            values["quantity"]
        ),
        "sale_amount": int(
            values["sale_amount"]
        ),
        "reason": (
            values["reason"]
        ),
        "reason_detail": (
            values["reason_detail"]
        ),
        "mood": (
            values["mood"]
        ),
        "gained": (
            values["gained"]
        ),
        "future_rule": (
            values["future_rule"]
        ),
        "memo": (
            values["memo"]
        ),
        "favorite": False,
        "created_at": now_text(),
        "updated_at": "",
    }

    data["records"].append(
        record
    )

    save_data(data)


def update_record(
    data,
    record_id,
    values,
):
    record = get_record_by_id(
        data,
        record_id
    )

    if not record:
        return

    for key, value in values.items():
        record[key] = value

    record["quantity"] = int(
        record.get(
            "quantity",
            1,
        )
    )

    record["sale_amount"] = int(
        record.get(
            "sale_amount",
            0,
        )
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
        for record in data[
            "records"
        ]
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
        record_id
    )

    if not record:
        return

    record["favorite"] = not bool(
        record.get(
            "favorite",
            False,
        )
    )

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def add_goal(
    data,
    values,
):
    goal = {
        "id": create_id(),
        "name": values["name"],
        "target_quantity": int(
            values["target_quantity"]
        ),
        "start_date": (
            values["start_date"]
        ),
        "deadline": (
            values["deadline"]
        ),
        "active": True,
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["goals"].append(
        goal
    )

    save_data(data)


def update_goal(
    data,
    goal_id,
    values,
):
    goal = get_goal_by_id(
        data,
        goal_id
    )

    if not goal:
        return

    for key, value in values.items():
        goal[key] = value

    goal["target_quantity"] = int(
        goal.get(
            "target_quantity",
            100,
        )
    )

    goal["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_goal(
    data,
    goal_id,
):
    data["goals"] = [
        goal
        for goal in data[
            "goals"
        ]
        if goal.get(
            "id"
        ) != goal_id
    ]

    save_data(data)


# =========================================================
# デザイン
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(80, 180, 150, 0.08);
        border: 1px solid rgba(80, 180, 150, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(80, 180, 150, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(80, 180, 150, 0.18),
                rgba(100, 150, 255, 0.10)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
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

goals = data[
    "goals"
]

today_text = str(
    date.today()
)

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🗑️ 捨て活ログ</h1>
        <p>
            手放した物を記録して、
            空間・お金・時間が増えていくのを見える化
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    ) == today_text
]

monthly_records = [
    record
    for record in records
    if record.get(
        "record_date",
        "",
    ).startswith(
        current_month
    )
]

today_quantity = (
    total_quantity(
        today_records
    )
)

monthly_quantity = (
    total_quantity(
        monthly_records
    )
)

all_quantity = (
    total_quantity(
        records
    )
)

monthly_sale = (
    total_sale_amount(
        monthly_records
    )
)

all_sale = (
    total_sale_amount(
        records
    )
)

category_counter = Counter()

for record in records:
    category_counter[
        record.get(
            "category",
            "その他",
        )
    ] += int(
        record.get(
            "quantity",
            0,
        )
    )

top_category = (
    category_counter.most_common(
        1
    )[0][0]
    if category_counter
    else "なし"
)


metric_row1 = st.columns(
    4
)

metric_row1[0].metric(
    "今日手放した",
    f"{today_quantity}個"
)

metric_row1[1].metric(
    "今月手放した",
    f"{monthly_quantity}個"
)

metric_row1[2].metric(
    "累計",
    f"{all_quantity}個"
)

metric_row1[3].metric(
    "連続捨て活",
    f"{calculate_streak(records)}日"
)


metric_row2 = st.columns(
    4
)

metric_row2[0].metric(
    "今月の売却額",
    f"{monthly_sale:,}円"
)

metric_row2[1].metric(
    "累計売却額",
    f"{all_sale:,}円"
)

metric_row2[2].metric(
    "最多カテゴリー",
    top_category
)

metric_row2[3].metric(
    "記録数",
    f"{len(records)}件"
)


# =========================================================
# 現在の目標
# =========================================================

active_goals = [
    goal
    for goal in goals
    if goal.get(
        "active",
        True,
    )
]

if active_goals:
    st.divider()

    st.subheader(
        "🎯 捨て活目標"
    )

    for goal in active_goals:
        progress = goal_progress(
            goal,
            all_quantity,
        )

        remaining = max(
            int(
                goal.get(
                    "target_quantity",
                    0,
                )
            )
            - all_quantity,
            0,
        )

        with st.container(
            border=True
        ):
            column1, column2 = (
                st.columns(
                    [
                        4,
                        1,
                    ]
                )
            )

            with column1:
                st.markdown(
                    f"### "
                    f"{goal.get('name', '')}"
                )

                st.write(
                    f"目標："
                    f"**{goal.get('target_quantity', 0)}個**"
                )

                st.write(
                    f"現在："
                    f"**{all_quantity}個**"
                )

                if goal.get(
                    "deadline",
                    "",
                ):
                    st.caption(
                        f"期限："
                        f"{format_date(goal.get('deadline', ''))}"
                    )

            with column2:
                st.metric(
                    "達成率",
                    f"{progress:.1f}%"
                )

            st.progress(
                progress / 100
            )

            if remaining == 0:
                st.success(
                    "🎉 目標達成！"
                )

            else:
                st.info(
                    f"あと **{remaining}個**"
                )


# =========================================================
# 最近の捨て活
# =========================================================

if records:
    st.divider()

    st.subheader(
        "✨ 最近手放したもの"
    )

    recent_records = sorted(
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
    )[:3]

    for record in recent_records:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### 🗑️ "
                f"{record.get('item_name', '')}"
            )

            st.caption(
                f"{format_date(record.get('record_date', ''))} ／ "
                f"{record.get('category', '')}"
            )

            st.write(
                f"**{record.get('quantity', 1)}個** "
                f"・{record.get('method', '')}"
            )

            if int(
                record.get(
                    "sale_amount",
                    0,
                )
            ) > 0:
                st.success(
                    f"💰 "
                    f"{record.get('sale_amount', 0):,}円になりました"
                )


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    goal_tab,
    favorite_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 手放した物を登録",
        "📚 捨て活一覧",
        "🎯 目標",
        "⭐ 印象に残った捨て活",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 新規登録
# =========================================================

with add_tab:
    st.header(
        "➕ 手放した物を登録"
    )

    with st.form(
        "add_record_form",
        clear_on_submit=True,
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            record_date_input = (
                st.date_input(
                    "手放した日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            item_name = st.text_input(
                "手放した物",
                placeholder=(
                    "例：着なくなったTシャツ"
                ),
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            quantity = st.number_input(
                "個数",
                min_value=1,
                max_value=100000,
                value=1,
                step=1,
            )

        with column2:
            method = st.selectbox(
                "手放し方",
                DISPOSAL_METHODS,
            )

            sale_amount = (
                st.number_input(
                    "売却金額",
                    min_value=0,
                    max_value=100000000,
                    value=0,
                    step=100,
                    help=(
                        "売っていない場合は0円"
                    ),
                )
            )

            reason = st.selectbox(
                "主な理由",
                REASONS,
            )

            mood = st.selectbox(
                "手放した後の気分",
                MOODS,
                index=2,
            )

        reason_detail = (
            st.text_area(
                "手放した理由・背景",
                placeholder=(
                    "例：1年以上着ていなかったから"
                ),
                height=100,
            )
        )

        gained = st.text_area(
            "手放したことで増えたもの",
            placeholder=(
                "例：棚の空きスペース、掃除のしやすさ、売却金"
            ),
            height=100,
        )

        future_rule = st.text_area(
            "また物を増やさないためのメモ",
            placeholder=(
                "例：服は1着買ったら1着手放す"
            ),
            height=90,
        )

        memo = st.text_area(
            "その他メモ",
            placeholder=(
                "残しておきたいこと"
            ),
            height=80,
        )

        submitted = (
            st.form_submit_button(
                "🗑️ 捨て活を記録",
                use_container_width=True,
            )
        )

        if submitted:
            if not item_name.strip():
                st.error(
                    "手放した物を入力してください。"
                )

            else:
                add_record(
                    data,
                    {
                        "record_date": str(
                            record_date_input
                        ),
                        "item_name": (
                            item_name.strip()
                        ),
                        "category": (
                            category
                        ),
                        "method": method,
                        "quantity": (
                            quantity
                        ),
                        "sale_amount": (
                            sale_amount
                        ),
                        "reason": reason,
                        "reason_detail": (
                            reason_detail.strip()
                        ),
                        "mood": mood,
                        "gained": (
                            gained.strip()
                        ),
                        "future_rule": (
                            future_rule.strip()
                        ),
                        "memo": (
                            memo.strip()
                        ),
                    }
                )

                st.success(
                    "捨て活を記録しました！"
                )

                st.balloons()
                st.rerun()


# =========================================================
# 一覧
# =========================================================

with list_tab:
    st.header(
        "📚 捨て活一覧"
    )

    if not records:
        st.info(
            "捨て活記録はまだありません。"
        )

    else:
        filter_columns = (
            st.columns(3)
        )

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 検索",
                placeholder=(
                    "物・理由・メモ"
                ),
            )

        with filter_columns[1]:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES,
                )
            )

        with filter_columns[2]:
            method_filter = (
                st.selectbox(
                    "手放し方",
                    [
                        "すべて"
                    ]
                    + DISPOSAL_METHODS,
                )
            )

        sort_option = st.selectbox(
            "並び順",
            [
                "新しい順",
                "個数が多い順",
                "売却金額が高い順",
                "古い順",
            ],
        )

        filtered = list(
            records
        )

        if keyword.strip():
            word = (
                keyword.strip().lower()
            )

            filtered = [
                record
                for record in filtered
                if (
                    word
                    in record.get(
                        "item_name",
                        "",
                    ).lower()
                    or word
                    in record.get(
                        "reason_detail",
                        "",
                    ).lower()
                    or word
                    in record.get(
                        "gained",
                        "",
                    ).lower()
                    or word
                    in record.get(
                        "memo",
                        "",
                    ).lower()
                )
            ]

        if category_filter != "すべて":
            filtered = [
                record
                for record in filtered
                if record.get(
                    "category"
                )
                == category_filter
            ]

        if method_filter != "すべて":
            filtered = [
                record
                for record in filtered
                if record.get(
                    "method"
                )
                == method_filter
            ]

        if sort_option == "新しい順":
            filtered.sort(
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

        elif sort_option == "個数が多い順":
            filtered.sort(
                key=lambda record: int(
                    record.get(
                        "quantity",
                        0,
                    )
                ),
                reverse=True,
            )

        elif sort_option == "売却金額が高い順":
            filtered.sort(
                key=lambda record: int(
                    record.get(
                        "sale_amount",
                        0,
                    )
                ),
                reverse=True,
            )

        else:
            filtered.sort(
                key=lambda record: (
                    record.get(
                        "record_date",
                        "",
                    )
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered)}件**"
        )

        for record in filtered:
            record_id = record[
                "id"
            ]

            with st.container(
                border=True
            ):
                column1, column2 = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with column1:
                    favorite_icon = (
                        "⭐ "
                        if record.get(
                            "favorite",
                            False,
                        )
                        else ""
                    )

                    st.markdown(
                        f"### "
                        f"{favorite_icon}"
                        f"{record.get('item_name', '')}"
                    )

                    st.caption(
                        f"{format_date(record.get('record_date', ''))} ／ "
                        f"{record.get('category', '')} ／ "
                        f"{record.get('method', '')}"
                    )

                with column2:
                    st.metric(
                        "個数",
                        f"{record.get('quantity', 1)}個"
                    )

                info_columns = (
                    st.columns(3)
                )

                info_columns[0].metric(
                    "売却金額",
                    f"{record.get('sale_amount', 0):,}円"
                )

                info_columns[1].metric(
                    "手放し方",
                    record.get(
                        "method",
                        "",
                    )
                )

                info_columns[2].metric(
                    "気分",
                    record.get(
                        "mood",
                        "",
                    )
                )

                if record.get(
                    "reason_detail",
                    "",
                ):
                    st.info(
                        "手放した理由\n\n"
                        + record.get(
                            "reason_detail",
                            "",
                        )
                    )

                if record.get(
                    "gained",
                    "",
                ):
                    st.success(
                        "✨ 手放して増えたもの\n\n"
                        + record.get(
                            "gained",
                            "",
                        )
                    )

                if record.get(
                    "future_rule",
                    "",
                ):
                    st.warning(
                        "📌 次回へのルール\n\n"
                        + record.get(
                            "future_rule",
                            "",
                        )
                    )

                if record.get(
                    "memo",
                    "",
                ):
                    st.write(
                        record.get(
                            "memo",
                            "",
                        )
                    )

                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if record.get(
                            "favorite",
                            False,
                        )
                        else "☆ 印象に残す"
                    ),
                    key=(
                        f"favorite_"
                        f"{record_id}"
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_name = st.text_input(
                        "手放した物",
                        value=record.get(
                            "item_name",
                            "",
                        ),
                        key=(
                            f"edit_name_"
                            f"{record_id}"
                        ),
                    )

                    edit_date = st.date_input(
                        "日付",
                        value=(
                            parse_date(
                                record.get(
                                    "record_date",
                                    "",
                                )
                            )
                            or date.today()
                        ),
                        max_value=date.today(),
                        key=(
                            f"edit_date_"
                            f"{record_id}"
                        ),
                    )

                    edit_columns = (
                        st.columns(2)
                    )

                    with edit_columns[0]:
                        current_category = (
                            record.get(
                                "category",
                                "その他",
                            )
                        )

                        edit_category = (
                            st.selectbox(
                                "カテゴリー",
                                CATEGORIES,
                                index=(
                                    CATEGORIES.index(
                                        current_category
                                    )
                                    if current_category
                                    in CATEGORIES
                                    else (
                                        len(
                                            CATEGORIES
                                        )
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_category_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        current_method = (
                            record.get(
                                "method",
                                "捨てた",
                            )
                        )

                        edit_method = (
                            st.selectbox(
                                "手放し方",
                                DISPOSAL_METHODS,
                                index=(
                                    DISPOSAL_METHODS.index(
                                        current_method
                                    )
                                    if current_method
                                    in DISPOSAL_METHODS
                                    else 0
                                ),
                                key=(
                                    f"edit_method_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        edit_quantity = (
                            st.number_input(
                                "個数",
                                min_value=1,
                                max_value=100000,
                                value=int(
                                    record.get(
                                        "quantity",
                                        1,
                                    )
                                ),
                                key=(
                                    f"edit_quantity_"
                                    f"{record_id}"
                                ),
                            )
                        )

                    with edit_columns[1]:
                        edit_sale_amount = (
                            st.number_input(
                                "売却金額",
                                min_value=0,
                                max_value=100000000,
                                value=int(
                                    record.get(
                                        "sale_amount",
                                        0,
                                    )
                                ),
                                key=(
                                    f"edit_sale_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        current_reason = (
                            record.get(
                                "reason",
                                "その他",
                            )
                        )

                        edit_reason = (
                            st.selectbox(
                                "主な理由",
                                REASONS,
                                index=(
                                    REASONS.index(
                                        current_reason
                                    )
                                    if current_reason
                                    in REASONS
                                    else (
                                        len(REASONS)
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_reason_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        current_mood = (
                            record.get(
                                "mood",
                                "😊 スッキリ",
                            )
                        )

                        edit_mood = (
                            st.selectbox(
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
                                    f"edit_mood_"
                                    f"{record_id}"
                                ),
                            )
                        )

                    edit_reason_detail = (
                        st.text_area(
                            "理由・背景",
                            value=record.get(
                                "reason_detail",
                                "",
                            ),
                            key=(
                                f"edit_reason_detail_"
                                f"{record_id}"
                            ),
                        )
                    )

                    edit_gained = (
                        st.text_area(
                            "増えたもの",
                            value=record.get(
                                "gained",
                                "",
                            ),
                            key=(
                                f"edit_gained_"
                                f"{record_id}"
                            ),
                        )
                    )

                    edit_future_rule = (
                        st.text_area(
                            "次回へのルール",
                            value=record.get(
                                "future_rule",
                                "",
                            ),
                            key=(
                                f"edit_rule_"
                                f"{record_id}"
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
                            f"edit_memo_"
                            f"{record_id}"
                        ),
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_record_"
                            f"{record_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_name.strip():
                            st.error(
                                "手放した物を入力してください。"
                            )

                        else:
                            update_record(
                                data,
                                record_id,
                                {
                                    "item_name": (
                                        edit_name.strip()
                                    ),
                                    "record_date": str(
                                        edit_date
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "method": (
                                        edit_method
                                    ),
                                    "quantity": (
                                        edit_quantity
                                    ),
                                    "sale_amount": (
                                        edit_sale_amount
                                    ),
                                    "reason": (
                                        edit_reason
                                    ),
                                    "mood": (
                                        edit_mood
                                    ),
                                    "reason_detail": (
                                        edit_reason_detail.strip()
                                    ),
                                    "gained": (
                                        edit_gained.strip()
                                    ),
                                    "future_rule": (
                                        edit_future_rule.strip()
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                }
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 記録を削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{record_id}"
                            ),
                        )
                    )

                    if st.button(
                        "この記録を削除",
                        key=(
                            f"delete_record_"
                            f"{record_id}"
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
# 目標
# =========================================================

with goal_tab:
    st.header(
        "🎯 捨て活目標"
    )

    with st.form(
        "add_goal_form",
        clear_on_submit=True,
    ):
        goal_columns = (
            st.columns(2)
        )

        with goal_columns[0]:
            goal_name = st.text_input(
                "目標名",
                placeholder=(
                    "例：100個手放す"
                ),
            )

            target_quantity = (
                st.number_input(
                    "目標個数",
                    min_value=1,
                    max_value=1000000,
                    value=100,
                    step=10,
                )
            )

        with goal_columns[1]:
            start_date_input = (
                st.date_input(
                    "開始日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            set_deadline = (
                st.checkbox(
                    "期限を設定する"
                )
            )

            deadline = ""

            if set_deadline:
                deadline = str(
                    st.date_input(
                        "期限",
                        value=(
                            date.today()
                            + timedelta(
                                days=30
                            )
                        ),
                    )
                )

        goal_memo = st.text_area(
            "目標メモ",
            placeholder=(
                "例：引っ越し前に不要な物を減らす"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🎯 目標を追加",
                use_container_width=True,
            )
        )

        if submitted:
            if not goal_name.strip():
                st.error(
                    "目標名を入力してください。"
                )

            else:
                add_goal(
                    data,
                    {
                        "name": (
                            goal_name.strip()
                        ),
                        "target_quantity": (
                            target_quantity
                        ),
                        "start_date": str(
                            start_date_input
                        ),
                        "deadline": (
                            deadline
                        ),
                        "memo": (
                            goal_memo.strip()
                        ),
                    }
                )

                st.rerun()

    st.divider()

    if not goals:
        st.info(
            "捨て活目標はまだありません。"
        )

    for goal in goals:
        goal_id = goal[
            "id"
        ]

        progress = goal_progress(
            goal,
            all_quantity,
        )

        with st.container(
            border=True
        ):
            st.subheader(
                goal.get(
                    "name",
                    "",
                )
            )

            columns = st.columns(
                4
            )

            columns[0].metric(
                "目標",
                f"{goal.get('target_quantity', 0)}個"
            )

            columns[1].metric(
                "現在",
                f"{all_quantity}個"
            )

            columns[2].metric(
                "達成率",
                f"{progress:.1f}%"
            )

            columns[3].metric(
                "状態",
                (
                    "有効"
                    if goal.get(
                        "active",
                        True,
                    )
                    else "停止中"
                )
            )

            st.progress(
                progress / 100
            )

            if goal.get(
                "memo",
                "",
            ):
                st.info(
                    goal.get(
                        "memo",
                        "",
                    )
                )

            with st.expander(
                "✏️ 目標を編集"
            ):
                edit_goal_name = (
                    st.text_input(
                        "目標名",
                        value=goal.get(
                            "name",
                            "",
                        ),
                        key=(
                            f"edit_goal_name_"
                            f"{goal_id}"
                        ),
                    )
                )

                edit_target = (
                    st.number_input(
                        "目標個数",
                        min_value=1,
                        max_value=1000000,
                        value=int(
                            goal.get(
                                "target_quantity",
                                100,
                            )
                        ),
                        key=(
                            f"edit_goal_target_"
                            f"{goal_id}"
                        ),
                    )
                )

                edit_active = (
                    st.checkbox(
                        "この目標を有効にする",
                        value=bool(
                            goal.get(
                                "active",
                                True,
                            )
                        ),
                        key=(
                            f"edit_goal_active_"
                            f"{goal_id}"
                        ),
                    )
                )

                deadline_value = (
                    parse_date(
                        goal.get(
                            "deadline",
                            "",
                        )
                    )
                )

                edit_has_deadline = (
                    st.checkbox(
                        "期限を設定",
                        value=bool(
                            deadline_value
                        ),
                        key=(
                            f"edit_goal_deadline_check_"
                            f"{goal_id}"
                        ),
                    )
                )

                edit_deadline = ""

                if edit_has_deadline:
                    edit_deadline = str(
                        st.date_input(
                            "期限",
                            value=(
                                deadline_value
                                or date.today()
                            ),
                            key=(
                                f"edit_goal_deadline_"
                                f"{goal_id}"
                            ),
                        )
                    )

                edit_goal_memo = (
                    st.text_area(
                        "メモ",
                        value=goal.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_goal_memo_"
                            f"{goal_id}"
                        ),
                    )
                )

                if st.button(
                    "目標を保存",
                    key=(
                        f"save_goal_"
                        f"{goal_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_goal_name.strip():
                        st.error(
                            "目標名を入力してください。"
                        )

                    else:
                        update_goal(
                            data,
                            goal_id,
                            {
                                "name": (
                                    edit_goal_name.strip()
                                ),
                                "target_quantity": (
                                    edit_target
                                ),
                                "active": (
                                    edit_active
                                ),
                                "deadline": (
                                    edit_deadline
                                ),
                                "memo": (
                                    edit_goal_memo.strip()
                                ),
                            }
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 目標を削除"
            ):
                confirm_goal_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_goal_delete_"
                            f"{goal_id}"
                        ),
                    )
                )

                if st.button(
                    "この目標を削除",
                    key=(
                        f"delete_goal_"
                        f"{goal_id}"
                    ),
                    disabled=(
                        not confirm_goal_delete
                    ),
                    use_container_width=True,
                ):
                    delete_goal(
                        data,
                        goal_id,
                    )

                    st.rerun()


# =========================================================
# お気に入り
# =========================================================

with favorite_tab:
    st.header(
        "⭐ 印象に残った捨て活"
    )

    favorites = [
        record
        for record in records
        if record.get(
            "favorite",
            False,
        )
    ]

    if not favorites:
        st.info(
            "印象に残した記録はまだありません。"
        )

    else:
        favorites.sort(
            key=lambda record: (
                int(
                    record.get(
                        "quantity",
                        0,
                    )
                ),
                int(
                    record.get(
                        "sale_amount",
                        0,
                    )
                ),
            ),
            reverse=True,
        )

        for record in favorites:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### ⭐ "
                    f"{record.get('item_name', '')}"
                )

                st.caption(
                    f"{record.get('category', '')} ／ "
                    f"{record.get('quantity', 1)}個"
                )

                if record.get(
                    "gained",
                    "",
                ):
                    st.success(
                        record.get(
                            "gained",
                            "",
                        )
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 捨て活分析"
    )

    if not records:
        st.info(
            "分析できる記録がありません。"
        )

    else:
        analysis_rows = []

        for record in records:
            analysis_rows.append(
                {
                    "日付": (
                        record.get(
                            "record_date",
                            "",
                        )
                    ),
                    "月": (
                        record.get(
                            "record_date",
                            "",
                        )[:7]
                    ),
                    "物": (
                        record.get(
                            "item_name",
                            "",
                        )
                    ),
                    "カテゴリー": (
                        record.get(
                            "category",
                            "",
                        )
                    ),
                    "手放し方": (
                        record.get(
                            "method",
                            "",
                        )
                    ),
                    "個数": int(
                        record.get(
                            "quantity",
                            0,
                        )
                    ),
                    "売却金額": int(
                        record.get(
                            "sale_amount",
                            0,
                        )
                    ),
                    "理由": (
                        record.get(
                            "reason",
                            "",
                        )
                    ),
                    "気分": (
                        record.get(
                            "mood",
                            "",
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "月別手放し個数"
        )

        monthly_summary = (
            analysis_df.groupby(
                "月",
                as_index=False,
            )
            .agg(
                手放した個数=(
                    "個数",
                    "sum",
                ),
                売却金額=(
                    "売却金額",
                    "sum",
                ),
            )
            .sort_values(
                "月"
            )
        )

        st.bar_chart(
            monthly_summary.set_index(
                "月"
            )[["手放した個数"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "カテゴリー別"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .agg(
                個数=(
                    "個数",
                    "sum",
                ),
                売却金額=(
                    "売却金額",
                    "sum",
                ),
            )
            .sort_values(
                "個数",
                ascending=False,
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["個数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "手放し方別"
        )

        method_summary = (
            analysis_df.groupby(
                "手放し方",
                as_index=False,
            )
            .agg(
                個数=(
                    "個数",
                    "sum",
                ),
                売却金額=(
                    "売却金額",
                    "sum",
                ),
            )
            .sort_values(
                "個数",
                ascending=False,
            )
        )

        st.bar_chart(
            method_summary.set_index(
                "手放し方"
            )[["個数"]]
        )

        st.dataframe(
            method_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "手放した理由"
        )

        reason_summary = (
            analysis_df.groupby(
                "理由",
                as_index=False,
            )
            .agg(
                回数=(
                    "物",
                    "count",
                ),
                個数=(
                    "個数",
                    "sum",
                ),
            )
            .sort_values(
                "個数",
                ascending=False,
            )
        )

        st.bar_chart(
            reason_summary.set_index(
                "理由"
            )[["個数"]]
        )

        st.dataframe(
            reason_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "売却金額ランキング"
        )

        sale_ranking = (
            analysis_df[
                analysis_df[
                    "売却金額"
                ]
                > 0
            ]
            .sort_values(
                "売却金額",
                ascending=False,
            )
        )

        if sale_ranking.empty:
            st.info(
                "売却記録はまだありません。"
            )

        else:
            st.dataframe(
                sale_ranking[
                    [
                        "物",
                        "カテゴリー",
                        "個数",
                        "売却金額",
                        "日付",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "手放した後の気分"
        )

        mood_summary = (
            analysis_df.groupby(
                "気分",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "回数"
                }
            )
            .sort_values(
                "回数",
                ascending=False,
            )
        )

        st.bar_chart(
            mood_summary.set_index(
                "気分"
            )[["回数"]]
        )

        st.dataframe(
            mood_summary,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# データ管理
# =========================================================

with data_tab:
    st.header(
        "💾 データ管理"
    )

    st.subheader(
        "JSONバックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"declutter_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = (
        st.file_uploader(
            "バックアップJSONを選択",
            type=[
                "json"
            ],
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict,
                )
                or "records"
                not in imported_data
                or "goals"
                not in imported_data
            ):
                st.error(
                    "対応していないJSON形式です。"
                )

            else:
                imported_data = (
                    normalize_data(
                        imported_data
                    )
                )

                st.warning(
                    "復元すると現在のデータが上書きされます。"
                )

                confirm_restore = (
                    st.checkbox(
                        "上書き復元を確認しました"
                    )
                )

                if st.button(
                    "JSONから復元",
                    disabled=(
                        not confirm_restore
                    ),
                    use_container_width=True,
                ):
                    save_data(
                        imported_data
                    )

                    st.success(
                        "データを復元しました！"
                    )

                    st.rerun()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "捨て活記録・目標がすべて削除されます。"
    )

    confirm_delete_all = (
        st.checkbox(
            "全データ削除を確認しました"
        )
    )

    if st.button(
        "すべて削除",
        disabled=(
            not confirm_delete_all
        ),
        use_container_width=True,
    ):
        save_data(
            create_empty_data()
        )

        st.success(
            "すべてのデータを削除しました。"
        )

        st.rerun()


# =========================================================
# フッター
# =========================================================

st.divider()

st.success(
    "物をひとつ手放すたびに、暮らしに少し余白が増えていく。🗑️✨"
)
