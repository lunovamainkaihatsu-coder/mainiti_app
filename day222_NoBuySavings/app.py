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
    page_title="買わなかった貯金",
    page_icon="💸",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "savings_data.json",
)

CATEGORIES = [
    "飲食",
    "お菓子",
    "コンビニ",
    "外食",
    "服",
    "趣味",
    "ゲーム",
    "アプリ",
    "家電",
    "日用品",
    "子ども用品",
    "車",
    "サブスク",
    "その他",
]

NECESSITY_LEVELS = [
    "必要だった",
    "少し必要だった",
    "なくても困らない",
    "完全な衝動買い",
]

STATUS_OPTIONS = [
    "買わなかった",
    "あとで購入した",
    "保留中",
]

STATUS_ICONS = {
    "買わなかった": "💰",
    "あとで購入した": "🛒",
    "保留中": "⏳",
}

REASON_OPTIONS = [
    "家に代わりの物があった",
    "予算を超えていた",
    "衝動買いだと思った",
    "今すぐ必要ではなかった",
    "価格が高かった",
    "他の目標を優先した",
    "家族と相談した",
    "時間を置いて考えた",
    "その他",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作る。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds",
    )


def create_empty_data():
    """空の初期データを返す。"""

    return {
        "records": [],
        "goals": [],
    }


