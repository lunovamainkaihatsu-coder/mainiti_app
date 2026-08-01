import calendar
import json
import os
import uuid
from datetime import date, datetime, time, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="カウントダウン管理",
    page_icon="⏳",
    layout="wide"
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "countdown_data.json"
)

CATEGORIES = [
    "仕事",
    "入社",
    "引っ越し",
    "旅行",
    "誕生日",
    "記念日",
    "試験",
    "アプリ開発",
    "家族",
    "支払い",
    "健康",
    "イベント",
    "その他",
]

PRIORITIES = [
    "最重要",
    "高",
    "中",
    "低",
]

PRIORITY_ICONS = {
    "最重要": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵",
}

PRIORITY_ORDER = {
    "最重要": 0,
    "高": 1,
    "中": 2,
    "低": 3,
}

REPEAT_TYPES = [
    "繰り返しなし",
    "毎年",
    "毎月",
    "毎週",
]

STATUS_OPTIONS = [
    "予定",
    "完了",
    "中止",
]

STATUS_ICONS = {
    "予定": "⏳",
    "完了": "✅",
    "中止": "⛔",
}


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
    """空の初期データを作成する。"""

    return {
        "events": []
    }


def save_data(data):
    """JSONファイルへ保存する。"""

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


def normalize_data(data):
    """保存データに不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "events",
        []
    )

    for event in data["events"]:
        event.setdefault(
            "id",
            create_id()
        )

        event.setdefault(
            "title",
            ""
        )

        event.setdefault(
            "event_date",
            str(date.today())
        )

        event.setdefault(
            "event_time",
            ""
        )

        event.setdefault(
            "has_time",
            False
        )

        event.setdefault(
            "category",
            "その他"
        )

        event.setdefault(
            "priority",
            "中"
        )

        event.setdefault(
            "status",
            "予定"
        )

        event.setdefault(
            "repeat_type",
            "繰り返しなし"
        )

        event.setdefault(
            "memo",
            ""
        )

        event.setdefault(
            "is_anniversary",
            False
        )

        event.setdefault(
            "preparation_items",
            []
        )

        event.setdefault(
            "completed_date",
            ""
        )

        event.setdefault(
            "created_at",
            ""
        )

        event.setdefault(
            "updated_at",
            ""
        )

        for item in event["preparation_items"]:
            item.setdefault(
                "id",
                create_id()
            )

            item.setdefault(
                "name",
                ""
            )

            item.setdefault(
                "checked",
                False
            )

            item.setdefault(
                "created_at",
                ""
            )

    return data


def load_data():
    """JSONファイルから読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
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
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE
            ):
                os.replace(
                    DATA_FILE,
                    broken_file
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 日付関連
# =========================================================

def parse_date(date_text):
    """日付文字列をdate型へ変換する。"""

    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except (
        TypeError,
        ValueError
    ):
        return None


def parse_time(time_text):
    """時刻文字列をtime型へ変換する。"""

    if not time_text:
        return None

    try:
        return datetime.strptime(
            time_text,
            "%H:%M"
        ).time()

    except (
        TypeError,
        ValueError
    ):
        return None


def format_date(date_text):
    """日付を日本語表示にする。"""

    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "日付不明"

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


def safe_replace_year(
    target_date,
    year
):
    """うるう日を考慮して年を変更する。"""

    try:
        return target_date.replace(
            year=year
        )

    except ValueError:
        return target_date.replace(
            year=year,
            day=28
        )


def safe_replace_month(
    target_date,
    year,
    month
):
    """月末日を考慮して年月を変更する。"""

    last_day = calendar.monthrange(
        year,
        month
    )[1]

    return date(
        year,
        month,
        min(
            target_date.day,
            last_day
        )
    )


def get_next_occurrence(event):
    """繰り返し設定を考慮した次回日を返す。"""

    original_date = parse_date(
        event.get(
            "event_date",
            ""
        )
    )

    if not original_date:
        return None

    repeat_type = event.get(
        "repeat_type",
        "繰り返しなし"
    )

    today = date.today()

    if repeat_type == "繰り返しなし":
        return original_date

    if repeat_type == "毎年":
        candidate = safe_replace_year(
            original_date,
            today.year
        )

        if candidate < today:
            candidate = safe_replace_year(
                original_date,
                today.year + 1
            )

        return candidate

    if repeat_type == "毎月":
        candidate = safe_replace_month(
            original_date,
            today.year,
            today.month
        )

        if candidate < today:
            if today.month == 12:
                next_year = today.year + 1
                next_month = 1

            else:
                next_year = today.year
                next_month = today.month + 1

            candidate = safe_replace_month(
                original_date,
                next_year,
                next_month
            )

        return candidate

    if repeat_type == "毎週":
        days_difference = (
            original_date.weekday()
            - today.weekday()
        ) % 7

        candidate = (
            today
            + timedelta(
                days=days_difference
            )
        )

        return candidate

    return original_date


def event_datetime(event):
    """イベントの次回日時を返す。"""

    next_date = get_next_occurrence(
        event
    )

    if not next_date:
        return None

    if event.get(
        "has_time",
        False
    ):
        event_time = parse_time(
            event.get(
                "event_time",
                ""
            )
        )

        if event_time:
            return datetime.combine(
                next_date,
                event_time
            )

    return datetime.combine(
        next_date,
        time.min
    )


def countdown_days(event):
    """イベントまでの日数を返す。"""

    next_date = get_next_occurrence(
        event
    )

    if not next_date:
        return None

    return (
        next_date
        - date.today()
    ).days


def countdown_text(event):
    """カウントダウン表示文字列を返す。"""

    days = countdown_days(
        event
    )

    if days is None:
        return "日付不明"

    if (
        event.get(
            "status"
        )
        == "完了"
        and event.get(
            "repeat_type"
        )
        == "繰り返しなし"
    ):
        return "完了済み"

    if days < 0:
        return f"{abs(days)}日経過"

    if days == 0:
        return "今日です！"

    if days == 1:
        return "明日！"

    if days >= 365:
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30

        if months > 0:
            return (
                f"あと{years}年"
                f"{months}か月"
            )

        return f"あと{years}年"

    if days >= 31:
        months = days // 30
        remaining_days = days % 30

        if remaining_days > 0:
            return (
                f"あと{months}か月"
                f"{remaining_days}日"
            )

        return f"あと{months}か月"

    return f"あと{days}日"


def elapsed_days(event):
    """登録日からの経過日数を返す。"""

    event_date = parse_date(
        event.get(
            "event_date",
            ""
        )
    )

    if not event_date:
        return None

    return (
        date.today()
        - event_date
    ).days


# =========================================================
# 補助関数
# =========================================================

def get_event_by_id(
    data,
    event_id
):
    """IDからイベントを取得する。"""

    for event in data["events"]:
        if event.get("id") == event_id:
            return event

    return None


def preparation_progress(event):
    """準備リストの進捗率を返す。"""

    items = event.get(
        "preparation_items",
        []
    )

    if not items:
        return 0

    checked_count = len(
        [
            item
            for item in items
            if item.get(
                "checked",
                False
            )
        ]
    )

    return (
        checked_count
        / len(items)
        * 100
    )


def preparation_checked_count(event):
    """準備済み項目数を返す。"""

    return len(
        [
            item
            for item in event.get(
                "preparation_items",
                []
            )
            if item.get(
                "checked",
                False
            )
        ]
    )


def event_sort_key(event):
    """イベント一覧の並び替えキーを返す。"""

    next_datetime = event_datetime(
        event
    )

    return (
        next_datetime
        if next_datetime
        else datetime.max
    )


# =========================================================
# データ操作
# =========================================================

def add_event(
    data,
    values
):
    """新しいイベントを追加する。"""

    event = {
        "id": create_id(),
        "title": values["title"],
        "event_date": values["event_date"],
        "event_time": values["event_time"],
        "has_time": values["has_time"],
        "category": values["category"],
        "priority": values["priority"],
        "status": "予定",
        "repeat_type": values["repeat_type"],
        "memo": values["memo"],
        "is_anniversary": (
            values["is_anniversary"]
        ),
        "preparation_items": [],
        "completed_date": "",
        "created_at": now_text(),
        "updated_at": "",
    }

    data["events"].append(
        event
    )

    save_data(data)


def update_event(
    data,
    event_id,
    values
):
    """イベント情報を更新する。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    previous_status = event.get(
        "status",
        "予定"
    )

    for key, value in values.items():
        event[key] = value

    if (
        event.get("status")
        == "完了"
        and previous_status
        != "完了"
    ):
        event["completed_date"] = str(
            date.today()
        )

    elif event.get(
        "status"
    ) != "完了":
        event["completed_date"] = ""

    event["updated_at"] = now_text()

    save_data(data)


def delete_event(
    data,
    event_id
):
    """イベントを削除する。"""

    data["events"] = [
        event
        for event in data["events"]
        if event.get("id")
        != event_id
    ]

    save_data(data)


def mark_event_completed(
    data,
    event_id
):
    """イベントを完了にする。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    event["status"] = "完了"
    event["completed_date"] = str(
        date.today()
    )
    event["updated_at"] = now_text()

    save_data(data)


def reopen_event(
    data,
    event_id
):
    """完了済みイベントを再開する。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    event["status"] = "予定"
    event["completed_date"] = ""
    event["updated_at"] = now_text()

    save_data(data)


def add_preparation_item(
    data,
    event_id,
    item_name
):
    """準備項目を追加する。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    item = {
        "id": create_id(),
        "name": item_name,
        "checked": False,
        "created_at": now_text(),
    }

    event[
        "preparation_items"
    ].append(
        item
    )

    event["updated_at"] = now_text()

    save_data(data)


def update_preparation_check(
    data,
    event_id,
    item_id,
    checked
):
    """準備項目のチェックを更新する。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    for item in event.get(
        "preparation_items",
        []
    ):
        if item.get("id") == item_id:
            item["checked"] = bool(
                checked
            )
            break

    event["updated_at"] = now_text()

    save_data(data)


def delete_preparation_item(
    data,
    event_id,
    item_id
):
    """準備項目を削除する。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    event[
        "preparation_items"
    ] = [
        item
        for item in event.get(
            "preparation_items",
            []
        )
        if item.get("id")
        != item_id
    ]

    event["updated_at"] = now_text()

    save_data(data)


def reset_preparation_items(
    data,
    event_id
):
    """準備項目のチェックをすべて外す。"""

    event = get_event_by_id(
        data,
        event_id
    )

    if not event:
        return

    for item in event.get(
        "preparation_items",
        []
    ):
        item["checked"] = False

    event["updated_at"] = now_text()

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
        background: rgba(120, 95, 255, 0.07);
        border: 1px solid rgba(120, 95, 255, 0.16);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(120, 95, 255, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(120, 95, 255, 0.18),
                rgba(255, 160, 90, 0.12)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }

    .big-countdown {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        padding: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

events = data[
    "events"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⏳ カウントダウン管理</h1>
        <p>
            楽しみな予定、大切な期限、人生の節目までの時間を見える化
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ダッシュボード
# =========================================================

active_events = [
    event
    for event in events
    if event.get("status")
    == "予定"
]

completed_events = [
    event
    for event in events
    if event.get("status")
    == "完了"
]

today_events = [
    event
    for event in active_events
    if countdown_days(
        event
    )
    == 0
]

within_7_days = [
    event
    for event in active_events
    if (
        countdown_days(
            event
        )
        is not None
        and 0
        <= countdown_days(event)
        <= 7
    )
]

within_30_days = [
    event
    for event in active_events
    if (
        countdown_days(
            event
        )
        is not None
        and 0
        <= countdown_days(event)
        <= 30
    )
]

expired_events = [
    event
    for event in active_events
    if (
        event.get(
            "repeat_type"
        )
        == "繰り返しなし"
        and countdown_days(
            event
        )
        is not None
        and countdown_days(
            event
        )
        < 0
    )
]

current_month_event_count = 0

for event in active_events:
    next_date = get_next_occurrence(
        event
    )

    if (
        next_date
        and next_date.year
        == date.today().year
        and next_date.month
        == date.today().month
    ):
        current_month_event_count += 1


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "登録イベント",
    f"{len(events)}件"
)

metric_row1[1].metric(
    "今日の予定",
    f"{len(today_events)}件"
)

metric_row1[2].metric(
    "7日以内",
    f"{len(within_7_days)}件"
)

metric_row1[3].metric(
    "30日以内",
    f"{len(within_30_days)}件"
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "今月の予定",
    f"{current_month_event_count}件"
)

metric_row2[1].metric(
    "完了済み",
    f"{len(completed_events)}件"
)

metric_row2[2].metric(
    "期限経過",
    f"{len(expired_events)}件"
)

metric_row2[3].metric(
    "準備項目",
    sum(
        len(
            event.get(
                "preparation_items",
                []
            )
        )
        for event in events
    )
)


# =========================================================
# 次の大切な予定
# =========================================================

future_events = [
    event
    for event in active_events
    if (
        countdown_days(
            event
        )
        is not None
        and countdown_days(
            event
        )
        >= 0
    )
]

if future_events:
    st.divider()

    future_events = sorted(
        future_events,
        key=lambda event: (
            event_sort_key(
                event
            ),
            PRIORITY_ORDER.get(
                event.get(
                    "priority",
                    "中"
                ),
                99
            )
        )
    )

    next_event = future_events[0]

    st.subheader(
        "🌟 次の大切な予定"
    )

    with st.container(
        border=True
    ):
        next_column1, next_column2 = (
            st.columns(
                [
                    3,
                    2,
                ]
            )
        )

        with next_column1:
            st.markdown(
                f"### "
                f"{PRIORITY_ICONS.get(next_event.get('priority', ''), '')} "
                f"{next_event.get('title', '')}"
            )

            st.caption(
                f"{next_event.get('category', '')} ／ "
                f"{format_date(str(get_next_occurrence(next_event)))}"
            )

            if next_event.get(
                "has_time",
                False
            ):
                st.write(
                    f"🕒 "
                    f"{next_event.get('event_time', '')}"
                )

            if next_event.get(
                "memo",
                ""
            ):
                st.info(
                    next_event.get(
                        "memo",
                        ""
                    )
                )

        with next_column2:
            st.markdown(
                (
                    "<div class='big-countdown'>"
                    + countdown_text(
                        next_event
                    )
                    + "</div>"
                ),
                unsafe_allow_html=True
            )

            items = next_event.get(
                "preparation_items",
                []
            )

            if items:
                progress = (
                    preparation_progress(
                        next_event
                    )
                )

                st.progress(
                    progress / 100
                )

                st.caption(
                    f"準備："
                    f"{preparation_checked_count(next_event)}"
                    f"／{len(items)}"
                )


# =========================================================
# 今日・期限間近
# =========================================================

if today_events or expired_events:
    st.divider()

    alert_column1, alert_column2 = (
        st.columns(2)
    )

    with alert_column1:
        st.subheader(
            "📣 今日の予定"
        )

        if not today_events:
            st.success(
                "今日の予定はありません。"
            )

        else:
            for event in today_events:
                st.warning(
                    f"**{event.get('title', '')}** "
                    f"— 今日です！"
                )

    with alert_column2:
        st.subheader(
            "⚠️ 期限を過ぎた予定"
        )

        if not expired_events:
            st.success(
                "期限を過ぎた予定はありません。"
            )

        else:
            for event in expired_events:
                st.error(
                    f"**{event.get('title', '')}** "
                    f"— {abs(countdown_days(event))}日経過"
                )


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    preparation_tab,
    history_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ イベント登録",
        "⏳ カウントダウン一覧",
        "🎒 準備リスト",
        "✅ 完了・過去イベント",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# イベント登録
# =========================================================

with add_tab:
    st.header(
        "➕ 新しいイベントを登録"
    )

    with st.form(
        "add_event_form",
        clear_on_submit=True
    ):
        form_column1, form_column2 = (
            st.columns(2)
        )

        with form_column1:
            title = st.text_input(
                "イベント名",
                placeholder=(
                    "例：新しい会社への入社"
                )
            )

            event_date_input = (
                st.date_input(
                    "イベント日",
                    value=(
                        date.today()
                        + timedelta(
                            days=30
                        )
                    )
                )
            )

            has_time = st.checkbox(
                "時刻を設定する"
            )

            event_time_text = ""

            if has_time:
                event_time_input = (
                    st.time_input(
                        "イベント時刻",
                        value=time(
                            hour=9,
                            minute=0
                        )
                    )
                )

                event_time_text = (
                    event_time_input.strftime(
                        "%H:%M"
                    )
                )

        with form_column2:
            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

            priority = st.selectbox(
                "重要度",
                PRIORITIES,
                index=2
            )

            repeat_type = st.selectbox(
                "繰り返し",
                REPEAT_TYPES
            )

            is_anniversary = (
                st.checkbox(
                    "経過日数も表示する"
                )
            )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "事前に確認することや、"
                "この予定について残しておきたいこと"
            ),
            height=120
        )

        submitted = (
            st.form_submit_button(
                "⏳ イベントを登録",
                use_container_width=True
            )
        )

        if submitted:
            cleaned_title = (
                title.strip()
            )

            duplicate_exists = any(
                event.get(
                    "title",
                    ""
                ).strip().lower()
                == cleaned_title.lower()
                and event.get(
                    "event_date"
                )
                == str(
                    event_date_input
                )
                for event in events
            )

            if not cleaned_title:
                st.error(
                    "イベント名を入力してください。"
                )

            elif duplicate_exists:
                st.warning(
                    "同じ名前と日付のイベントが登録されています。"
                )

            else:
                add_event(
                    data,
                    {
                        "title": (
                            cleaned_title
                        ),
                        "event_date": str(
                            event_date_input
                        ),
                        "event_time": (
                            event_time_text
                        ),
                        "has_time": (
                            has_time
                        ),
                        "category": (
                            category
                        ),
                        "priority": (
                            priority
                        ),
                        "repeat_type": (
                            repeat_type
                        ),
                        "memo": (
                            memo.strip()
                        ),
                        "is_anniversary": (
                            is_anniversary
                        ),
                    }
                )

                st.success(
                    "イベントを登録しました！"
                )

                st.rerun()


