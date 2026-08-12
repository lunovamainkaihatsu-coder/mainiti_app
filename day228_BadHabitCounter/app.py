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
    page_title="やめたい習慣カウンター",
    page_icon="🔥",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "habit_data.json",
)

CATEGORIES = [
    "夜更かし",
    "SNS見すぎ",
    "スマホ見すぎ",
    "無駄遣い",
    "間食",
    "食べすぎ",
    "お酒",
    "ゲームしすぎ",
    "先延ばし",
    "ダラダラ",
    "怒りすぎ",
    "運動不足",
    "その他",
]

RESULTS = [
    "成功",
    "失敗",
    "対象外",
]

RESULT_ICONS = {
    "成功": "✅",
    "失敗": "❌",
    "対象外": "➖",
}

TRIGGERS = [
    "疲れていた",
    "ストレス",
    "暇だった",
    "寝る前",
    "仕事後",
    "SNSを見た",
    "空腹だった",
    "誘惑が近くにあった",
    "予定が崩れた",
    "なんとなく",
    "その他",
]

MOODS = [
    "😩 とても悪い",
    "😕 少し悪い",
    "😐 普通",
    "🙂 少し良い",
    "😊 良い",
]

DIFFICULTIES = [
    "かなり簡単",
    "少し簡単",
    "普通",
    "少し難しい",
    "かなり難しい",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作成する。"""
    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    """空のデータを作成する。"""
    return {
        "habits": [],
        "records": [],
    }


def save_data(data):
    """JSONへ保存する。"""
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
    """古いデータへ不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "habits",
        [],
    )

    data.setdefault(
        "records",
        [],
    )

    for habit in data["habits"]:
        habit.setdefault(
            "id",
            create_id(),
        )

        habit.setdefault(
            "name",
            "",
        )

        habit.setdefault(
            "category",
            "その他",
        )

        habit.setdefault(
            "goal",
            "",
        )

        habit.setdefault(
            "start_date",
            str(date.today()),
        )

        habit.setdefault(
            "reason",
            "",
        )

        habit.setdefault(
            "replacement_action",
            "",
        )

        habit.setdefault(
            "active",
            True,
        )

        habit.setdefault(
            "memo",
            "",
        )

        habit.setdefault(
            "created_at",
            "",
        )

        habit.setdefault(
            "updated_at",
            "",
        )

    for record in data["records"]:
        record.setdefault(
            "id",
            create_id(),
        )

        record.setdefault(
            "habit_id",
            "",
        )

        record.setdefault(
            "record_date",
            str(date.today()),
        )

        record.setdefault(
            "result",
            "成功",
        )

        record.setdefault(
            "trigger",
            "",
        )

        record.setdefault(
            "trigger_detail",
            "",
        )

        record.setdefault(
            "situation",
            "",
        )

        record.setdefault(
            "improvement",
            "",
        )

        record.setdefault(
            "improvement_tried",
            False,
        )

        record.setdefault(
            "improvement_result",
            "",
        )

        record.setdefault(
            "mood",
            "😐 普通",
        )

        record.setdefault(
            "difficulty",
            "普通",
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

    return data


def load_data():
    """JSONから読み込む。"""

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
    """日本語形式の日付表示。"""

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


def get_habit_by_id(
    data,
    habit_id,
):
    """IDから習慣を取得する。"""

    for habit in data["habits"]:
        if habit.get(
            "id"
        ) == habit_id:
            return habit

    return None


def get_record_by_id(
    data,
    record_id,
):
    """IDから記録を取得する。"""

    for record in data["records"]:
        if record.get(
            "id"
        ) == record_id:
            return record

    return None


def get_habit_records(
    records,
    habit_id,
):
    """習慣ごとの記録を取得する。"""

    return [
        record
        for record in records
        if record.get(
            "habit_id"
        ) == habit_id
    ]


def get_record_for_date(
    records,
    habit_id,
    target_date,
):
    """指定日の記録を取得する。"""

    target_text = str(
        target_date
    )

    for record in records:
        if (
            record.get(
                "habit_id"
            )
            == habit_id
            and record.get(
                "record_date"
            )
            == target_text
        ):
            return record

    return None


def success_rate(
    records,
):
    """成功率を計算する。"""

    valid_records = [
        record
        for record in records
        if record.get(
            "result"
        )
        in [
            "成功",
            "失敗",
        ]
    ]

    if not valid_records:
        return 0

    success_count = len(
        [
            record
            for record in valid_records
            if record.get(
                "result"
            )
            == "成功"
        ]
    )

    return (
        success_count
        / len(valid_records)
        * 100
    )


def current_streak(
    records,
):
    """現在の連続成功日数を計算する。"""

    result_map = {
        record.get(
            "record_date"
        ): record.get(
            "result"
        )
        for record in records
        if record.get(
            "record_date"
        )
    }

    if not result_map:
        return 0

    current = date.today()

    # 今日未記録なら昨日から確認
    if str(current) not in result_map:
        current -= timedelta(
            days=1
        )

    streak = 0

    while True:
        result = result_map.get(
            str(current)
        )

        if result == "成功":
            streak += 1

        elif result == "対象外":
            pass

        else:
            break

        current -= timedelta(
            days=1
        )

    return streak


def longest_streak(
    records,
):
    """最長連続成功日数を計算する。"""

    valid_records = [
        record
        for record in records
        if parse_date(
            record.get(
                "record_date",
                ""
            )
        )
    ]

    if not valid_records:
        return 0

    valid_records.sort(
        key=lambda record: (
            record.get(
                "record_date",
                ""
            )
        )
    )

    result_map = {
        record.get(
            "record_date"
        ): record.get(
            "result"
        )
        for record in valid_records
    }

    dates = [
        parse_date(
            record.get(
                "record_date"
            )
        )
        for record in valid_records
    ]

    start = min(dates)
    end = max(dates)

    current = start
    streak = 0
    best = 0

    while current <= end:
        result = result_map.get(
            str(current)
        )

        if result == "成功":
            streak += 1
            best = max(
                best,
                streak,
            )

        elif result == "対象外":
            pass

        else:
            streak = 0

        current += timedelta(
            days=1
        )

    return best


def monthly_result_count(
    records,
    result,
):
    """今月の結果数を返す。"""

    current_month = (
        date.today().strftime(
            "%Y-%m"
        )
    )

    return len(
        [
            record
            for record in records
            if (
                record.get(
                    "record_date",
                    ""
                ).startswith(
                    current_month
                )
                and record.get(
                    "result"
                )
                == result
            )
        ]
    )


# =========================================================
# データ操作
# =========================================================

def add_habit(
    data,
    values,
):
    """習慣を追加する。"""

    habit = {
        "id": create_id(),
        "name": values["name"],
        "category": (
            values["category"]
        ),
        "goal": values["goal"],
        "start_date": (
            values["start_date"]
        ),
        "reason": values["reason"],
        "replacement_action": (
            values[
                "replacement_action"
            ]
        ),
        "active": True,
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["habits"].append(
        habit
    )

    save_data(data)


def update_habit(
    data,
    habit_id,
    values,
):
    """習慣を更新する。"""

    habit = get_habit_by_id(
        data,
        habit_id
    )

    if not habit:
        return

    for key, value in values.items():
        habit[key] = value

    habit["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_habit(
    data,
    habit_id,
):
    """習慣と関連記録を削除する。"""

    data["habits"] = [
        habit
        for habit in data[
            "habits"
        ]
        if habit.get(
            "id"
        ) != habit_id
    ]

    data["records"] = [
        record
        for record in data[
            "records"
        ]
        if record.get(
            "habit_id"
        ) != habit_id
    ]

    save_data(data)


def save_daily_record(
    data,
    values,
):
    """毎日の結果を保存する。"""

    existing = get_record_for_date(
        data["records"],
        values["habit_id"],
        values["record_date"],
    )

    if existing:
        for key, value in values.items():
            if key != "habit_id":
                existing[key] = value

        existing["updated_at"] = (
            now_text()
        )

    else:
        record = {
            "id": create_id(),
            "habit_id": (
                values["habit_id"]
            ),
            "record_date": (
                values["record_date"]
            ),
            "result": (
                values["result"]
            ),
            "trigger": (
                values["trigger"]
            ),
            "trigger_detail": (
                values["trigger_detail"]
            ),
            "situation": (
                values["situation"]
            ),
            "improvement": (
                values["improvement"]
            ),
            "improvement_tried": False,
            "improvement_result": "",
            "mood": (
                values["mood"]
            ),
            "difficulty": (
                values["difficulty"]
            ),
            "memo": (
                values["memo"]
            ),
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
    """記録を更新する。"""

    record = get_record_by_id(
        data,
        record_id
    )

    if not record:
        return

    for key, value in values.items():
        record[key] = value

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
            "id"
        ) != record_id
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
        background: rgba(255, 110, 90, 0.08);
        border: 1px solid rgba(255, 110, 90, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 110, 90, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(255, 110, 90, 0.18),
                rgba(255, 180, 80, 0.12)
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
# 読み込み
# =========================================================

data = load_data()

habits = data[
    "habits"
]

records = data[
    "records"
]

today_text = str(
    date.today()
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🔥 やめたい習慣カウンター</h1>
        <p>
            失敗を責めるのではなく、
            パターンを見つけて少しずつ攻略していくアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

active_habits = [
    habit
    for habit in habits
    if habit.get(
        "active",
        True
    )
]

today_success = 0
today_failure = 0
today_unrecorded = 0

for habit in active_habits:
    record = get_record_for_date(
        records,
        habit["id"],
        date.today(),
    )

    if not record:
        today_unrecorded += 1

    elif record.get(
        "result"
    ) == "成功":
        today_success += 1

    elif record.get(
        "result"
    ) == "失敗":
        today_failure += 1


all_success = len(
    [
        record
        for record in records
        if record.get(
            "result"
        ) == "成功"
    ]
)

all_failure = len(
    [
        record
        for record in records
        if record.get(
            "result"
        ) == "失敗"
    ]
)

trigger_counter = Counter(
    record.get(
        "trigger",
        ""
    )
    for record in records
    if (
        record.get(
            "result"
        )
        == "失敗"
        and record.get(
            "trigger",
            ""
        )
    )
)

top_trigger = (
    trigger_counter.most_common(
        1
    )[0][0]
    if trigger_counter
    else "なし"
)


metric_row1 = st.columns(
    4
)

metric_row1[0].metric(
    "今日成功",
    f"{today_success}個"
)

metric_row1[1].metric(
    "今日失敗",
    f"{today_failure}個"
)

metric_row1[2].metric(
    "今日未記録",
    f"{today_unrecorded}個"
)

metric_row1[3].metric(
    "管理中の習慣",
    f"{len(active_habits)}個"
)


metric_row2 = st.columns(
    4
)

metric_row2[0].metric(
    "累計成功",
    f"{all_success}回"
)

metric_row2[1].metric(
    "累計失敗",
    f"{all_failure}回"
)

metric_row2[2].metric(
    "全体成功率",
    f"{success_rate(records):.1f}%"
)

metric_row2[3].metric(
    "最多失敗トリガー",
    top_trigger
)


# =========================================================
# 今日のチェック
# =========================================================

st.divider()

st.header(
    "📅 今日のチェック"
)

if not active_habits:
    st.info(
        "まずは「習慣管理」から、やめたい習慣を登録しよう。"
    )

else:
    for habit in active_habits:
        habit_id = habit[
            "id"
        ]

        habit_records = (
            get_habit_records(
                records,
                habit_id,
            )
        )

        today_record = (
            get_record_for_date(
                records,
                habit_id,
                date.today(),
            )
        )

        with st.container(
            border=True
        ):
            title_column, streak_column = (
                st.columns(
                    [
                        4,
                        1,
                    ]
                )
            )

            with title_column:
                st.markdown(
                    f"### 🔥 "
                    f"{habit.get('name', '')}"
                )

                st.caption(
                    habit.get(
                        "category",
                        ""
                    )
                )

                if habit.get(
                    "goal",
                    ""
                ):
                    st.write(
                        f"目標："
                        f"**{habit.get('goal', '')}**"
                    )

            with streak_column:
                st.metric(
                    "連続成功",
                    f"{current_streak(habit_records)}日"
                )

            if today_record:
                result = today_record.get(
                    "result",
                    ""
                )

                if result == "成功":
                    st.success(
                        "✅ 今日は成功！"
                    )

                elif result == "失敗":
                    st.error(
                        "❌ 今日は失敗として記録されています。"
                    )

                else:
                    st.info(
                        "➖ 今日は対象外です。"
                    )

            with st.expander(
                "今日の結果を記録",
                expanded=(
                    today_record
                    is None
                )
            ):
                default_result = (
                    today_record.get(
                        "result",
                        "成功"
                    )
                    if today_record
                    else "成功"
                )

                result = st.radio(
                    "今日どうだった？",
                    RESULTS,
                    index=(
                        RESULTS.index(
                            default_result
                        )
                        if default_result
                        in RESULTS
                        else 0
                    ),
                    format_func=lambda value: (
                        f"{RESULT_ICONS.get(value, '')} "
                        f"{value}"
                    ),
                    key=(
                        f"today_result_"
                        f"{habit_id}"
                    )
                )

                mood = st.selectbox(
                    "今日の気分",
                    MOODS,
                    index=(
                        MOODS.index(
                            today_record.get(
                                "mood",
                                "😐 普通"
                            )
                        )
                        if (
                            today_record
                            and today_record.get(
                                "mood"
                            )
                            in MOODS
                        )
                        else 2
                    ),
                    key=(
                        f"today_mood_"
                        f"{habit_id}"
                    )
                )

                difficulty = st.selectbox(
                    "今日はどれくらい難しかった？",
                    DIFFICULTIES,
                    index=(
                        DIFFICULTIES.index(
                            today_record.get(
                                "difficulty",
                                "普通"
                            )
                        )
                        if (
                            today_record
                            and today_record.get(
                                "difficulty"
                            )
                            in DIFFICULTIES
                        )
                        else 2
                    ),
                    key=(
                        f"today_difficulty_"
                        f"{habit_id}"
                    )
                )

                trigger = ""
                trigger_detail = ""
                situation = ""
                improvement = ""

                if result == "失敗":
                    trigger = st.selectbox(
                        "失敗したきっかけ",
                        TRIGGERS,
                        index=(
                            TRIGGERS.index(
                                today_record.get(
                                    "trigger",
                                    "その他"
                                )
                            )
                            if (
                                today_record
                                and today_record.get(
                                    "trigger"
                                )
                                in TRIGGERS
                            )
                            else 0
                        ),
                        key=(
                            f"today_trigger_"
                            f"{habit_id}"
                        )
                    )

                    trigger_detail = (
                        st.text_area(
                            "具体的に何があった？",
                            value=(
                                today_record.get(
                                    "trigger_detail",
                                    ""
                                )
                                if today_record
                                else ""
                            ),
                            placeholder=(
                                "例：YouTubeを1本だけ見るつもりだった"
                            ),
                            key=(
                                f"today_trigger_detail_"
                                f"{habit_id}"
                            )
                        )
                    )

                    situation = (
                        st.text_area(
                            "そのときの状況",
                            value=(
                                today_record.get(
                                    "situation",
                                    ""
                                )
                                if today_record
                                else ""
                            ),
                            placeholder=(
                                "例：寝る前、疲れていた"
                            ),
                            key=(
                                f"today_situation_"
                                f"{habit_id}"
                            )
                        )
                    )

                    improvement = (
                        st.text_area(
                            "次回どうする？",
                            value=(
                                today_record.get(
                                    "improvement",
                                    ""
                                )
                                if today_record
                                else ""
                            ),
                            placeholder=(
                                "例：スマホを寝室に持ち込まない"
                            ),
                            key=(
                                f"today_improvement_"
                                f"{habit_id}"
                            )
                        )
                    )

                memo = st.text_area(
                    "ひとことメモ",
                    value=(
                        today_record.get(
                            "memo",
                            ""
                        )
                        if today_record
                        else ""
                    ),
                    key=(
                        f"today_memo_"
                        f"{habit_id}"
                    )
                )

                if st.button(
                    "今日の結果を保存",
                    key=(
                        f"save_today_"
                        f"{habit_id}"
                    ),
                    use_container_width=True,
                ):
                    save_daily_record(
                        data,
                        {
                            "habit_id": (
                                habit_id
                            ),
                            "record_date": (
                                today_text
                            ),
                            "result": result,
                            "trigger": trigger,
                            "trigger_detail": (
                                trigger_detail.strip()
                            ),
                            "situation": (
                                situation.strip()
                            ),
                            "improvement": (
                                improvement.strip()
                            ),
                            "mood": mood,
                            "difficulty": (
                                difficulty
                            ),
                            "memo": (
                                memo.strip()
                            ),
                        }
                    )

                    st.success(
                        "今日の結果を記録しました！"
                    )

                    st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    habit_tab,
    history_tab,
    improvement_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "📝 習慣管理",
        "📚 記録履歴",
        "🛠️ 改善策",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 習慣管理
# =========================================================

with habit_tab:
    st.header(
        "📝 やめたい習慣を登録"
    )

    with st.form(
        "add_habit_form",
        clear_on_submit=True,
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            habit_name = st.text_input(
                "やめたい習慣",
                placeholder=(
                    "例：寝る前にスマホを見る"
                ),
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            start_date_input = (
                st.date_input(
                    "開始日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

        with column2:
            goal = st.text_input(
                "具体的な目標",
                placeholder=(
                    "例：23時以降はスマホを触らない"
                ),
            )

            reason = st.text_area(
                "なぜ減らしたい？",
                placeholder=(
                    "例：睡眠時間を増やしたい"
                ),
                height=100,
            )

        replacement_action = (
            st.text_area(
                "代わりに何をする？",
                placeholder=(
                    "例：寝る前は本を10分読む"
                ),
                height=90,
            )
        )

        habit_memo = st.text_area(
            "メモ",
            placeholder=(
                "ルールや気をつけたいこと"
            ),
            height=80,
        )

        submitted = (
            st.form_submit_button(
                "🔥 習慣を登録",
                use_container_width=True,
            )
        )

        if submitted:
            if not habit_name.strip():
                st.error(
                    "やめたい習慣を入力してください。"
                )

            else:
                add_habit(
                    data,
                    {
                        "name": (
                            habit_name.strip()
                        ),
                        "category": (
                            category
                        ),
                        "goal": (
                            goal.strip()
                        ),
                        "start_date": str(
                            start_date_input
                        ),
                        "reason": (
                            reason.strip()
                        ),
                        "replacement_action": (
                            replacement_action.strip()
                        ),
                        "memo": (
                            habit_memo.strip()
                        ),
                    }
                )

                st.success(
                    "習慣を登録しました！"
                )

                st.rerun()

    st.divider()

    if not habits:
        st.info(
            "登録されている習慣はありません。"
        )

    for habit in habits:
        habit_id = habit[
            "id"
        ]

        habit_records = (
            get_habit_records(
                records,
                habit_id,
            )
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{'🔥' if habit.get('active', True) else '⏸️'} "
                f"{habit.get('name', '')}"
            )

            st.caption(
                f"{habit.get('category', '')} ／ "
                f"開始：{format_date(habit.get('start_date', ''))}"
            )

            stats = st.columns(
                4
            )

            stats[0].metric(
                "成功率",
                f"{success_rate(habit_records):.1f}%"
            )

            stats[1].metric(
                "現在の連続",
                f"{current_streak(habit_records)}日"
            )

            stats[2].metric(
                "最長連続",
                f"{longest_streak(habit_records)}日"
            )

            stats[3].metric(
                "記録数",
                f"{len(habit_records)}日"
            )

            if habit.get(
                "goal",
                ""
            ):
                st.success(
                    f"🎯 {habit.get('goal', '')}"
                )

            if habit.get(
                "replacement_action",
                ""
            ):
                st.info(
                    "代わりにやること\n\n"
                    + habit.get(
                        "replacement_action",
                        ""
                    )
                )

            with st.expander(
                "✏️ 習慣を編集"
            ):
                edit_name = st.text_input(
                    "習慣名",
                    value=habit.get(
                        "name",
                        "",
                    ),
                    key=(
                        f"edit_habit_name_"
                        f"{habit_id}"
                    ),
                )

                current_category = (
                    habit.get(
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
                            f"edit_habit_category_"
                            f"{habit_id}"
                        ),
                    )
                )

                edit_goal = st.text_input(
                    "目標",
                    value=habit.get(
                        "goal",
                        "",
                    ),
                    key=(
                        f"edit_goal_"
                        f"{habit_id}"
                    ),
                )

                edit_reason = st.text_area(
                    "減らしたい理由",
                    value=habit.get(
                        "reason",
                        "",
                    ),
                    key=(
                        f"edit_reason_"
                        f"{habit_id}"
                    ),
                )

                edit_replacement = (
                    st.text_area(
                        "代わりにやること",
                        value=habit.get(
                            "replacement_action",
                            "",
                        ),
                        key=(
                            f"edit_replacement_"
                            f"{habit_id}"
                        ),
                    )
                )

                edit_active = st.checkbox(
                    "この習慣を管理中にする",
                    value=bool(
                        habit.get(
                            "active",
                            True
                        )
                    ),
                    key=(
                        f"edit_active_"
                        f"{habit_id}"
                    ),
                )

                edit_memo = st.text_area(
                    "メモ",
                    value=habit.get(
                        "memo",
                        "",
                    ),
                    key=(
                        f"edit_habit_memo_"
                        f"{habit_id}"
                    ),
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_habit_"
                        f"{habit_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.error(
                            "習慣名を入力してください。"
                        )

                    else:
                        update_habit(
                            data,
                            habit_id,
                            {
                                "name": (
                                    edit_name.strip()
                                ),
                                "category": (
                                    edit_category
                                ),
                                "goal": (
                                    edit_goal.strip()
                                ),
                                "reason": (
                                    edit_reason.strip()
                                ),
                                "replacement_action": (
                                    edit_replacement.strip()
                                ),
                                "active": (
                                    edit_active
                                ),
                                "memo": (
                                    edit_memo.strip()
                                ),
                            }
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 習慣を削除"
            ):
                st.warning(
                    "この習慣の毎日の記録も削除されます。"
                )

                confirm_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_habit_delete_"
                            f"{habit_id}"
                        ),
                    )
                )

                if st.button(
                    "この習慣を削除",
                    key=(
                        f"delete_habit_"
                        f"{habit_id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True,
                ):
                    delete_habit(
                        data,
                        habit_id
                    )

                    st.rerun()


# =========================================================
# 記録履歴
# =========================================================

with history_tab:
    st.header(
        "📚 毎日の記録"
    )

    if not records:
        st.info(
            "記録はまだありません。"
        )

    else:
        habit_options = {
            "すべて": ""
        }

        for habit in habits:
            habit_options[
                habit.get(
                    "name",
                    ""
                )
            ] = habit[
                "id"
            ]

        filter_columns = (
            st.columns(2)
        )

        with filter_columns[0]:
            selected_habit_name = (
                st.selectbox(
                    "習慣",
                    list(
                        habit_options.keys()
                    ),
                )
            )

        with filter_columns[1]:
            result_filter = (
                st.selectbox(
                    "結果",
                    [
                        "すべて"
                    ]
                    + RESULTS,
                )
            )

        selected_habit_id = (
            habit_options[
                selected_habit_name
            ]
        )

        filtered_records = list(
            records
        )

        if selected_habit_id:
            filtered_records = [
                record
                for record
                in filtered_records
                if record.get(
                    "habit_id"
                )
                == selected_habit_id
            ]

        if result_filter != "すべて":
            filtered_records = [
                record
                for record
                in filtered_records
                if record.get(
                    "result"
                )
                == result_filter
            ]

        filtered_records.sort(
            key=lambda record: (
                record.get(
                    "record_date",
                    ""
                )
            ),
            reverse=True,
        )

        st.write(
            f"表示件数："
            f"**{len(filtered_records)}件**"
        )

        for record in filtered_records:
            record_id = record[
                "id"
            ]

            habit = get_habit_by_id(
                data,
                record.get(
                    "habit_id",
                    ""
                ),
            )

            with st.container(
                border=True
            ):
                result = record.get(
                    "result",
                    "",
                )

                st.markdown(
                    f"### "
                    f"{RESULT_ICONS.get(result, '')} "
                    f"{habit.get('name', '不明な習慣') if habit else '不明な習慣'}"
                )

                st.caption(
                    format_date(
                        record.get(
                            "record_date",
                            ""
                        )
                    )
                )

                columns = st.columns(
                    3
                )

                columns[0].metric(
                    "結果",
                    result
                )

                columns[1].metric(
                    "気分",
                    record.get(
                        "mood",
                        ""
                    )
                )

                columns[2].metric(
                    "難易度",
                    record.get(
                        "difficulty",
                        ""
                    )
                )

                if result == "失敗":
                    st.error(
                        f"失敗トリガー："
                        f"{record.get('trigger', '')}"
                    )

                    if record.get(
                        "trigger_detail",
                        ""
                    ):
                        st.write(
                            "**何があった？**"
                        )

                        st.write(
                            record.get(
                                "trigger_detail",
                                ""
                            )
                        )

                    if record.get(
                        "situation",
                        ""
                    ):
                        st.write(
                            "**状況**"
                        )

                        st.write(
                            record.get(
                                "situation",
                                ""
                            )
                        )

                    if record.get(
                        "improvement",
                        ""
                    ):
                        st.success(
                            "次回の改善策\n\n"
                            + record.get(
                                "improvement",
                                ""
                            )
                        )

                if record.get(
                    "memo",
                    ""
                ):
                    st.info(
                        record.get(
                            "memo",
                            ""
                        )
                    )

                with st.expander(
                    "🗑️ 記録を削除"
                ):
                    confirm_record_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_record_delete_"
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
                            not confirm_record_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_record(
                            data,
                            record_id
                        )

                        st.rerun()


# =========================================================
# 改善策
# =========================================================

with improvement_tab:
    st.header(
        "🛠️ 失敗から作った改善策"
    )

    improvement_records = [
        record
        for record in records
        if (
            record.get(
                "result"
            )
            == "失敗"
            and record.get(
                "improvement",
                ""
            ).strip()
        )
    ]

    if not improvement_records:
        st.info(
            "改善策はまだありません。失敗した日に「次回どうする？」を記録すると表示されます。"
        )

    else:
        improvement_records.sort(
            key=lambda record: (
                record.get(
                    "record_date",
                    ""
                )
            ),
            reverse=True,
        )

        for record in improvement_records:
            record_id = record[
                "id"
            ]

            habit = get_habit_by_id(
                data,
                record.get(
                    "habit_id",
                    ""
                ),
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### 🛠️ "
                    f"{habit.get('name', '') if habit else '不明な習慣'}"
                )

                st.caption(
                    format_date(
                        record.get(
                            "record_date",
                            ""
                        )
                    )
                )

                st.write(
                    f"失敗原因："
                    f"**{record.get('trigger', '')}**"
                )

                st.success(
                    record.get(
                        "improvement",
                        ""
                    )
                )

                tried = st.checkbox(
                    "この改善策を試した",
                    value=bool(
                        record.get(
                            "improvement_tried",
                            False,
                        )
                    ),
                    key=(
                        f"improvement_tried_"
                        f"{record_id}"
                    ),
                )

                improvement_result = (
                    st.text_area(
                        "試した結果",
                        value=record.get(
                            "improvement_result",
                            ""
                        ),
                        placeholder=(
                            "例：寝室にスマホを持ち込まなかったら成功した"
                        ),
                        key=(
                            f"improvement_result_"
                            f"{record_id}"
                        ),
                    )
                )

                if st.button(
                    "改善結果を保存",
                    key=(
                        f"save_improvement_"
                        f"{record_id}"
                    ),
                    use_container_width=True,
                ):
                    update_record(
                        data,
                        record_id,
                        {
                            "improvement_tried": (
                                tried
                            ),
                            "improvement_result": (
                                improvement_result.strip()
                            ),
                        }
                    )

                    st.success(
                        "改善結果を保存しました！"
                    )

                    st.rerun()


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 習慣分析"
    )

    if not records:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for record in records:
            habit = get_habit_by_id(
                data,
                record.get(
                    "habit_id",
                    ""
                ),
            )

            record_date = parse_date(
                record.get(
                    "record_date",
                    ""
                )
            )

            analysis_rows.append(
                {
                    "日付": (
                        record.get(
                            "record_date",
                            ""
                        )
                    ),
                    "月": (
                        record.get(
                            "record_date",
                            ""
                        )[:7]
                    ),
                    "曜日": (
                        record_date.strftime(
                            "%A"
                        )
                        if record_date
                        else ""
                    ),
                    "習慣": (
                        habit.get(
                            "name",
                            ""
                        )
                        if habit
                        else "不明"
                    ),
                    "カテゴリー": (
                        habit.get(
                            "category",
                            ""
                        )
                        if habit
                        else "不明"
                    ),
                    "結果": (
                        record.get(
                            "result",
                            ""
                        )
                    ),
                    "トリガー": (
                        record.get(
                            "trigger",
                            ""
                        )
                    ),
                    "気分": (
                        record.get(
                            "mood",
                            ""
                        )
                    ),
                    "難易度": (
                        record.get(
                            "difficulty",
                            ""
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "月別成功・失敗"
        )

        monthly_df = analysis_df[
            analysis_df[
                "結果"
            ]
            .isin(
                [
                    "成功",
                    "失敗",
                ]
            )
        ]

        if not monthly_df.empty:
            monthly_summary = (
                monthly_df.groupby(
                    [
                        "月",
                        "結果",
                    ]
                )
                .size()
                .unstack(
                    fill_value=0
                )
                .sort_index()
            )

            st.bar_chart(
                monthly_summary
            )

            st.dataframe(
                monthly_summary,
                use_container_width=True,
            )

        st.divider()

        st.subheader(
            "習慣別成功率"
        )

        habit_rows = []

        for habit in habits:
            habit_records = (
                get_habit_records(
                    records,
                    habit["id"],
                )
            )

            habit_rows.append(
                {
                    "習慣": (
                        habit.get(
                            "name",
                            ""
                        )
                    ),
                    "カテゴリー": (
                        habit.get(
                            "category",
                            ""
                        )
                    ),
                    "成功率": round(
                        success_rate(
                            habit_records
                        ),
                        1,
                    ),
                    "現在の連続成功": (
                        current_streak(
                            habit_records
                        )
                    ),
                    "最長連続成功": (
                        longest_streak(
                            habit_records
                        )
                    ),
                    "成功": len(
                        [
                            record
                            for record
                            in habit_records
                            if record.get(
                                "result"
                            )
                            == "成功"
                        ]
                    ),
                    "失敗": len(
                        [
                            record
                            for record
                            in habit_records
                            if record.get(
                                "result"
                            )
                            == "失敗"
                        ]
                    ),
                }
            )

        habit_df = pd.DataFrame(
            habit_rows
        )

        if not habit_df.empty:
            habit_df = (
                habit_df.sort_values(
                    "成功率",
                    ascending=False,
                )
            )

            st.bar_chart(
                habit_df.set_index(
                    "習慣"
                )[["成功率"]]
            )

            st.dataframe(
                habit_df,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "失敗トリガーランキング"
        )

        failure_df = analysis_df[
            analysis_df[
                "結果"
            ]
            == "失敗"
        ]

        failure_trigger_df = (
            failure_df[
                failure_df[
                    "トリガー"
                ]
                != ""
            ]
        )

        if failure_trigger_df.empty:
            st.success(
                "失敗トリガーの記録はまだありません。"
            )

        else:
            trigger_summary = (
                failure_trigger_df.groupby(
                    "トリガー",
                    as_index=False,
                )
                .size()
                .rename(
                    columns={
                        "size": "失敗回数"
                    }
                )
                .sort_values(
                    "失敗回数",
                    ascending=False,
                )
            )

            st.bar_chart(
                trigger_summary.set_index(
                    "トリガー"
                )[["失敗回数"]]
            )

            st.dataframe(
                trigger_summary,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "曜日別の失敗"
        )

        if failure_df.empty:
            st.info(
                "失敗記録はありません。"
            )

        else:
            weekday_names = {
                "Monday": "月曜日",
                "Tuesday": "火曜日",
                "Wednesday": "水曜日",
                "Thursday": "木曜日",
                "Friday": "金曜日",
                "Saturday": "土曜日",
                "Sunday": "日曜日",
            }

            weekday_order = [
                "月曜日",
                "火曜日",
                "水曜日",
                "木曜日",
                "金曜日",
                "土曜日",
                "日曜日",
            ]

            weekday_summary = (
                failure_df.groupby(
                    "曜日",
                    as_index=False,
                )
                .size()
                .rename(
                    columns={
                        "size": "失敗回数"
                    }
                )
            )

            weekday_summary[
                "曜日"
            ] = weekday_summary[
                "曜日"
            ].map(
                weekday_names
            )

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
                    "並び順"
                )
                .drop(
                    columns=[
                        "並び順"
                    ]
                )
            )

            st.bar_chart(
                weekday_summary.set_index(
                    "曜日"
                )[["失敗回数"]]
            )

            st.dataframe(
                weekday_summary,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "改善策の実践状況"
        )

        improvement_records = [
            record
            for record in records
            if record.get(
                "improvement",
                ""
            ).strip()
        ]

        tried_improvements = [
            record
            for record
            in improvement_records
            if record.get(
                "improvement_tried",
                False,
            )
        ]

        improvement_columns = (
            st.columns(3)
        )

        improvement_columns[0].metric(
            "改善策",
            f"{len(improvement_records)}件"
        )

        improvement_columns[1].metric(
            "試した",
            f"{len(tried_improvements)}件"
        )

        improvement_columns[2].metric(
            "実践率",
            (
                f"{len(tried_improvements) / len(improvement_records) * 100:.1f}%"
                if improvement_records
                else "0.0%"
            )
        )

        if tried_improvements:
            improvement_rows = []

            for record in tried_improvements:
                habit = get_habit_by_id(
                    data,
                    record.get(
                        "habit_id",
                        ""
                    ),
                )

                improvement_rows.append(
                    {
                        "習慣": (
                            habit.get(
                                "name",
                                ""
                            )
                            if habit
                            else "不明"
                        ),
                        "原因": (
                            record.get(
                                "trigger",
                                ""
                            )
                        ),
                        "改善策": (
                            record.get(
                                "improvement",
                                ""
                            )
                        ),
                        "結果": (
                            record.get(
                                "improvement_result",
                                ""
                            )
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    improvement_rows
                ),
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
            f"bad_habit_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONから復元"
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
                or "habits"
                not in imported_data
                or "records"
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
        "習慣・毎日の記録・改善策がすべて削除されます。"
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
    "連続記録が途切れても大丈夫。成功率が少しずつ上がれば、それも立派な前進。🔥"
)