def save_data(data):
    """JSONファイルへ保存する。"""

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
    """過去データへ不足項目を追加する。"""

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
            "amount",
            0,
        )

        record.setdefault(
            "category",
            "その他",
        )

        record.setdefault(
            "wanted_reason",
            "",
        )

        record.setdefault(
            "not_buy_reason",
            "",
        )

        record.setdefault(
            "reason_type",
            "その他",
        )

        record.setdefault(
            "resistance_score",
            3,
        )

        record.setdefault(
            "necessity",
            "なくても困らない",
        )

        record.setdefault(
            "status",
            "買わなかった",
        )

        record.setdefault(
            "purchased_date",
            "",
        )

        record.setdefault(
            "actual_purchase_amount",
            0,
        )

        record.setdefault(
            "memo",
            "",
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
            "target_amount",
            0,
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
    """JSONファイルからデータを読み込む。"""

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
    """日付文字列をdate型へ変換する。"""

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
    """日付を日本語表示にする。"""

    parsed = parse_date(
        date_text,
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
    """IDから記録を取得する。"""

    for record in data["records"]:
        if record.get(
            "id",
        ) == record_id:
            return record

    return None


def get_goal_by_id(
    data,
    goal_id,
):
    """IDから目標を取得する。"""

    for goal in data["goals"]:
        if goal.get(
            "id",
        ) == goal_id:
            return goal

    return None


def effective_saving_amount(
    record,
):
    """実際の節約額を返す。"""

    if record.get(
        "status",
    ) != "買わなかった":
        return 0

    return int(
        record.get(
            "amount",
            0,
        )
    )


def total_savings(
    records,
):
    """節約額合計を返す。"""

    return sum(
        effective_saving_amount(
            record,
        )
        for record in records
    )


def average_score(
    records,
    key,
):
    """数値項目の平均を返す。"""

    values = [
        int(
            record.get(
                key,
                0,
            )
        )
        for record in records
        if int(
            record.get(
                key,
                0,
            )
        ) > 0
    ]

    if not values:
        return 0

    return (
        sum(values)
        / len(values)
    )


def calculate_streak(
    records,
):
    """買わなかった記録の連続日数を計算する。"""

    recorded_dates = {
        parse_date(
            record.get(
                "record_date",
                "",
            )
        )
        for record in records
        if record.get(
            "status",
        ) == "買わなかった"
    }

    recorded_dates.discard(
        None,
    )

    if not recorded_dates:
        return 0

    current_date = date.today()

    if current_date not in recorded_dates:
        current_date -= timedelta(
            days=1,
        )

        if current_date not in recorded_dates:
            return 0

    streak = 0

    while current_date in recorded_dates:
        streak += 1
        current_date -= timedelta(
            days=1,
        )

    return streak


def goal_progress(
    goal,
    savings_amount,
):
    """目標達成率を返す。"""

    target = int(
        goal.get(
            "target_amount",
            0,
        )
    )

    if target <= 0:
        return 0

    return min(
        savings_amount
        / target
        * 100,
        100,
    )


def purchased_later_rate(
    records,
):
    """あとで購入した割合を返す。"""

    if not records:
        return 0

    purchased_count = len(
        [
            record
            for record in records
            if record.get(
                "status",
            ) == "あとで購入した"
        ]
    )

    return (
        purchased_count
        / len(records)
        * 100
    )


# =========================================================
# データ操作
# =========================================================

def add_record(
    data,
    values,
):
    """買わなかった記録を追加する。"""

    record = {
        "id": create_id(),
        "record_date": (
            values["record_date"]
        ),
        "item_name": (
            values["item_name"]
        ),
        "amount": int(
            values["amount"]
        ),
        "category": (
            values["category"]
        ),
        "wanted_reason": (
            values["wanted_reason"]
        ),
        "not_buy_reason": (
            values["not_buy_reason"]
        ),
        "reason_type": (
            values["reason_type"]
        ),
        "resistance_score": int(
            values["resistance_score"]
        ),
        "necessity": (
            values["necessity"]
        ),
        "status": (
            values["status"]
        ),
        "purchased_date": "",
        "actual_purchase_amount": 0,
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["records"].append(
        record,
    )

    save_data(data)


def update_record(
    data,
    record_id,
    values,
):
    """記録を更新する。"""

    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    previous_status = record.get(
        "status",
        "買わなかった",
    )

    for key, value in values.items():
        record[key] = value

    record["amount"] = int(
        record.get(
            "amount",
            0,
        )
    )

    record[
        "resistance_score"
    ] = int(
        record.get(
            "resistance_score",
            3,
        )
    )

    record[
        "actual_purchase_amount"
    ] = int(
        record.get(
            "actual_purchase_amount",
            0,
        )
    )

    if (
        record.get(
            "status",
        )
        == "あとで購入した"
        and previous_status
        != "あとで購入した"
        and not record.get(
            "purchased_date",
            "",
        )
    ):
        record["purchased_date"] = str(
            date.today()
        )

    elif record.get(
        "status",
    ) != "あとで購入した":
        record["purchased_date"] = ""
        record[
            "actual_purchase_amount"
        ] = 0

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_record(
    data,
    record_id,
):
    """記録を削除する。"""

    data["records"] = [
        record
        for record in data[
            "records"
        ]
        if record.get(
            "id",
        ) != record_id
    ]

    save_data(data)


def add_goal(
    data,
    values,
):
    """貯金目標を追加する。"""

    goal = {
        "id": create_id(),
        "name": values["name"],
        "target_amount": int(
            values["target_amount"]
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
        goal,
    )

    save_data(data)


def update_goal(
    data,
    goal_id,
    values,
):
    """貯金目標を更新する。"""

    goal = get_goal_by_id(
        data,
        goal_id,
    )

    if not goal:
        return

    for key, value in values.items():
        goal[key] = value

    goal["target_amount"] = int(
        goal.get(
            "target_amount",
            0,
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
    """貯金目標を削除する。"""

    data["goals"] = [
        goal
        for goal in data[
            "goals"
        ]
        if goal.get(
            "id",
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
        background: rgba(65, 190, 120, 0.08);
        border: 1px solid rgba(65, 190, 120, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(65, 190, 120, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(65, 190, 120, 0.18),
                rgba(255, 200, 70, 0.12)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }

    .saving-amount {
        font-size: 2.1rem;
        font-weight: 700;
        text-align: center;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

records = data["records"]
goals = data["goals"]

today_text = str(
    date.today()
)

current_month = (
    date.today().strftime(
        "%Y-%m",
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>💸 買わなかった貯金</h1>
        <p>
            使わなかったお金を、
            未来の自分へ残せた成果として記録するアプリ
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
        "record_date",
    ) == today_text
]

monthly_records = [
    record
    for record in records
    if record.get(
        "record_date",
        "",
    ).startswith(
        current_month,
    )
]

today_savings = total_savings(
    today_records,
)

monthly_savings = total_savings(
    monthly_records,
)

all_savings = total_savings(
    records,
)

monthly_no_buy_count = len(
    [
        record
        for record in monthly_records
        if record.get(
            "status",
        ) == "買わなかった"
    ]
)

average_resistance = average_score(
    monthly_records,
    "resistance_score",
)

streak_count = calculate_streak(
    records,
)

category_counter = Counter()

for record in monthly_records:
    saving = effective_saving_amount(
        record,
    )

    if saving > 0:
        category_counter[
            record.get(
                "category",
                "その他",
            )
        ] += saving

top_category = (
    category_counter.most_common(
        1,
    )[0][0]
    if category_counter
    else "なし"
)


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "今日浮いた金額",
    f"{today_savings:,}円",
)

metric_row1[1].metric(
    "今月浮いた金額",
    f"{monthly_savings:,}円",
)

metric_row1[2].metric(
    "累計浮いた金額",
    f"{all_savings:,}円",
)

metric_row1[3].metric(
    "今月の我慢回数",
    f"{monthly_no_buy_count}回",
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "最多カテゴリー",
    top_category,
)

metric_row2[1].metric(
    "平均我慢度",
    (
        f"{average_resistance:.1f}/5"
        if average_resistance > 0
        else "未記録"
    ),
)

metric_row2[2].metric(
    "連続記録",
    f"{streak_count}日",
)

metric_row2[3].metric(
    "あとで購入した割合",
    f"{purchased_later_rate(records):.1f}%",
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
        "🎯 買わなかった貯金の目標"
    )

    for goal in active_goals:
        progress = goal_progress(
            goal,
            all_savings,
        )

        with st.container(
            border=True,
        ):
            goal_column1, goal_column2 = (
                st.columns(
                    [
                        4,
                        1,
                    ]
                )
            )

            with goal_column1:
                st.markdown(
                    f"### {goal.get('name', '')}"
                )

                st.write(
                    f"目標金額："
                    f"**{goal.get('target_amount', 0):,}円**"
                )

                st.write(
                    f"現在："
                    f"**{all_savings:,}円**"
                )

                if goal.get(
                    "deadline",
                    "",
                ):
                    st.caption(
                        f"目標期限："
                        f"{format_date(goal.get('deadline', ''))}"
                    )

            with goal_column2:
                st.metric(
                    "達成率",
                    f"{progress:.1f}%",
                )

            st.progress(
                progress / 100,
            )

            remaining = max(
                int(
                    goal.get(
                        "target_amount",
                        0,
                    )
                )
                - all_savings,
                0,
            )

            if remaining == 0:
                st.success(
                    "目標達成！おめでとうございます！🎉"
                )

            else:
                st.info(
                    f"目標まであと "
                    f"**{remaining:,}円**"
                )


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "🌱 今日の買わなかった記録"
)

saved_today_records = [
    record
    for record in today_records
    if record.get(
        "status",
    ) == "買わなかった"
]

if not saved_today_records:
    st.info(
        "今日の記録はまだありません。"
    )

else:
    for record in saved_today_records:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 💰 "
                f"{record.get('item_name', '')}"
            )

            st.write(
                f"未来へ残せた金額："
                f"**{record.get('amount', 0):,}円**"
            )

            st.caption(
                f"{record.get('category', '')} ／ "
                f"我慢度 {record.get('resistance_score', 3)}/5"
            )


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    records_tab,
    goal_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 買わなかった物を登録",
        "📚 記録一覧",
        "🎯 貯金目標",
        "📈 節約分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 記録登録
# =========================================================

with add_tab:
    st.header(
        "➕ 買わなかった物を登録"
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
                    "記録日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            item_name = st.text_input(
                "買わなかった物",
                placeholder=(
                    "例：コンビニのスイーツ"
                ),
            )

            amount = st.number_input(
                "金額",
                min_value=1,
                max_value=100000000,
                value=500,
                step=10,
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

        with column2:
            status = st.selectbox(
                "現在の状態",
                STATUS_OPTIONS,
            )

            necessity = st.selectbox(
                "本当に必要だった？",
                NECESSITY_LEVELS,
                index=2,
            )

            resistance_score = (
                st.slider(
                    "我慢できた度",
                    min_value=1,
                    max_value=5,
                    value=3,
                )
            )

            reason_type = st.selectbox(
                "買わなかった主な理由",
                REASON_OPTIONS,
            )

        wanted_reason = st.text_area(
            "欲しかった理由",
            placeholder=(
                "疲れていた、広告を見た、気分転換したかったなど"
            ),
            height=100,
        )

        not_buy_reason = st.text_area(
            "買わなかった理由",
            placeholder=(
                "家に代わりがあった、予算を守りたかったなど"
            ),
            height=100,
        )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "そのときの気持ちや、次回の対策"
            ),
            height=80,
        )

        submitted = (
            st.form_submit_button(
                "💸 記録を保存",
                use_container_width=True,
            )
        )

        if submitted:
            if not item_name.strip():
                st.error(
                    "買わなかった物を入力してください。"
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
                        "amount": amount,
                        "category": category,
                        "wanted_reason": (
                            wanted_reason.strip()
                        ),
                        "not_buy_reason": (
                            not_buy_reason.strip()
                        ),
                        "reason_type": (
                            reason_type
                        ),
                        "resistance_score": (
                            resistance_score
                        ),
                        "necessity": necessity,
                        "status": status,
                        "memo": memo.strip(),
                    },
                )

                st.success(
                    "買わなかった記録を保存しました！"
                )

                if status == "買わなかった":
                    st.balloons()

                st.rerun()

    st.divider()

    st.info(
        "必要な物まで我慢しなくて大丈夫。"
        "不要な出費を減らし、納得できるお金の使い方を増やそう。"
    )


# =========================================================
# 記録一覧
# =========================================================

with records_tab:
    st.header(
        "📚 買わなかった記録一覧"
    )

    if not records:
        st.info(
            "記録はまだありません。"
        )

    else:
        filter_columns = st.columns(3)

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "商品名・理由・メモ"
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
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ]
                    + STATUS_OPTIONS,
                )
            )

        necessity_filter = (
            st.multiselect(
                "必要性",
                NECESSITY_LEVELS,
                default=NECESSITY_LEVELS,
            )
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "新しい順",
                "金額が高い順",
                "我慢度が高い順",
                "古い順",
            ],
        )

        filtered_records = list(
            records,
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_records = [
                record
                for record in filtered_records
                if (
                    search_word
                    in record.get(
                        "item_name",
                        "",
                    ).lower()
                    or search_word
                    in record.get(
                        "wanted_reason",
                        "",
                    ).lower()
                    or search_word
                    in record.get(
                        "not_buy_reason",
                        "",
                    ).lower()
                    or search_word
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
                    "category",
                )
                == category_filter
            ]

        if status_filter != "すべて":
            filtered_records = [
                record
                for record in filtered_records
                if record.get(
                    "status",
                )
                == status_filter
            ]

        filtered_records = [
            record
            for record in filtered_records
            if record.get(
                "necessity",
            )
            in necessity_filter
        ]

        if sort_option == "新しい順":
            filtered_records.sort(
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

        elif sort_option == "金額が高い順":
            filtered_records.sort(
                key=lambda record: int(
                    record.get(
                        "amount",
                        0,
                    )
                ),
                reverse=True,
            )

        elif sort_option == "我慢度が高い順":
            filtered_records.sort(
                key=lambda record: int(
                    record.get(
                        "resistance_score",
                        0,
                    )
                ),
                reverse=True,
            )

        else:
            filtered_records.sort(
                key=lambda record: (
                    record.get(
                        "record_date",
                        "",
                    ),
                    record.get(
                        "created_at",
                        "",
                    ),
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_records)}件**"
        )

        for record in filtered_records:
            record_id = record["id"]

            with st.container(
                border=True,
            ):
                title_column, amount_column = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with title_column:
                    status = record.get(
                        "status",
                        "買わなかった",
                    )

                    st.markdown(
                        f"### "
                        f"{STATUS_ICONS.get(status, '')} "
                        f"{record.get('item_name', '')}"
                    )

                    st.caption(
                        f"{format_date(record.get('record_date', ''))} ／ "
                        f"{record.get('category', '')} ／ "
                        f"{status}"
                    )

                with amount_column:
                    st.metric(
                        "対象金額",
                        f"{record.get('amount', 0):,}円",
                    )

                info_columns = st.columns(3)

                info_columns[0].metric(
                    "我慢度",
                    f"{record.get('resistance_score', 3)}/5",
                )

                info_columns[1].metric(
                    "必要性",
                    record.get(
                        "necessity",
                        "",
                    ),
                )

                info_columns[2].metric(
                    "節約額",
                    f"{effective_saving_amount(record):,}円",
                )

                if record.get(
                    "wanted_reason",
                    "",
                ):
                    st.write(
                        "**欲しかった理由**"
                    )

                    st.write(
                        record.get(
                            "wanted_reason",
                            "",
                        )
                    )

                if record.get(
                    "not_buy_reason",
                    "",
                ):
                    st.success(
                        "買わなかった理由\n\n"
                        + record.get(
                            "not_buy_reason",
                            "",
                        )
                    )

                if record.get(
                    "reason_type",
                    "",
                ):
                    st.caption(
                        f"主な理由："
                        f"{record.get('reason_type', '')}"
                    )

                if record.get(
                    "status",
                ) == "あとで購入した":
                    st.warning(
                        f"あとで購入済み："
                        f"{format_date(record.get('purchased_date', ''))}"
                    )

                    if int(
                        record.get(
                            "actual_purchase_amount",
                            0,
                        )
                    ) > 0:
                        st.write(
                            f"実際の購入額："
                            f"**{record.get('actual_purchase_amount', 0):,}円**"
                        )

                if record.get(
                    "memo",
                    "",
                ):
                    st.info(
                        record.get(
                            "memo",
                            "",
                        )
                    )

                with st.expander(
                    "✏️ 記録を編集"
                ):
                    edit_date = st.date_input(
                        "記録日",
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

                    edit_name = st.text_input(
                        "買わなかった物",
                        value=record.get(
                            "item_name",
                            "",
                        ),
                        key=(
                            f"edit_name_"
                            f"{record_id}"
                        ),
                    )

                    edit_amount = (
                        st.number_input(
                            "金額",
                            min_value=1,
                            max_value=100000000,
                            value=int(
                                record.get(
                                    "amount",
                                    1,
                                )
                            ),
                            key=(
                                f"edit_amount_"
                                f"{record_id}"
                            ),
                        )
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
                                        len(CATEGORIES)
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_category_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        current_status = (
                            record.get(
                                "status",
                                "買わなかった",
                            )
                        )

                        edit_status = (
                            st.selectbox(
                                "状態",
                                STATUS_OPTIONS,
                                index=(
                                    STATUS_OPTIONS.index(
                                        current_status
                                    )
                                    if current_status
                                    in STATUS_OPTIONS
                                    else 0
                                ),
                                key=(
                                    f"edit_status_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        current_necessity = (
                            record.get(
                                "necessity",
                                "なくても困らない",
                            )
                        )

                        edit_necessity = (
                            st.selectbox(
                                "必要性",
                                NECESSITY_LEVELS,
                                index=(
                                    NECESSITY_LEVELS.index(
                                        current_necessity
                                    )
                                    if current_necessity
                                    in NECESSITY_LEVELS
                                    else 2
                                ),
                                key=(
                                    f"edit_necessity_"
                                    f"{record_id}"
                                ),
                            )
                        )

                    with edit_columns[1]:
                        current_reason = (
                            record.get(
                                "reason_type",
                                "その他",
                            )
                        )

                        edit_reason_type = (
                            st.selectbox(
                                "主な理由",
                                REASON_OPTIONS,
                                index=(
                                    REASON_OPTIONS.index(
                                        current_reason
                                    )
                                    if current_reason
                                    in REASON_OPTIONS
                                    else (
                                        len(REASON_OPTIONS)
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_reason_type_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        edit_resistance = (
                            st.slider(
                                "我慢度",
                                min_value=1,
                                max_value=5,
                                value=int(
                                    record.get(
                                        "resistance_score",
                                        3,
                                    )
                                ),
                                key=(
                                    f"edit_resistance_"
                                    f"{record_id}"
                                ),
                            )
                        )

                    edit_wanted_reason = (
                        st.text_area(
                            "欲しかった理由",
                            value=record.get(
                                "wanted_reason",
                                "",
                            ),
                            key=(
                                f"edit_wanted_"
                                f"{record_id}"
                            ),
                        )
                    )

                    edit_not_buy_reason = (
                        st.text_area(
                            "買わなかった理由",
                            value=record.get(
                                "not_buy_reason",
                                "",
                            ),
                            key=(
                                f"edit_not_buy_"
                                f"{record_id}"
                            ),
                        )
                    )

                    purchased_date_text = (
                        record.get(
                            "purchased_date",
                            "",
                        )
                    )

                    actual_purchase_amount = int(
                        record.get(
                            "actual_purchase_amount",
                            0,
                        )
                    )

                    edit_purchased_date = ""

                    if edit_status == "あとで購入した":
                        edit_purchased_date = str(
                            st.date_input(
                                "購入日",
                                value=(
                                    parse_date(
                                        purchased_date_text
                                    )
                                    or date.today()
                                ),
                                max_value=date.today(),
                                key=(
                                    f"edit_purchased_date_"
                                    f"{record_id}"
                                ),
                            )
                        )

                        actual_purchase_amount = (
                            st.number_input(
                                "実際の購入額",
                                min_value=0,
                                max_value=100000000,
                                value=actual_purchase_amount,
                                key=(
                                    f"edit_purchase_amount_"
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
                                "商品名を入力してください。"
                            )

                        else:
                            update_record(
                                data,
                                record_id,
                                {
                                    "record_date": str(
                                        edit_date
                                    ),
                                    "item_name": (
                                        edit_name.strip()
                                    ),
                                    "amount": (
                                        edit_amount
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "necessity": (
                                        edit_necessity
                                    ),
                                    "reason_type": (
                                        edit_reason_type
                                    ),
                                    "resistance_score": (
                                        edit_resistance
                                    ),
                                    "wanted_reason": (
                                        edit_wanted_reason.strip()
                                    ),
                                    "not_buy_reason": (
                                        edit_not_buy_reason.strip()
                                    ),
                                    "purchased_date": (
                                        edit_purchased_date
                                    ),
                                    "actual_purchase_amount": (
                                        actual_purchase_amount
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                },
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
# 貯金目標
# =========================================================

with goal_tab:
    st.header(
        "🎯 買わなかった貯金の目標"
    )

    with st.form(
        "add_goal_form",
        clear_on_submit=True,
    ):
        goal_columns = st.columns(2)

        with goal_columns[0]:
            goal_name = st.text_input(
                "目標名",
                placeholder=(
                    "例：新しいパソコン"
                ),
            )

            target_amount = (
                st.number_input(
                    "目標金額",
                    min_value=1,
                    max_value=1000000000,
                    value=100000,
                    step=1000,
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
                        "目標期限",
                        value=(
                            date.today()
                            + timedelta(
                                days=180,
                            )
                        ),
                    )
                )

        goal_memo = st.text_area(
            "目標メモ",
            placeholder=(
                "なぜこの目標を達成したいか"
            ),
        )

        goal_submit = (
            st.form_submit_button(
                "目標を追加",
                use_container_width=True,
            )
        )

        if goal_submit:
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
                        "target_amount": (
                            target_amount
                        ),
                        "start_date": str(
                            start_date_input
                        ),
                        "deadline": deadline,
                        "memo": (
                            goal_memo.strip()
                        ),
                    },
                )

                st.rerun()

    st.divider()

    if not goals:
        st.info(
            "貯金目標はまだありません。"
        )

    for goal in goals:
        goal_id = goal["id"]

        progress = goal_progress(
            goal,
            all_savings,
        )

        with st.container(
            border=True,
        ):
            st.subheader(
                goal.get(
                    "name",
                    "",
                )
            )

            columns = st.columns(4)

            columns[0].metric(
                "目標金額",
                f"{goal.get('target_amount', 0):,}円",
            )

            columns[1].metric(
                "現在",
                f"{all_savings:,}円",
            )

            columns[2].metric(
                "達成率",
                f"{progress:.1f}%",
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
                ),
            )

            st.progress(
                progress / 100,
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

                edit_goal_amount = (
                    st.number_input(
                        "目標金額",
                        min_value=1,
                        max_value=1000000000,
                        value=int(
                            goal.get(
                                "target_amount",
                                1,
                            )
                        ),
                        key=(
                            f"edit_goal_amount_"
                            f"{goal_id}"
                        ),
                    )
                )

                edit_goal_active = (
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

                deadline_value = parse_date(
                    goal.get(
                        "deadline",
                        "",
                    )
                )

                edit_has_deadline = (
                    st.checkbox(
                        "期限を設定",
                        value=bool(
                            deadline_value
                        ),
                        key=(
                            f"edit_goal_has_deadline_"
                            f"{goal_id}"
                        ),
                    )
                )

                edit_goal_deadline = ""

                if edit_has_deadline:
                    edit_goal_deadline = str(
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
                                "target_amount": (
                                    edit_goal_amount
                                ),
                                "active": (
                                    edit_goal_active
                                ),
                                "deadline": (
                                    edit_goal_deadline
                                ),
                                "memo": (
                                    edit_goal_memo.strip()
                                ),
                            },
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
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 買わなかった貯金の分析"
    )

    if not records:
        st.info(
            "分析できる記録がありません。"
        )

    else:
        analysis_rows = []

        for record in records:
            record_date = parse_date(
                record.get(
                    "record_date",
                    "",
                )
            )

            analysis_rows.append(
                {
                    "日付": record_date,
                    "月": (
                        record.get(
                            "record_date",
                            "",
                        )[:7]
                    ),
                    "曜日": (
                        record_date.strftime(
                            "%A"
                        )
                        if record_date
                        else ""
                    ),
                    "商品": record.get(
                        "item_name",
                        "",
                    ),
                    "カテゴリー": (
                        record.get(
                            "category",
                            "",
                        )
                    ),
                    "状態": record.get(
                        "status",
                        "",
                    ),
                    "対象金額": int(
                        record.get(
                            "amount",
                            0,
                        )
                    ),
                    "節約額": (
                        effective_saving_amount(
                            record
                        )
                    ),
                    "我慢度": int(
                        record.get(
                            "resistance_score",
                            0,
                        )
                    ),
                    "必要性": (
                        record.get(
                            "necessity",
                            "",
                        )
                    ),
                    "理由": record.get(
                        "reason_type",
                        "",
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows,
        )

        st.subheader(
            "月別節約額"
        )

        monthly_summary = (
            analysis_df.groupby(
                "月",
                as_index=False,
            )
            .agg(
                節約額=(
                    "節約額",
                    "sum",
                ),
                記録数=(
                    "商品",
                    "count",
                ),
            )
            .sort_values(
                "月",
            )
        )

        st.bar_chart(
            monthly_summary.set_index(
                "月",
            )[["節約額"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "カテゴリー別節約額"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .agg(
                節約額=(
                    "節約額",
                    "sum",
                ),
                回数=(
                    "商品",
                    "count",
                ),
            )
            .sort_values(
                "節約額",
                ascending=False,
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー",
            )[["節約額"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "買わなかった理由ランキング"
        )

        reason_summary = (
            analysis_df.groupby(
                "理由",
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
            reason_summary.set_index(
                "理由",
            )[["回数"]]
        )

        st.dataframe(
            reason_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "必要性の分析"
        )

        necessity_summary = (
            analysis_df.groupby(
                "必要性",
                as_index=False,
            )
            .agg(
                回数=(
                    "商品",
                    "count",
                ),
                対象金額=(
                    "対象金額",
                    "sum",
                ),
            )
            .sort_values(
                "回数",
                ascending=False,
            )
        )

        st.bar_chart(
            necessity_summary.set_index(
                "必要性",
            )[["回数"]]
        )

        st.dataframe(
            necessity_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "曜日別の買いたくなりやすさ"
        )

        weekday_names = {
            "Monday": "月曜日",
            "Tuesday": "火曜日",
            "Wednesday": "水曜日",
            "Thursday": "木曜日",
            "Friday": "金曜日",
            "Saturday": "土曜日",
            "Sunday": "日曜日",
        }

        weekday_summary = (
            analysis_df.groupby(
                "曜日",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "回数"
                }
            )
        )

        weekday_summary[
            "曜日"
        ] = weekday_summary[
            "曜日"
        ].map(
            weekday_names,
        )

        weekday_order = [
            "月曜日",
            "火曜日",
            "水曜日",
            "木曜日",
            "金曜日",
            "土曜日",
            "日曜日",
        ]

        weekday_summary[
            "並び順"
        ] = weekday_summary[
            "曜日"
        ].apply(
            lambda value: (
                weekday_order.index(
                    value
                )
                if value
                in weekday_order
                else 99
            )
        )

        weekday_summary = (
            weekday_summary.sort_values(
                "並び順",
            )
            .drop(
                columns=[
                    "並び順"
                ]
            )
        )

        st.bar_chart(
            weekday_summary.set_index(
                "曜日",
            )[["回数"]]
        )

        st.dataframe(
            weekday_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "金額の大きかった記録"
        )

        amount_ranking = (
            analysis_df.sort_values(
                "対象金額",
                ascending=False,
            )[
                [
                    "商品",
                    "カテゴリー",
                    "対象金額",
                    "節約額",
                    "状態",
                ]
            ]
        )

        st.dataframe(
            amount_ranking,
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
            f"no_buy_savings_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = st.file_uploader(
        "バックアップJSONを選択",
        type=[
            "json"
        ],
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file,
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
                        imported_data,
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
        "買わなかった記録と貯金目標がすべて削除されます。"
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
            create_empty_data(),
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
    "我慢した金額ではなく、未来の自分へ残せた金額。💸"
)
