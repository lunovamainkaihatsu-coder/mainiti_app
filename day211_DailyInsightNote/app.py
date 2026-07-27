import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =====================================
# ページ設定
# =====================================

st.set_page_config(
    page_title="今日の気づきノート",
    page_icon="💡",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "insight_data.json"
)


MOODS = [
    "とても良い",
    "良い",
    "普通",
    "少し疲れた",
    "つらい"
]


MOOD_ICONS = {
    "とても良い": "😄",
    "良い": "😊",
    "普通": "😐",
    "少し疲れた": "😮‍💨",
    "つらい": "😢"
}


MOOD_SCORES = {
    "とても良い": 5,
    "良い": 4,
    "普通": 3,
    "少し疲れた": 2,
    "つらい": 1
}


DEFAULT_TAGS = [
    "LuNova",
    "仕事",
    "家族",
    "筋トレ",
    "健康",
    "学び",
    "人間関係",
    "メンタル",
    "趣味",
    "生活"
]


# =====================================
# データ保存・読み込み
# =====================================

def create_empty_data():
    """空の初期データを作成する。"""

    return {
        "records": []
    }


def save_data(data):
    """JSONファイルへデータを保存する。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "保存データの形式が正しくありません。"
            )

        data.setdefault(
            "records",
            []
        )

        for record in data["records"]:
            record.setdefault(
                "record_date",
                str(date.today())
            )

            record.setdefault(
                "mood",
                "普通"
            )

            record.setdefault(
                "insight",
                ""
            )

            record.setdefault(
                "success",
                ""
            )

            record.setdefault(
                "reflection",
                ""
            )

            record.setdefault(
                "tomorrow_action",
                ""
            )

            record.setdefault(
                "tags",
                []
            )

            record.setdefault(
                "memo",
                ""
            )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data


# =====================================
# 補助関数
# =====================================

def create_id():
    """一意のIDを生成する。"""

    return str(
        uuid.uuid4()
    )


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date_text(
    date_text
):
    """日付文字列をdate型へ変換する。"""

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except (
        ValueError,
        TypeError
    ):
        return None


def format_date(
    date_text
):
    """日付を日本語表示へ変換する。"""

    parsed_date = parse_date_text(
        date_text
    )

    if not parsed_date:
        return "日付不明"

    weekday_names = [
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日"
    ]

    weekday = weekday_names[
        parsed_date.weekday()
    ]

    return parsed_date.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_record_by_id(
    data,
    record_id
):
    """IDから記録を取得する。"""

    for record in data["records"]:
        if record.get(
            "id"
        ) == record_id:
            return record

    return None


def get_record_by_date(
    data,
    target_date
):
    """指定日の記録を取得する。"""

    target_text = str(
        target_date
    )

    for record in data["records"]:
        if record.get(
            "record_date"
        ) == target_text:
            return record

    return None


def calculate_streak(
    records
):
    """今日または昨日から続く連続記録日数を計算する。"""

    if not records:
        return 0

    recorded_dates = {
        parse_date_text(
            record.get(
                "record_date",
                ""
            )
        )
        for record in records
    }

    recorded_dates.discard(
        None
    )

    if not recorded_dates:
        return 0

    current_date = date.today()

    if current_date not in recorded_dates:
        yesterday = (
            current_date
            - timedelta(
                days=1
            )
        )

        if yesterday not in recorded_dates:
            return 0

        current_date = yesterday

    streak = 0

    while current_date in recorded_dates:
        streak += 1
        current_date -= timedelta(
            days=1
        )

    return streak


def get_average_mood(
    records
):
    """平均気分を取得する。"""

    if not records:
        return None

    scores = [
        MOOD_SCORES.get(
            record.get(
                "mood",
                "普通"
            ),
            3
        )
        for record in records
    ]

    average_score = (
        sum(scores)
        / len(scores)
    )

    nearest_score = round(
        average_score
    )

    for mood, score in MOOD_SCORES.items():
        if score == nearest_score:
            return mood

    return "普通"


def get_all_tags(
    records
):
    """登録済みタグをすべて取得する。"""

    tags = set(
        DEFAULT_TAGS
    )

    for record in records:
        for tag in record.get(
            "tags",
            []
        ):
            if tag:
                tags.add(
                    tag
                )

    return sorted(
        tags
    )


# =====================================
# データ操作
# =====================================

def add_record(
    data,
    record_date,
    mood,
    insight,
    success,
    reflection,
    tomorrow_action,
    tags,
    memo
):
    """新しい記録を追加する。"""

    record = {
        "id": create_id(),
        "record_date": str(
            record_date
        ),
        "mood": mood,
        "insight": insight,
        "success": success,
        "reflection": reflection,
        "tomorrow_action": tomorrow_action,
        "tags": tags,
        "memo": memo,
        "created_at": now_text(),
        "updated_at": ""
    }

    data["records"].append(
        record
    )

    save_data(data)


def update_record(
    data,
    record_id,
    record_date,
    mood,
    insight,
    success,
    reflection,
    tomorrow_action,
    tags,
    memo
):
    """記録を更新する。"""

    record = get_record_by_id(
        data,
        record_id
    )

    if not record:
        return

    record["record_date"] = str(
        record_date
    )
    record["mood"] = mood
    record["insight"] = insight
    record["success"] = success
    record["reflection"] = reflection
    record["tomorrow_action"] = (
        tomorrow_action
    )
    record["tags"] = tags
    record["memo"] = memo
    record["updated_at"] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id
):
    """記録を削除する。"""

    data["records"] = [
        record
        for record in data["records"]
        if record.get(
            "id"
        ) != record_id
    ]

    save_data(data)


# =====================================
# データ読み込み
# =====================================

data = load_data()

records = data["records"]

all_tags = get_all_tags(
    records
)


# =====================================
# タイトル
# =====================================

st.title(
    "💡 今日の気づきノート"
)

st.caption(
    "毎日の学びや小さな変化を記録して、"
    "自分の成長を積み重ねるノートです。"
)


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header(
    "📊 ダッシュボード"
)

today = date.today()

this_month_records = [
    record
    for record in records
    if (
        parse_date_text(
            record.get(
                "record_date",
                ""
            )
        )
        and parse_date_text(
            record.get(
                "record_date",
                ""
            )
        ).year
        == today.year
        and parse_date_text(
            record.get(
                "record_date",
                ""
            )
        ).month
        == today.month
    )
]

streak_count = calculate_streak(
    records
)

average_mood = get_average_mood(
    this_month_records
)

tag_counter = Counter()

for record in records:
    tag_counter.update(
        record.get(
            "tags",
            []
        )
    )

most_common_tag = (
    tag_counter.most_common(1)[0][0]
    if tag_counter
    else "なし"
)


metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = (
    st.columns(5)
)

with metric_col1:
    st.metric(
        "総記録数",
        f"{len(records)}件"
    )

with metric_col2:
    st.metric(
        "連続記録",
        f"{streak_count}日"
    )

with metric_col3:
    st.metric(
        "今月の記録",
        f"{len(this_month_records)}件"
    )

with metric_col4:
    st.metric(
        "今月の平均気分",
        (
            f"{MOOD_ICONS.get(average_mood, '')} "
            f"{average_mood}"
            if average_mood
            else "未記録"
        )
    )

with metric_col5:
    st.metric(
        "よく使うタグ",
        most_common_tag
    )


today_record = get_record_by_date(
    data,
    today
)

if today_record:
    st.success(
        "今日はすでに振り返りを記録しています！✨"
    )

else:
    st.info(
        "今日の気づきを、ひとことだけでも残してみましょう。"
    )


# =====================================
# 過去の気づき
# =====================================

insight_records = [
    record
    for record in records
    if record.get(
        "insight",
        ""
    ).strip()
]

if insight_records:
    st.divider()

    st.header(
        "🎲 過去の気づきを振り返る"
    )

    if (
        "random_insight_id"
        not in st.session_state
    ):
        st.session_state[
            "random_insight_id"
        ] = random.choice(
            insight_records
        ).get(
            "id"
        )

    random_record = get_record_by_id(
        data,
        st.session_state[
            "random_insight_id"
        ]
    )

    if random_record:
        with st.container(
            border=True
        ):
            st.subheader(
                f"{MOOD_ICONS.get(random_record.get('mood', ''), '')} "
                f"{format_date(random_record.get('record_date', ''))}"
            )

            st.info(
                random_record.get(
                    "insight",
                    ""
                )
            )

            if random_record.get(
                "tags",
                []
            ):
                st.caption(
                    "タグ："
                    + " / ".join(
                        random_record.get(
                            "tags",
                            []
                        )
                    )
                )

    if st.button(
        "🔄 別の気づきを表示"
    ):
        st.session_state[
            "random_insight_id"
        ] = random.choice(
            insight_records
        ).get(
            "id"
        )

        st.rerun()


# =====================================
# タブ
# =====================================

st.divider()

record_tab, history_tab, calendar_tab, analysis_tab = (
    st.tabs(
        [
            "✍️ 今日の記録",
            "📚 過去の記録",
            "📅 月別表示",
            "📈 振り返り分析"
        ]
    )
)


# =====================================
# 今日の記録
# =====================================

with record_tab:
    st.header(
        "✍️ 今日の振り返り"
    )

    selected_date = st.date_input(
        "記録日",
        value=date.today(),
        max_value=date.today()
    )

    existing_record = get_record_by_date(
        data,
        selected_date
    )

    if existing_record:
        st.warning(
            "この日付の記録はすでに存在します。"
            "下の編集画面から更新できます。"
        )

        record_id = existing_record.get(
            "id",
            ""
        )

        current_mood = existing_record.get(
            "mood",
            "普通"
        )

        mood_index = (
            MOODS.index(
                current_mood
            )
            if current_mood in MOODS
            else 2
        )

        with st.form(
            f"edit_today_record_{record_id}"
        ):
            mood = st.selectbox(
                "今日の気分",
                MOODS,
                index=mood_index
            )

            insight = st.text_area(
                "💡 今日の気づき",
                value=existing_record.get(
                    "insight",
                    ""
                ),
                placeholder=(
                    "今日、気づいたことや学んだこと"
                ),
                height=120
            )

            success = st.text_area(
                "🌟 今日うまくいったこと",
                value=existing_record.get(
                    "success",
                    ""
                ),
                placeholder=(
                    "小さな成功でも大丈夫です"
                ),
                height=100
            )

            reflection = st.text_area(
                "🔍 今日の反省",
                value=existing_record.get(
                    "reflection",
                    ""
                ),
                placeholder=(
                    "改善したいことや次に生かしたいこと"
                ),
                height=100
            )

            tomorrow_action = st.text_area(
                "➡️ 明日試したいこと",
                value=existing_record.get(
                    "tomorrow_action",
                    ""
                ),
                placeholder=(
                    "明日できる小さな行動"
                ),
                height=100
            )

            tags = st.multiselect(
                "🏷️ タグ",
                all_tags,
                default=existing_record.get(
                    "tags",
                    []
                )
            )

            custom_tags_text = st.text_input(
                "新しいタグ",
                placeholder=(
                    "複数ある場合はカンマ区切り"
                )
            )

            memo = st.text_area(
                "📝 自由メモ",
                value=existing_record.get(
                    "memo",
                    ""
                ),
                height=100
            )

            update_submit = (
                st.form_submit_button(
                    "💾 記録を更新",
                    use_container_width=True
                )
            )

            if update_submit:
                custom_tags = [
                    tag.strip()
                    for tag in custom_tags_text.split(
                        ","
                    )
                    if tag.strip()
                ]

                final_tags = list(
                    dict.fromkeys(
                        tags + custom_tags
                    )
                )

                if not any(
                    [
                        insight.strip(),
                        success.strip(),
                        reflection.strip(),
                        tomorrow_action.strip(),
                        memo.strip()
                    ]
                ):
                    st.error(
                        "振り返り内容を一つ以上入力してください。"
                    )

                else:
                    update_record(
                        data=data,
                        record_id=record_id,
                        record_date=selected_date,
                        mood=mood,
                        insight=insight.strip(),
                        success=success.strip(),
                        reflection=reflection.strip(),
                        tomorrow_action=(
                            tomorrow_action.strip()
                        ),
                        tags=final_tags,
                        memo=memo.strip()
                    )

                    st.success(
                        "記録を更新しました！"
                    )

                    st.rerun()

    else:
        with st.form(
            "add_record_form",
            clear_on_submit=True
        ):
            mood = st.selectbox(
                "今日の気分",
                MOODS,
                index=2
            )

            insight = st.text_area(
                "💡 今日の気づき",
                placeholder=(
                    "例：少しでも手を動かすと、"
                    "気持ちが前向きになる"
                ),
                height=120
            )

            success = st.text_area(
                "🌟 今日うまくいったこと",
                placeholder=(
                    "例：LuNovaのアプリ開発を進められた"
                ),
                height=100
            )

            reflection = st.text_area(
                "🔍 今日の反省",
                placeholder=(
                    "例：スマホを長く見すぎてしまった"
                ),
                height=100
            )

            tomorrow_action = st.text_area(
                "➡️ 明日試したいこと",
                placeholder=(
                    "例：作業前に25分タイマーをかける"
                ),
                height=100
            )

            tags = st.multiselect(
                "🏷️ タグ",
                all_tags
            )

            custom_tags_text = st.text_input(
                "新しいタグ",
                placeholder=(
                    "複数ある場合はカンマ区切り"
                )
            )

            memo = st.text_area(
                "📝 自由メモ",
                placeholder=(
                    "そのほか残しておきたいこと"
                ),
                height=100
            )

            record_submit = (
                st.form_submit_button(
                    "✨ 振り返りを記録",
                    use_container_width=True
                )
            )

            if record_submit:
                custom_tags = [
                    tag.strip()
                    for tag in custom_tags_text.split(
                        ","
                    )
                    if tag.strip()
                ]

                final_tags = list(
                    dict.fromkeys(
                        tags + custom_tags
                    )
                )

                if not any(
                    [
                        insight.strip(),
                        success.strip(),
                        reflection.strip(),
                        tomorrow_action.strip(),
                        memo.strip()
                    ]
                ):
                    st.error(
                        "振り返り内容を一つ以上入力してください。"
                    )

                else:
                    add_record(
                        data=data,
                        record_date=selected_date,
                        mood=mood,
                        insight=insight.strip(),
                        success=success.strip(),
                        reflection=reflection.strip(),
                        tomorrow_action=(
                            tomorrow_action.strip()
                        ),
                        tags=final_tags,
                        memo=memo.strip()
                    )

                    st.success(
                        "今日の気づきを記録しました！✨"
                    )

                    st.balloons()
                    st.rerun()


# =====================================
# 過去の記録
# =====================================

with history_tab:
    st.header(
        "📚 過去の記録"
    )

    if not records:
        st.info(
            "記録はまだありません。"
        )

    else:
        filter_col1, filter_col2, filter_col3 = (
            st.columns(3)
        )

        with filter_col1:
            search_keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "気づき・成功・反省・メモ"
                ),
                key="history_search"
            )

        with filter_col2:
            mood_filter = st.selectbox(
                "気分",
                [
                    "すべて"
                ] + MOODS
            )

        with filter_col3:
            tag_filter = st.selectbox(
                "タグ",
                [
                    "すべて"
                ] + all_tags
            )

        filtered_records = list(
            records
        )

        if search_keyword:
            keyword = (
                search_keyword.strip().lower()
            )

            filtered_records = [
                record
                for record in filtered_records
                if (
                    keyword
                    in record.get(
                        "insight",
                        ""
                    ).lower()
                    or keyword
                    in record.get(
                        "success",
                        ""
                    ).lower()
                    or keyword
                    in record.get(
                        "reflection",
                        ""
                    ).lower()
                    or keyword
                    in record.get(
                        "tomorrow_action",
                        ""
                    ).lower()
                    or keyword
                    in record.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        if mood_filter != "すべて":
            filtered_records = [
                record
                for record in filtered_records
                if record.get(
                    "mood"
                ) == mood_filter
            ]

        if tag_filter != "すべて":
            filtered_records = [
                record
                for record in filtered_records
                if tag_filter
                in record.get(
                    "tags",
                    []
                )
            ]

        filtered_records = sorted(
            filtered_records,
            key=lambda record: record.get(
                "record_date",
                ""
            ),
            reverse=True
        )

        st.write(
            f"表示件数："
            f"**{len(filtered_records)}件**"
        )

        for record in filtered_records:
            record_id = record.get(
                "id",
                ""
            )

            with st.container(
                border=True
            ):
                date_col, mood_col = st.columns(
                    [4, 1]
                )

                with date_col:
                    st.subheader(
                        format_date(
                            record.get(
                                "record_date",
                                ""
                            )
                        )
                    )

                    if record.get(
                        "tags",
                        []
                    ):
                        st.caption(
                            "🏷️ "
                            + " / ".join(
                                record.get(
                                    "tags",
                                    []
                                )
                            )
                        )

                with mood_col:
                    mood_name = record.get(
                        "mood",
                        "普通"
                    )

                    st.metric(
                        "気分",
                        f"{MOOD_ICONS.get(mood_name, '')} "
                        f"{mood_name}"
                    )

                if record.get(
                    "insight",
                    ""
                ):
                    st.info(
                        f"💡 今日の気づき\n\n"
                        f"{record.get('insight', '')}"
                    )

                if record.get(
                    "success",
                    ""
                ):
                    st.success(
                        f"🌟 うまくいったこと\n\n"
                        f"{record.get('success', '')}"
                    )

                if record.get(
                    "reflection",
                    ""
                ):
                    st.warning(
                        f"🔍 反省したこと\n\n"
                        f"{record.get('reflection', '')}"
                    )

                if record.get(
                    "tomorrow_action",
                    ""
                ):
                    st.write(
                        f"➡️ **明日試したいこと**\n\n"
                        f"{record.get('tomorrow_action', '')}"
                    )

                if record.get(
                    "memo",
                    ""
                ):
                    st.caption(
                        f"📝 {record.get('memo', '')}"
                    )

                with st.expander(
                    "✏️ 記録を編集"
                ):
                    current_date = (
                        parse_date_text(
                            record.get(
                                "record_date",
                                ""
                            )
                        )
                        or date.today()
                    )

                    edit_date = st.date_input(
                        "記録日",
                        value=current_date,
                        key=(
                            f"edit_date_{record_id}"
                        )
                    )

                    current_mood = record.get(
                        "mood",
                        "普通"
                    )

                    mood_index = (
                        MOODS.index(
                            current_mood
                        )
                        if current_mood
                        in MOODS
                        else 2
                    )

                    edit_mood = st.selectbox(
                        "気分",
                        MOODS,
                        index=mood_index,
                        key=(
                            f"edit_mood_{record_id}"
                        )
                    )

                    edit_insight = st.text_area(
                        "今日の気づき",
                        value=record.get(
                            "insight",
                            ""
                        ),
                        key=(
                            f"edit_insight_{record_id}"
                        )
                    )

                    edit_success = st.text_area(
                        "うまくいったこと",
                        value=record.get(
                            "success",
                            ""
                        ),
                        key=(
                            f"edit_success_{record_id}"
                        )
                    )

                    edit_reflection = st.text_area(
                        "反省したこと",
                        value=record.get(
                            "reflection",
                            ""
                        ),
                        key=(
                            f"edit_reflection_{record_id}"
                        )
                    )

                    edit_tomorrow = st.text_area(
                        "明日試したいこと",
                        value=record.get(
                            "tomorrow_action",
                            ""
                        ),
                        key=(
                            f"edit_tomorrow_{record_id}"
                        )
                    )

                    edit_tags = st.multiselect(
                        "タグ",
                        all_tags,
                        default=record.get(
                            "tags",
                            []
                        ),
                        key=(
                            f"edit_tags_{record_id}"
                        )
                    )

                    edit_memo = st.text_area(
                        "自由メモ",
                        value=record.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_memo_{record_id}"
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_record_{record_id}"
                        ),
                        use_container_width=True
                    ):
                        duplicate_record = (
                            get_record_by_date(
                                data,
                                edit_date
                            )
                        )

                        if (
                            duplicate_record
                            and duplicate_record.get(
                                "id"
                            ) != record_id
                        ):
                            st.error(
                                "この日付には別の記録があります。"
                            )

                        elif not any(
                            [
                                edit_insight.strip(),
                                edit_success.strip(),
                                edit_reflection.strip(),
                                edit_tomorrow.strip(),
                                edit_memo.strip()
                            ]
                        ):
                            st.error(
                                "内容を一つ以上入力してください。"
                            )

                        else:
                            update_record(
                                data=data,
                                record_id=record_id,
                                record_date=edit_date,
                                mood=edit_mood,
                                insight=(
                                    edit_insight.strip()
                                ),
                                success=(
                                    edit_success.strip()
                                ),
                                reflection=(
                                    edit_reflection.strip()
                                ),
                                tomorrow_action=(
                                    edit_tomorrow.strip()
                                ),
                                tags=edit_tags,
                                memo=(
                                    edit_memo.strip()
                                )
                            )

                            st.success(
                                "記録を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 記録を削除"
                ):
                    st.warning(
                        "削除した記録は元に戻せません。"
                    )

                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_{record_id}"
                        )
                    )

                    if st.button(
                        "この記録を削除",
                        key=(
                            f"delete_record_{record_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_record(
                            data,
                            record_id
                        )

                        st.rerun()


# =====================================
# 月別表示
# =====================================

with calendar_tab:
    st.header(
        "📅 月別表示"
    )

    if not records:
        st.info(
            "表示できる記録がありません。"
        )

    else:
        available_months = sorted(
            {
                (
                    parse_date_text(
                        record.get(
                            "record_date",
                            ""
                        )
                    ).year,
                    parse_date_text(
                        record.get(
                            "record_date",
                            ""
                        )
                    ).month
                )
                for record in records
                if parse_date_text(
                    record.get(
                        "record_date",
                        ""
                    )
                )
            },
            reverse=True
        )

        month_options = {
            f"{year}年{month}月": (
                year,
                month
            )
            for year, month
            in available_months
        }

        selected_month_name = st.selectbox(
            "表示する月",
            list(
                month_options.keys()
            )
        )

        selected_year, selected_month = (
            month_options[
                selected_month_name
            ]
        )

        monthly_records = [
            record
            for record in records
            if (
                parse_date_text(
                    record.get(
                        "record_date",
                        ""
                    )
                )
                and parse_date_text(
                    record.get(
                        "record_date",
                        ""
                    )
                ).year
                == selected_year
                and parse_date_text(
                    record.get(
                        "record_date",
                        ""
                    )
                ).month
                == selected_month
            )
        ]

        monthly_records = sorted(
            monthly_records,
            key=lambda record: record.get(
                "record_date",
                ""
            )
        )

        monthly_average_mood = (
            get_average_mood(
                monthly_records
            )
        )

        summary_col1, summary_col2 = (
            st.columns(2)
        )

        with summary_col1:
            st.metric(
                "記録日数",
                f"{len(monthly_records)}日"
            )

        with summary_col2:
            st.metric(
                "平均気分",
                (
                    f"{MOOD_ICONS.get(monthly_average_mood, '')} "
                    f"{monthly_average_mood}"
                )
            )

        for record in monthly_records:
            with st.container(
                border=True
            ):
                mood_name = record.get(
                    "mood",
                    "普通"
                )

                st.subheader(
                    f"{MOOD_ICONS.get(mood_name, '')} "
                    f"{format_date(record.get('record_date', ''))}"
                )

                if record.get(
                    "insight",
                    ""
                ):
                    st.write(
                        f"💡 **気づき：**"
                        f"{record.get('insight', '')}"
                    )

                if record.get(
                    "success",
                    ""
                ):
                    st.write(
                        f"🌟 **成功：**"
                        f"{record.get('success', '')}"
                    )

                if record.get(
                    "tomorrow_action",
                    ""
                ):
                    st.write(
                        f"➡️ **次の行動：**"
                        f"{record.get('tomorrow_action', '')}"
                    )


# =====================================
# 分析
# =====================================

with analysis_tab:
    st.header(
        "📈 振り返り分析"
    )

    if not records:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        record_rows = []

        for record in records:
            record_date = parse_date_text(
                record.get(
                    "record_date",
                    ""
                )
            )

            record_rows.append(
                {
                    "日付": record_date,
                    "気分": record.get(
                        "mood",
                        "普通"
                    ),
                    "気分スコア": MOOD_SCORES.get(
                        record.get(
                            "mood",
                            "普通"
                        ),
                        3
                    )
                }
            )

        record_df = pd.DataFrame(
            record_rows
        )

        record_df = record_df.dropna(
            subset=[
                "日付"
            ]
        )

        record_df = record_df.sort_values(
            "日付"
        )

        st.subheader(
            "😊 気分の推移"
        )

        mood_chart_df = (
            record_df.set_index(
                "日付"
            )[["気分スコア"]]
        )

        st.line_chart(
            mood_chart_df
        )

        st.caption(
            "気分スコア："
            "5＝とても良い、1＝つらい"
        )

        st.divider()

        st.subheader(
            "📊 気分別の記録数"
        )

        mood_summary = (
            record_df.groupby(
                "気分",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "記録数"
                }
            )
            .sort_values(
                "記録数",
                ascending=False
            )
        )

        st.bar_chart(
            mood_summary.set_index(
                "気分"
            )[["記録数"]]
        )

        st.dataframe(
            mood_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🏷️ よく使うタグ"
        )

        if not tag_counter:
            st.info(
                "タグがまだ登録されていません。"
            )

        else:
            tag_summary = pd.DataFrame(
                [
                    {
                        "タグ": tag,
                        "使用回数": count
                    }
                    for tag, count
                    in tag_counter.most_common()
                ]
            )

            st.bar_chart(
                tag_summary.set_index(
                    "タグ"
                )[["使用回数"]]
            )

            st.dataframe(
                tag_summary,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "🗓️ 月別の記録数"
        )

        monthly_summary_df = (
            record_df.copy()
        )

        monthly_summary_df[
            "月"
        ] = monthly_summary_df[
            "日付"
        ].apply(
            lambda value: value.strftime(
                "%Y-%m"
            )
        )

        monthly_summary = (
            monthly_summary_df.groupby(
                "月",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "記録数"
                }
            )
        )

        st.bar_chart(
            monthly_summary.set_index(
                "月"
            )[["記録数"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True
        )


st.divider()

st.success(
    "小さな気づきの積み重ねが、"
    "未来の大きな成長につながります！💡"
)
