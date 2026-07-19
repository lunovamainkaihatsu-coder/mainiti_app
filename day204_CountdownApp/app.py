import json
import os
import uuid
from datetime import date, datetime

import streamlit as st


st.set_page_config(
    page_title="カウントダウン",
    page_icon="⏳",
    layout="centered"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "events.json"
)


# =====================================
# データの保存・読み込み
# =====================================

def save_events(events):
    """イベントをJSONへ保存する"""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            events,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_events():
    """イベントをJSONから読み込む"""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        save_events([])
        return []

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    save_events([])
    return []


def add_event(
    events,
    event_name,
    event_date,
    category,
    memo
):
    """新しいイベントを追加する"""

    new_event = {
        "id": str(uuid.uuid4()),
        "name": event_name,
        "date": str(event_date),
        "category": category,
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    events.append(new_event)
    save_events(events)


def delete_event(
    events,
    event_id
):
    """指定したイベントを削除する"""

    updated_events = [
        event
        for event in events
        if event.get("id") != event_id
    ]

    save_events(updated_events)


# =====================================
# 日付関連
# =====================================

def parse_event_date(event):
    """イベントの日付をdate型で返す"""

    try:
        return datetime.strptime(
            event.get("date", ""),
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return date.max


def calculate_remaining_days(event_date):
    """今日からイベント日までの日数を返す"""

    return (
        event_date - date.today()
    ).days


def format_event_date(event_date):
    """日付を日本語表示へ変換する"""

    return event_date.strftime(
        "%Y年%m月%d日"
    )


def get_category_icon(category):
    """カテゴリー別のアイコン"""

    category_icons = {
        "旅行": "✈️",
        "試験": "📚",
        "仕事": "💼",
        "記念日": "🎉",
        "誕生日": "🎂",
        "アプリ公開": "🚀",
        "その他": "📅"
    }

    return category_icons.get(
        category,
        "📅"
    )


def get_countdown_message(
    remaining_days
):
    """残り日数に応じたメッセージ"""

    if remaining_days > 30:
        return (
            f"あと {remaining_days}日",
            "まだ時間があります。"
            "少しずつ準備していこう！"
        )

    if remaining_days > 7:
        return (
            f"あと {remaining_days}日",
            "少しずつ近づいてきました！"
        )

    if remaining_days > 1:
        return (
            f"あと {remaining_days}日",
            "もうすぐです！"
            "準備を確認しよう。"
        )

    if remaining_days == 1:
        return (
            "あと1日",
            "いよいよ明日です！"
        )

    if remaining_days == 0:
        return (
            "今日！",
            "🎉 ついに当日です！"
        )

    return (
        f"{abs(remaining_days)}日前",
        "このイベントは終了しました。"
    )


# =====================================
# データ読み込み
# =====================================

events = load_events()

events = sorted(
    events,
    key=parse_event_date
)


# =====================================
# タイトル
# =====================================

st.title("⏳ カウントダウン")

st.caption(
    "大切な日まで、"
    "あと何日かを見える化しよう。"
)


# =====================================
# 集計カード
# =====================================

future_events = []

today_events = []

past_events = []

for event in events:
    event_date = parse_event_date(event)

    remaining_days = (
        calculate_remaining_days(
            event_date
        )
    )

    if remaining_days > 0:
        future_events.append(event)

    elif remaining_days == 0:
        today_events.append(event)

    else:
        past_events.append(event)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📅 登録イベント",
        f"{len(events)}件"
    )

with col2:
    st.metric(
        "⏳ 予定",
        f"{len(future_events)}件"
    )

with col3:
    st.metric(
        "🎉 今日",
        f"{len(today_events)}件"
    )


st.divider()


# =====================================
# 次のイベント
# =====================================

st.header("🌟 次のイベント")

upcoming_events = [
    event
    for event in events
    if calculate_remaining_days(
        parse_event_date(event)
    ) >= 0
]

if not upcoming_events:
    st.info(
        "これからのイベントは"
        "まだ登録されていません。"
    )

else:
    nearest_event = upcoming_events[0]

    nearest_date = parse_event_date(
        nearest_event
    )

    nearest_days = (
        calculate_remaining_days(
            nearest_date
        )
    )

    countdown_text, countdown_message = (
        get_countdown_message(
            nearest_days
        )
    )

    icon = get_category_icon(
        nearest_event.get(
            "category",
            "その他"
        )
    )

    with st.container(border=True):
        st.markdown(
            f"# {countdown_text}"
        )

        st.subheader(
            f"{icon} "
            f"{nearest_event.get('name', '')}"
        )

        st.write(
            format_event_date(
                nearest_date
            )
        )

        st.info(
            countdown_message
        )

        nearest_memo = nearest_event.get(
            "memo",
            ""
        )

        if nearest_memo:
            st.caption(
                nearest_memo
            )


st.divider()


# =====================================
# イベント追加フォーム
# =====================================

st.header("➕ イベントを追加")

with st.form(
    "event_form",
    clear_on_submit=True
):
    event_name = st.text_input(
        "イベント名",
        placeholder=(
            "例：Androidアプリ公開"
        )
    )

    event_date = st.date_input(
        "イベントの日付",
        value=date.today()
    )

    category = st.selectbox(
        "カテゴリー",
        [
            "アプリ公開",
            "旅行",
            "試験",
            "仕事",
            "記念日",
            "誕生日",
            "その他"
        ]
    )

    memo = st.text_area(
        "メモ",
        placeholder=(
            "準備することや"
            "楽しみにしていること"
        )
    )

    submitted = st.form_submit_button(
        "⏳ イベントを登録",
        use_container_width=True
    )

    if submitted:
        cleaned_name = event_name.strip()

        if not cleaned_name:
            st.error(
                "イベント名を"
                "入力してください。"
            )

        else:
            add_event(
                events=events,
                event_name=cleaned_name,
                event_date=event_date,
                category=category,
                memo=memo.strip()
            )

            st.success(
                f"「{cleaned_name}」を"
                "登録しました！"
            )

            st.rerun()


st.divider()


# =====================================
# イベント一覧
# =====================================

st.header("📋 イベント一覧")

if not events:
    st.info(
        "まだイベントがありません。"
        "大切な日を登録してみよう！"
    )

else:
    filter_col1, filter_col2 = (
        st.columns(2)
    )

    with filter_col1:
        search_word = st.text_input(
            "🔍 イベント検索",
            placeholder=(
                "イベント名やメモ"
            )
        )

    with filter_col2:
        category_filter = st.selectbox(
            "カテゴリーで絞り込み",
            [
                "すべて",
                "アプリ公開",
                "旅行",
                "試験",
                "仕事",
                "記念日",
                "誕生日",
                "その他"
            ]
        )

    display_filter = st.radio(
        "表示するイベント",
        [
            "これから",
            "すべて",
            "終了済み"
        ],
        horizontal=True
    )

    filtered_events = events

    if search_word:
        keyword = search_word.lower()

        filtered_events = [
            event
            for event in filtered_events
            if keyword in event.get(
                "name",
                ""
            ).lower()
            or keyword in event.get(
                "memo",
                ""
            ).lower()
        ]

    if category_filter != "すべて":
        filtered_events = [
            event
            for event in filtered_events
            if event.get(
                "category"
            ) == category_filter
        ]

    if display_filter == "これから":
        filtered_events = [
            event
            for event in filtered_events
            if calculate_remaining_days(
                parse_event_date(event)
            ) >= 0
        ]

    elif display_filter == "終了済み":
        filtered_events = [
            event
            for event in filtered_events
            if calculate_remaining_days(
                parse_event_date(event)
            ) < 0
        ]

    filtered_events = sorted(
        filtered_events,
        key=parse_event_date
    )

    st.write(
        f"表示件数："
        f"**{len(filtered_events)}件**"
    )

    if not filtered_events:
        st.warning(
            "条件に一致するイベントが"
            "ありません。"
        )

    for event in filtered_events:
        event_id = event.get(
            "id",
            ""
        )

        event_name = event.get(
            "name",
            "名称未設定"
        )

        event_category = event.get(
            "category",
            "その他"
        )

        event_date = parse_event_date(
            event
        )

        remaining_days = (
            calculate_remaining_days(
                event_date
            )
        )

        countdown_text, message = (
            get_countdown_message(
                remaining_days
            )
        )

        icon = get_category_icon(
            event_category
        )

        with st.container(border=True):
            title_col, days_col = (
                st.columns([3, 1])
            )

            with title_col:
                st.subheader(
                    f"{icon} {event_name}"
                )

                st.caption(
                    f"{event_category} "
                    f"／ "
                    f"{format_event_date(event_date)}"
                )

            with days_col:
                st.metric(
                    "カウント",
                    countdown_text
                )

            if remaining_days == 0:
                st.success(message)

            elif remaining_days < 0:
                st.info(message)

            elif remaining_days <= 7:
                st.warning(message)

            else:
                st.info(message)

            event_memo = event.get(
                "memo",
                ""
            )

            if event_memo:
                st.write(event_memo)

            with st.expander(
                "🗑️ このイベントを削除"
            ):
                st.warning(
                    "削除したイベントは"
                    "元に戻せません。"
                )

                confirm_delete = st.checkbox(
                    "削除を確認しました",
                    key=(
                        f"confirm_"
                        f"{event_id}"
                    )
                )

                delete_button = st.button(
                    "イベントを削除",
                    key=f"delete_{event_id}",
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True
                )

                if delete_button:
                    delete_event(
                        events,
                        event_id
                    )

                    st.success(
                        f"「{event_name}」を"
                        "削除しました。"
                    )

                    st.rerun()


st.divider()

st.success(
    "楽しみな日も、目標の日も、"
    "一歩ずつ近づいています。⏳"
)