# =========================================================
# カウントダウン一覧
# =========================================================

with list_tab:
    st.header(
        "⏳ カウントダウン一覧"
    )

    if not events:
        st.info(
            "イベントはまだ登録されていません。"
        )

    else:
        filter_column1, filter_column2, filter_column3 = (
            st.columns(3)
        )

        with filter_column1:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "イベント名・メモ"
                )
            )

        with filter_column2:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES
                )
            )

        with filter_column3:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ]
                    + STATUS_OPTIONS
                )
            )

        priority_filter = (
            st.multiselect(
                "重要度",
                PRIORITIES,
                default=PRIORITIES
            )
        )

        display_filter = st.selectbox(
            "表示範囲",
            [
                "すべて",
                "今日",
                "7日以内",
                "30日以内",
                "未来の予定",
                "期限経過",
                "繰り返し予定",
            ]
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "日付が近い順",
                "重要度順",
                "登録が新しい順",
                "タイトル順",
            ]
        )

        filtered_events = list(
            events
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_events = [
                event
                for event
                in filtered_events
                if (
                    search_word
                    in event.get(
                        "title",
                        ""
                    ).lower()
                    or search_word
                    in event.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        if category_filter != "すべて":
            filtered_events = [
                event
                for event
                in filtered_events
                if event.get(
                    "category"
                )
                == category_filter
            ]

        if status_filter != "すべて":
            filtered_events = [
                event
                for event
                in filtered_events
                if event.get(
                    "status"
                )
                == status_filter
            ]

        filtered_events = [
            event
            for event in filtered_events
            if event.get(
                "priority",
                "中"
            )
            in priority_filter
        ]

        if display_filter == "今日":
            filtered_events = [
                event
                for event
                in filtered_events
                if countdown_days(
                    event
                )
                == 0
            ]

        elif display_filter == "7日以内":
            filtered_events = [
                event
                for event
                in filtered_events
                if (
                    countdown_days(
                        event
                    )
                    is not None
                    and 0
                    <= countdown_days(event)
                    <= 7
                )
            ]

        elif display_filter == "30日以内":
            filtered_events = [
                event
                for event
                in filtered_events
                if (
                    countdown_days(
                        event
                    )
                    is not None
                    and 0
                    <= countdown_days(event)
                    <= 30
                )
            ]

        elif display_filter == "未来の予定":
            filtered_events = [
                event
                for event
                in filtered_events
                if (
                    countdown_days(
                        event
                    )
                    is not None
                    and countdown_days(
                        event
                    )
                    >= 0
                )
            ]

        elif display_filter == "期限経過":
            filtered_events = [
                event
                for event
                in filtered_events
                if (
                    event.get(
                        "repeat_type"
                    )
                    == "繰り返しなし"
                    and countdown_days(
                        event
                    )
                    is not None
                    and countdown_days(
                        event
                    )
                    < 0
                )
            ]

        elif display_filter == "繰り返し予定":
            filtered_events = [
                event
                for event
                in filtered_events
                if event.get(
                    "repeat_type"
                )
                != "繰り返しなし"
            ]

        if sort_option == "日付が近い順":
            filtered_events.sort(
                key=event_sort_key
            )

        elif sort_option == "重要度順":
            filtered_events.sort(
                key=lambda event: (
                    PRIORITY_ORDER.get(
                        event.get(
                            "priority",
                            "中"
                        ),
                        99
                    ),
                    event_sort_key(
                        event
                    )
                )
            )

        elif sort_option == "登録が新しい順":
            filtered_events.sort(
                key=lambda event: (
                    event.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

        elif sort_option == "タイトル順":
            filtered_events.sort(
                key=lambda event: (
                    event.get(
                        "title",
                        ""
                    )
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_events)}件**"
        )

        for event in filtered_events:
            event_id = event["id"]

            next_date = get_next_occurrence(
                event
            )

            with st.container(
                border=True
            ):
                title_column, countdown_column = (
                    st.columns(
                        [
                            3,
                            2,
                        ]
                    )
                )

                with title_column:
                    st.markdown(
                        f"### "
                        f"{PRIORITY_ICONS.get(event.get('priority', ''), '')} "
                        f"{event.get('title', '')}"
                    )

                    st.caption(
                        f"{event.get('category', '')} ／ "
                        f"{STATUS_ICONS.get(event.get('status', ''), '')} "
                        f"{event.get('status', '')} ／ "
                        f"{event.get('repeat_type', '')}"
                    )

                    if next_date:
                        st.write(
                            f"📅 "
                            f"{format_date(str(next_date))}"
                        )

                    if event.get(
                        "has_time",
                        False
                    ):
                        st.write(
                            f"🕒 "
                            f"{event.get('event_time', '')}"
                        )

                with countdown_column:
                    st.markdown(
                        (
                            "<div class='big-countdown'>"
                            + countdown_text(
                                event
                            )
                            + "</div>"
                        ),
                        unsafe_allow_html=True
                    )

                if event.get(
                    "memo",
                    ""
                ):
                    st.info(
                        event.get(
                            "memo",
                            ""
                        )
                    )

                if event.get(
                    "is_anniversary",
                    False
                ):
                    elapsed = elapsed_days(
                        event
                    )

                    if (
                        elapsed is not None
                        and elapsed >= 0
                    ):
                        st.success(
                            f"この日から"
                            f" **{elapsed}日** "
                            f"経過しています。"
                        )

                preparation_items = event.get(
                    "preparation_items",
                    []
                )

                if preparation_items:
                    progress = (
                        preparation_progress(
                            event
                        )
                    )

                    st.progress(
                        progress / 100
                    )

                    st.caption(
                        f"準備："
                        f"{preparation_checked_count(event)}"
                        f"／"
                        f"{len(preparation_items)}"
                    )

                action_columns = (
                    st.columns(2)
                )

                with action_columns[0]:
                    if (
                        event.get("status")
                        != "完了"
                        and st.button(
                            "✅ 完了にする",
                            key=(
                                f"complete_event_"
                                f"{event_id}"
                            ),
                            use_container_width=True
                        )
                    ):
                        mark_event_completed(
                            data,
                            event_id
                        )

                        st.balloons()
                        st.rerun()

                with action_columns[1]:
                    if (
                        event.get("status")
                        == "完了"
                        and st.button(
                            "↩️ 再開する",
                            key=(
                                f"reopen_event_"
                                f"{event_id}"
                            ),
                            use_container_width=True
                        )
                    ):
                        reopen_event(
                            data,
                            event_id
                        )

                        st.rerun()

                with st.expander(
                    "✏️ イベントを編集"
                ):
                    edit_title = (
                        st.text_input(
                            "イベント名",
                            value=event.get(
                                "title",
                                ""
                            ),
                            key=(
                                f"edit_title_"
                                f"{event_id}"
                            )
                        )
                    )

                    edit_date = st.date_input(
                        "イベント日",
                        value=(
                            parse_date(
                                event.get(
                                    "event_date",
                                    ""
                                )
                            )
                            or date.today()
                        ),
                        key=(
                            f"edit_date_"
                            f"{event_id}"
                        )
                    )

                    edit_has_time = (
                        st.checkbox(
                            "時刻を設定する",
                            value=bool(
                                event.get(
                                    "has_time",
                                    False
                                )
                            ),
                            key=(
                                f"edit_has_time_"
                                f"{event_id}"
                            )
                        )
                    )

                    edit_time_text = ""

                    if edit_has_time:
                        current_time = (
                            parse_time(
                                event.get(
                                    "event_time",
                                    ""
                                )
                            )
                            or time(
                                hour=9,
                                minute=0
                            )
                        )

                        edit_time_value = (
                            st.time_input(
                                "時刻",
                                value=current_time,
                                key=(
                                    f"edit_time_"
                                    f"{event_id}"
                                )
                            )
                        )

                        edit_time_text = (
                            edit_time_value.strftime(
                                "%H:%M"
                            )
                        )

                    edit_column1, edit_column2 = (
                        st.columns(2)
                    )

                    with edit_column1:
                        current_category = (
                            event.get(
                                "category",
                                "その他"
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
                                    f"{event_id}"
                                )
                            )
                        )

                        current_priority = (
                            event.get(
                                "priority",
                                "中"
                            )
                        )

                        edit_priority = (
                            st.selectbox(
                                "重要度",
                                PRIORITIES,
                                index=(
                                    PRIORITIES.index(
                                        current_priority
                                    )
                                    if current_priority
                                    in PRIORITIES
                                    else 2
                                ),
                                key=(
                                    f"edit_priority_"
                                    f"{event_id}"
                                )
                            )
                        )

                    with edit_column2:
                        current_repeat = (
                            event.get(
                                "repeat_type",
                                "繰り返しなし"
                            )
                        )

                        edit_repeat = (
                            st.selectbox(
                                "繰り返し",
                                REPEAT_TYPES,
                                index=(
                                    REPEAT_TYPES.index(
                                        current_repeat
                                    )
                                    if current_repeat
                                    in REPEAT_TYPES
                                    else 0
                                ),
                                key=(
                                    f"edit_repeat_"
                                    f"{event_id}"
                                )
                            )
                        )

                        current_status = (
                            event.get(
                                "status",
                                "予定"
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
                                    f"{event_id}"
                                )
                            )
                        )

                    edit_anniversary = (
                        st.checkbox(
                            "経過日数も表示する",
                            value=bool(
                                event.get(
                                    "is_anniversary",
                                    False
                                )
                            ),
                            key=(
                                f"edit_anniversary_"
                                f"{event_id}"
                            )
                        )
                    )

                    edit_memo = st.text_area(
                        "メモ",
                        value=event.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_memo_"
                            f"{event_id}"
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_event_"
                            f"{event_id}"
                        ),
                        use_container_width=True
                    ):
                        if not edit_title.strip():
                            st.error(
                                "イベント名を入力してください。"
                            )

                        else:
                            update_event(
                                data,
                                event_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "event_date": str(
                                        edit_date
                                    ),
                                    "event_time": (
                                        edit_time_text
                                    ),
                                    "has_time": (
                                        edit_has_time
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "repeat_type": (
                                        edit_repeat
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "is_anniversary": (
                                        edit_anniversary
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                }
                            )

                            st.success(
                                "イベントを更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ イベントを削除"
                ):
                    st.warning(
                        "準備リストも一緒に削除されます。"
                    )

                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{event_id}"
                            )
                        )
                    )

                    if st.button(
                        "このイベントを削除",
                        key=(
                            f"delete_event_"
                            f"{event_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_event(
                            data,
                            event_id
                        )

                        st.rerun()


# =========================================================
# 準備リスト
# =========================================================

with preparation_tab:
    st.header(
        "🎒 イベント準備リスト"
    )

    if not events:
        st.info(
            "イベントを登録すると準備リストを作れます。"
        )

    else:
        preparation_options = {
            (
                f"{event.get('title', '')}"
                f"｜{countdown_text(event)}"
            ): event["id"]
            for event in sorted(
                events,
                key=event_sort_key
            )
        }

        selected_event_name = (
            st.selectbox(
                "イベントを選択",
                list(
                    preparation_options.keys()
                )
            )
        )

        selected_event = (
            get_event_by_id(
                data,
                preparation_options[
                    selected_event_name
                ]
            )
        )

        selected_event_id = (
            selected_event["id"]
        )

        with st.container(
            border=True
        ):
            st.subheader(
                selected_event.get(
                    "title",
                    ""
                )
            )

            st.markdown(
                (
                    "<div class='big-countdown'>"
                    + countdown_text(
                        selected_event
                    )
                    + "</div>"
                ),
                unsafe_allow_html=True
            )

        with st.form(
            (
                f"add_preparation_"
                f"{selected_event_id}"
            ),
            clear_on_submit=True
        ):
            preparation_name = (
                st.text_input(
                    "準備すること",
                    placeholder=(
                        "例：必要書類をそろえる"
                    )
                )
            )

            preparation_submit = (
                st.form_submit_button(
                    "➕ 準備項目を追加",
                    use_container_width=True
                )
            )

            if preparation_submit:
                cleaned_name = (
                    preparation_name.strip()
                )

                duplicate_exists = any(
                    item.get(
                        "name",
                        ""
                    ).strip().lower()
                    == cleaned_name.lower()
                    for item
                    in selected_event.get(
                        "preparation_items",
                        []
                    )
                )

                if not cleaned_name:
                    st.error(
                        "準備項目を入力してください。"
                    )

                elif duplicate_exists:
                    st.warning(
                        "同じ準備項目が登録されています。"
                    )

                else:
                    add_preparation_item(
                        data,
                        selected_event_id,
                        cleaned_name
                    )

                    st.success(
                        "準備項目を追加しました！"
                    )

                    st.rerun()

        items = selected_event.get(
            "preparation_items",
            []
        )

        st.divider()

        if not items:
            st.info(
                "準備項目はまだありません。"
            )

        else:
            progress = (
                preparation_progress(
                    selected_event
                )
            )

            st.progress(
                progress / 100
            )

            st.write(
                f"準備状況："
                f"**{preparation_checked_count(selected_event)}"
                f" / {len(items)}**"
            )

            if progress >= 100:
                st.success(
                    "すべての準備が完了しました！🎉"
                )

            for item in items:
                item_id = item["id"]

                with st.container(
                    border=True
                ):
                    item_column1, item_column2 = (
                        st.columns(
                            [
                                5,
                                1,
                            ]
                        )
                    )

                    with item_column1:
                        checked = st.checkbox(
                            item.get(
                                "name",
                                ""
                            ),
                            value=bool(
                                item.get(
                                    "checked",
                                    False
                                )
                            ),
                            key=(
                                f"prepare_check_"
                                f"{item_id}"
                            )
                        )

                        if (
                            checked
                            != item.get(
                                "checked",
                                False
                            )
                        ):
                            update_preparation_check(
                                data,
                                selected_event_id,
                                item_id,
                                checked
                            )

                            st.rerun()

                    with item_column2:
                        if st.button(
                            "削除",
                            key=(
                                f"delete_prepare_"
                                f"{item_id}"
                            )
                        ):
                            delete_preparation_item(
                                data,
                                selected_event_id,
                                item_id
                            )

                            st.rerun()

            if st.button(
                "🔄 チェックをすべてリセット",
                use_container_width=True
            ):
                reset_preparation_items(
                    data,
                    selected_event_id
                )

                st.rerun()


# =========================================================
# 完了・過去イベント
# =========================================================

with history_tab:
    st.header(
        "✅ 完了・過去イベント"
    )

    history_events = [
        event
        for event in events
        if (
            event.get(
                "status"
            )
            in [
                "完了",
                "中止",
            ]
            or (
                event.get(
                    "repeat_type"
                )
                == "繰り返しなし"
                and countdown_days(
                    event
                )
                is not None
                and countdown_days(
                    event
                )
                < 0
            )
        )
    ]

    if not history_events:
        st.info(
            "完了・過去イベントはありません。"
        )

    else:
        history_events = sorted(
            history_events,
            key=lambda event: (
                parse_date(
                    event.get(
                        "event_date",
                        ""
                    )
                )
                or date.min
            ),
            reverse=True
        )

        for event in history_events:
            with st.container(
                border=True
            ):
                history_column1, history_column2 = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with history_column1:
                    st.subheader(
                        event.get(
                            "title",
                            ""
                        )
                    )

                    st.caption(
                        f"{event.get('category', '')} ／ "
                        f"{format_date(event.get('event_date', ''))}"
                    )

                    if event.get(
                        "memo",
                        ""
                    ):
                        st.write(
                            event.get(
                                "memo",
                                ""
                            )
                        )

                with history_column2:
                    st.metric(
                        "状態",
                        (
                            f"{STATUS_ICONS.get(event.get('status', ''), '')} "
                            f"{event.get('status', '')}"
                        )
                    )

                if event.get(
                    "completed_date",
                    ""
                ):
                    st.success(
                        f"完了日："
                        f"{format_date(event.get('completed_date', ''))}"
                    )

                event_date = parse_date(
                    event.get(
                        "event_date",
                        ""
                    )
                )

                if (
                    event_date
                    and event_date
                    <= date.today()
                ):
                    st.caption(
                        f"イベントから"
                        f"{(date.today() - event_date).days}日経過"
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 イベント分析"
    )

    if not events:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for event in events:
            next_date = get_next_occurrence(
                event
            )

            analysis_rows.append(
                {
                    "イベント": event.get(
                        "title",
                        ""
                    ),
                    "カテゴリー": event.get(
                        "category",
                        ""
                    ),
                    "重要度": event.get(
                        "priority",
                        ""
                    ),
                    "状態": event.get(
                        "status",
                        ""
                    ),
                    "繰り返し": event.get(
                        "repeat_type",
                        ""
                    ),
                    "次回日": (
                        next_date
                        if next_date
                        else None
                    ),
                    "残り日数": (
                        countdown_days(
                            event
                        )
                    ),
                    "準備項目数": len(
                        event.get(
                            "preparation_items",
                            []
                        )
                    ),
                    "準備済み数": (
                        preparation_checked_count(
                            event
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "カテゴリー別イベント数"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["件数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "状態別イベント数"
        )

        status_summary = (
            analysis_df.groupby(
                "状態",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False
            )
        )

        st.bar_chart(
            status_summary.set_index(
                "状態"
            )[["件数"]]
        )

        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "重要度別イベント数"
        )

        priority_summary = (
            analysis_df.groupby(
                "重要度",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
        )

        priority_summary[
            "並び順"
        ] = priority_summary[
            "重要度"
        ].map(
            PRIORITY_ORDER
        )

        priority_summary = (
            priority_summary.sort_values(
                "並び順"
            )
            .drop(
                columns=[
                    "並び順"
                ]
            )
        )

        st.bar_chart(
            priority_summary.set_index(
                "重要度"
            )[["件数"]]
        )

        st.dataframe(
            priority_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "月別イベント数"
        )

        month_rows = []

        for event in events:
            event_date = parse_date(
                event.get(
                    "event_date",
                    ""
                )
            )

            if event_date:
                month_rows.append(
                    {
                        "月": event_date.strftime(
                            "%Y-%m"
                        ),
                        "件数": 1,
                    }
                )

        if month_rows:
            month_df = pd.DataFrame(
                month_rows
            )

            month_summary = (
                month_df.groupby(
                    "月",
                    as_index=False
                )["件数"]
                .sum()
                .sort_values(
                    "月"
                )
            )

            st.bar_chart(
                month_summary.set_index(
                    "月"
                )[["件数"]]
            )

            st.dataframe(
                month_summary,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "準備が多いイベント"
        )

        preparation_ranking = (
            analysis_df.sort_values(
                "準備項目数",
                ascending=False
            )[
                [
                    "イベント",
                    "準備項目数",
                    "準備済み数",
                    "状態",
                ]
            ]
        )

        st.dataframe(
            preparation_ranking,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "今後のイベント一覧"
        )

        upcoming_df = analysis_df[
            analysis_df[
                "残り日数"
            ].notna()
        ]

        upcoming_df = upcoming_df[
            upcoming_df[
                "残り日数"
            ]
            >= 0
        ].sort_values(
            "残り日数"
        )

        st.dataframe(
            upcoming_df[
                [
                    "イベント",
                    "カテゴリー",
                    "次回日",
                    "残り日数",
                    "重要度",
                ]
            ],
            use_container_width=True,
            hide_index=True
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
        indent=2
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"countdown_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = st.file_uploader(
        "バックアップJSONを選択",
        type=[
            "json"
        ]
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict
                )
                or "events"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "events"
                    ],
                    list
                )
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
                    use_container_width=True
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
            UnicodeDecodeError
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "イベントと準備リストがすべて削除されます。"
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
        use_container_width=True
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
    "大切な日は、待っている時間も思い出になる。⏳"
)
