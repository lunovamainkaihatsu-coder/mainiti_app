import json
import os
import random
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="あの日から何日？",
    page_icon="🌱",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "events.json")

CATEGORIES = [
    "💻 制作・開発",
    "📚 勉強",
    "🏃 健康・運動",
    "💼 仕事",
    "👨‍👩‍👧 家族",
    "🏠 生活",
    "🌟 挑戦",
    "❤️ 大切な出来事",
    "✨ その他",
]

MILESTONES = [
    7,
    30,
    50,
    100,
    200,
    300,
    365,
    500,
    730,
    1000,
    1500,
    2000,
    3000,
    3650,
    5000,
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


def elapsed_days(event):
    start = parse_date(
        event.get("start_date")
    )

    if not start:
        return 0

    return max(
        (date.today() - start).days,
        0,
    )


def elapsed_hours(event):
    return elapsed_days(event) * 24


def human_elapsed(start_date):
    start = parse_date(start_date)

    if not start:
        return "-"

    today = date.today()

    if start > today:
        return "まだ始まっていません"

    years = today.year - start.year
    months = today.month - start.month
    days = today.day - start.day

    if days < 0:
        months -= 1

        previous_month = today.month - 1
        previous_year = today.year

        if previous_month == 0:
            previous_month = 12
            previous_year -= 1

        if previous_month == 12:
            next_month = date(
                previous_year + 1,
                1,
                1,
            )
        else:
            next_month = date(
                previous_year,
                previous_month + 1,
                1,
            )

        month_start = date(
            previous_year,
            previous_month,
            1,
        )

        days_in_previous_month = (
            next_month - month_start
        ).days

        days += days_in_previous_month

    if months < 0:
        years -= 1
        months += 12

    parts = []

    if years:
        parts.append(f"{years}年")

    if months:
        parts.append(f"{months}か月")

    if days or not parts:
        parts.append(f"{days}日")

    return "".join(parts)


def next_milestone(days):
    for milestone in MILESTONES:
        if milestone > days:
            return milestone

    # 5000日を超えたら1000日刻み
    return (
        ((days // 1000) + 1)
        * 1000
    )


def reached_milestones(days):
    return [
        milestone
        for milestone in MILESTONES
        if milestone <= days
    ]


def milestone_progress(days):
    next_target = next_milestone(days)

    previous_targets = [
        milestone
        for milestone in MILESTONES
        if milestone <= days
    ]

    previous = (
        max(previous_targets)
        if previous_targets
        else 0
    )

    span = next_target - previous

    if span <= 0:
        return 1.0

    progress = (
        (days - previous)
        / span
    )

    return max(
        0.0,
        min(progress, 1.0),
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "events": [],
        "progress_notes": [],
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

        data.setdefault("events", [])
        data.setdefault(
            "progress_notes",
            [],
        )

        for event in data["events"]:
            event.setdefault(
                "id",
                create_id(),
            )
            event.setdefault(
                "title",
                "",
            )
            event.setdefault(
                "category",
                "✨ その他",
            )
            event.setdefault(
                "start_date",
                today_text(),
            )
            event.setdefault(
                "first_memo",
                "",
            )
            event.setdefault(
                "favorite",
                False,
            )
            event.setdefault(
                "created_at",
                now_text(),
            )
            event.setdefault(
                "updated_at",
                event.get(
                    "created_at",
                    now_text(),
                ),
            )

        for note in data[
            "progress_notes"
        ]:
            note.setdefault(
                "id",
                create_id(),
            )
            note.setdefault(
                "event_id",
                "",
            )
            note.setdefault(
                "note",
                "",
            )
            note.setdefault(
                "record_date",
                today_text(),
            )
            note.setdefault(
                "created_at",
                now_text(),
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

def get_event(data, event_id):
    return next(
        (
            event
            for event in data["events"]
            if event.get("id")
            == event_id
        ),
        None,
    )


def add_event(
    data,
    title,
    category,
    start_date,
    first_memo,
):
    event = {
        "id": create_id(),
        "title": title,
        "category": category,
        "start_date": str(start_date),
        "first_memo": first_memo,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["events"].append(event)
    save_data(data)

    return event["id"]


def update_event(
    data,
    event_id,
    title,
    category,
    start_date,
    first_memo,
):
    event = get_event(
        data,
        event_id,
    )

    if not event:
        return

    event["title"] = title
    event["category"] = category
    event["start_date"] = str(
        start_date
    )
    event["first_memo"] = (
        first_memo
    )
    event["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    event_id,
):
    event = get_event(
        data,
        event_id,
    )

    if not event:
        return

    event["favorite"] = (
        not event.get(
            "favorite",
            False,
        )
    )

    event["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_event(
    data,
    event_id,
):
    data["events"] = [
        event
        for event in data["events"]
        if event.get("id")
        != event_id
    ]

    data["progress_notes"] = [
        note
        for note
        in data["progress_notes"]
        if note.get("event_id")
        != event_id
    ]

    save_data(data)


def add_progress_note(
    data,
    event_id,
    note,
):
    item = {
        "id": create_id(),
        "event_id": event_id,
        "note": note,
        "record_date": today_text(),
        "created_at": now_text(),
    }

    data[
        "progress_notes"
    ].append(item)

    save_data(data)


def delete_progress_note(
    data,
    note_id,
):
    data["progress_notes"] = [
        note
        for note
        in data["progress_notes"]
        if note.get("id")
        != note_id
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
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;
        background: rgba(70, 180, 120, 0.07);
        border: 1px solid rgba(70, 180, 120, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 190, 120, 0.20),
                rgba(110, 180, 220, 0.08)
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

    .day-number {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 8px 0;
    }

    .soft-text {
        opacity: 0.72;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()
events = data["events"]
progress_notes = data[
    "progress_notes"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📅 あの日から何日？</h1>
        <p>
            あの日に始まったことは、
            今日の自分につながっている。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

if events:
    longest_event = max(
        events,
        key=elapsed_days,
    )

    total_days = sum(
        elapsed_days(event)
        for event in events
    )

    total_milestones = sum(
        len(
            reached_milestones(
                elapsed_days(event)
            )
        )
        for event in events
    )

else:
    longest_event = None
    total_days = 0
    total_milestones = 0


col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌱 登録した「あの日」",
    f"{len(events)}個",
)

col2.metric(
    "📅 合計経過",
    f"{total_days:,}日",
)

col3.metric(
    "🏆 最長",
    (
        f"{elapsed_days(longest_event):,}日"
        if longest_event
        else "-"
    ),
)

col4.metric(
    "🎉 節目達成",
    f"{total_milestones}個",
)


if longest_event:
    st.info(
        "🏆 一番長く続いている物語："
        f"「{longest_event.get('title', '')}」"
        f" — {elapsed_days(longest_event):,}日"
    )


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "🌱 新しい「あの日」を登録"
)

with st.form(
    "new_event_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "🌱 何が始まった日？",
        placeholder=(
            "例：アプリ制作を始めた"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "📅 開始日",
            value=date.today(),
            max_value=date.today(),
        )

    with col2:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

    first_memo = st.text_area(
        "📝 あの日のひとこと",
        placeholder=(
            "例：ここから毎日作り始めた！"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🌱 あの日を登録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "何が始まった日か入力してね。"
            )

        else:
            event_id = add_event(
                data=data,
                title=title.strip(),
                category=category,
                start_date=start_date,
                first_memo=(
                    first_memo.strip()
                ),
            )

            st.session_state[
                "just_added_event"
            ] = event_id

            st.rerun()


# =========================================================
# 登録直後
# =========================================================

just_added = (
    st.session_state.pop(
        "just_added_event",
        None,
    )
)

if just_added:
    event = get_event(
        data,
        just_added,
    )

    if event:
        st.success(
            "🌱 新しい物語を登録しました！ "
            f"あの日から"
            f"{elapsed_days(event):,}日です。"
        )


# =========================================================
# あの日カード
# =========================================================

st.divider()

st.subheader(
    "📅 あの日から今日まで"
)

if not events:
    st.info(
        "まだ「あの日」がありません。"
    )

else:
    sorted_events = sorted(
        events,
        key=elapsed_days,
        reverse=True,
    )

    for event in sorted_events:
        event_id = event.get(
            "id",
            "",
        )

        days = elapsed_days(event)
        next_target = next_milestone(
            days
        )
        remaining = max(
            next_target - days,
            0,
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns([7, 1])
            )

            with col1:
                st.subheader(
                    event.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if event.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "event_favorite_"
                        + event_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        event_id,
                    )
                    st.rerun()

            st.caption(
                event.get(
                    "category",
                    "",
                )
                + " ｜ "
                + format_date(
                    event.get(
                        "start_date"
                    )
                )
                + "〜"
            )

            st.markdown(
                f"""
                <div class="day-number">
                    {days:,}日
                </div>
                <div class="soft-text">
                    あの日から
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "🗓️ 経過",
                human_elapsed(
                    event.get(
                        "start_date"
                    )
                ),
            )

            col2.metric(
                "⏰ 時間にすると",
                f"{elapsed_hours(event):,}時間",
            )

            st.write(
                f"🎯 **次の節目："
                f"{next_target:,}日**"
            )

            st.progress(
                milestone_progress(
                    days
                )
            )

            st.caption(
                f"あと {remaining:,}日"
            )

            reached = (
                reached_milestones(
                    days
                )
            )

            if reached:
                latest = max(reached)

                st.success(
                    f"🎉 {latest:,}日達成済み！"
                )

            if event.get(
                "first_memo"
            ):
                st.write(
                    "📝 **あの日のひとこと**"
                )
                st.write(
                    event.get(
                        "first_memo",
                        "",
                    )
                )

            event_notes = [
                note
                for note
                in progress_notes
                if note.get(
                    "event_id"
                )
                == event_id
            ]

            if event_notes:
                st.write(
                    "🌱 **途中経過**"
                )

                recent_notes = sorted(
                    event_notes,
                    key=lambda item: (
                        item.get(
                            "created_at",
                            "",
                        )
                    ),
                    reverse=True,
                )[:3]

                for note in recent_notes:
                    note_date = (
                        parse_date(
                            note.get(
                                "record_date"
                            )
                        )
                    )

                    start = parse_date(
                        event.get(
                            "start_date"
                        )
                    )

                    note_days = 0

                    if (
                        note_date
                        and start
                    ):
                        note_days = max(
                            (
                                note_date
                                - start
                            ).days,
                            0,
                        )

                    st.write(
                        f"**{note_days:,}日目** "
                        f"— {note.get('note', '')}"
                    )

            with st.expander(
                "📝 今の自分から追記"
            ):
                note_text = (
                    st.text_area(
                        "今の気持ち・変化",
                        key=(
                            "progress_note_"
                            + event_id
                        ),
                        placeholder=(
                            "例：思った以上に"
                            "続いている。"
                        ),
                    )
                )

                if st.button(
                    "🌱 途中経過を残す",
                    key=(
                        "add_note_"
                        + event_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        note_text.strip()
                    ):
                        st.warning(
                            "ひとこと入力してね。"
                        )

                    else:
                        add_progress_note(
                            data,
                            event_id,
                            note_text.strip(),
                        )

                        st.rerun()


# =========================================================
# マイルストーン
# =========================================================

if events:
    st.divider()

    st.subheader(
        "🎉 マイルストーン"
    )

    milestone_rows = []

    for event in events:
        days = elapsed_days(event)

        for milestone in (
            reached_milestones(days)
        ):
            start = parse_date(
                event.get(
                    "start_date"
                )
            )

            achieved_date = (
                start
                + timedelta(
                    days=milestone
                )
                if start
                else None
            )

            milestone_rows.append(
                {
                    "event": (
                        event.get(
                            "title",
                            "",
                        )
                    ),
                    "milestone": (
                        milestone
                    ),
                    "date": (
                        achieved_date
                    ),
                }
            )

    if milestone_rows:
        milestone_rows.sort(
            key=lambda item: (
                item["date"]
                or date.min
            ),
            reverse=True,
        )

        for item in (
            milestone_rows[:10]
        ):
            with st.container(
                border=True
            ):
                st.write(
                    f"🎉 **"
                    f"{item['milestone']:,}日達成！"
                    f"**"
                )

                st.write(
                    item["event"]
                )

                if item["date"]:
                    st.caption(
                        item[
                            "date"
                        ].strftime(
                            "%Y/%m/%d"
                        )
                    )

    else:
        st.caption(
            "最初の7日マイルストーンを"
            "目指してみよう。"
        )


# =========================================================
# 大切な「あの日」
# =========================================================

favorites = [
    event
    for event in events
    if event.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 大切な「あの日」"
    )

    for event in sorted(
        favorites,
        key=elapsed_days,
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            st.subheader(
                event.get(
                    "title",
                    "",
                )
            )

            st.metric(
                "あの日から",
                f"{elapsed_days(event):,}日",
            )

            st.caption(
                format_date(
                    event.get(
                        "start_date"
                    )
                )
                + " ｜ "
                + event.get(
                    "category",
                    "",
                )
            )

            if event.get(
                "first_memo"
            ):
                st.write(
                    event.get(
                        "first_memo",
                        "",
                    )
                )


# =========================================================
# この時期に始まったこと
# =========================================================

if events:
    st.divider()

    st.subheader(
        "🗓️ この時期に始まったこと"
    )

    today = date.today()
    anniversary_events = []

    for event in events:
        start = parse_date(
            event.get(
                "start_date"
            )
        )

        if not start:
            continue

        try:
            this_year = start.replace(
                year=today.year
            )
        except ValueError:
            # 2/29対策
            this_year = date(
                today.year,
                2,
                28,
            )

        distance = abs(
            (
                this_year - today
            ).days
        )

        if (
            distance <= 7
            and start.year
            < today.year
        ):
            anniversary_events.append(
                (
                    distance,
                    event,
                )
            )

    anniversary_events.sort(
        key=lambda item: item[0]
    )

    if anniversary_events:
        for _, event in (
            anniversary_events
        ):
            start = parse_date(
                event.get(
                    "start_date"
                )
            )

            years = (
                today.year
                - start.year
            )

            with st.container(
                border=True
            ):
                st.write(
                    f"🌱 **"
                    f"{event.get('title', '')}"
                    f"**"
                )

                st.write(
                    f"{years}年前の"
                    "この時期に始まりました。"
                )

                st.caption(
                    format_date(
                        event.get(
                            "start_date"
                        )
                    )
                )

    else:
        st.caption(
            "前後7日以内に始まった"
            "過去の出来事はありません。"
        )


# =========================================================
# ランダム「あの日」
# =========================================================

if events:
    st.divider()

    st.subheader(
        "🎲 今日の「あの日」"
    )

    if (
        "random_event_id"
        not in st.session_state
        or not get_event(
            data,
            st.session_state[
                "random_event_id"
            ],
        )
    ):
        st.session_state[
            "random_event_id"
        ] = random.choice(
            events
        ).get("id")

    random_event = get_event(
        data,
        st.session_state[
            "random_event_id"
        ],
    )

    if random_event:
        with st.container(
            border=True
        ):
            st.subheader(
                random_event.get(
                    "title",
                    "",
                )
            )

            st.metric(
                "あの日から",
                f"{elapsed_days(random_event):,}日",
            )

            st.caption(
                format_date(
                    random_event.get(
                        "start_date"
                    )
                )
            )

            if random_event.get(
                "first_memo"
            ):
                st.write(
                    "📝 **最初のメモ**"
                )
                st.write(
                    random_event.get(
                        "first_memo",
                        "",
                    )
                )

        if st.button(
            "🎲 別の「あの日」を見る",
            use_container_width=True,
        ):
            st.session_state[
                "random_event_id"
            ] = random.choice(
                events
            ).get("id")

            st.rerun()


# =========================================================
# タイムライン
# =========================================================

if events:
    st.divider()

    st.subheader(
        "📖 自分のタイムライン"
    )

    timeline_events = sorted(
        events,
        key=lambda event: (
            event.get(
                "start_date",
                "",
            )
        ),
    )

    previous_date = None

    for event in timeline_events:
        current_date = parse_date(
            event.get(
                "start_date"
            )
        )

        if (
            previous_date
            and current_date
        ):
            gap = (
                current_date
                - previous_date
            ).days

            st.caption(
                f"│　{gap:,}日"
            )

        st.write(
            "🌱 **"
            + event.get(
                "title",
                "",
            )
            + "**"
        )

        st.caption(
            format_date(
                event.get(
                    "start_date"
                )
            )
            + " ｜ "
            + event.get(
                "category",
                "",
            )
        )

        previous_date = (
            current_date
        )

    st.caption("│")
    st.write(
        f"▼ **今日 "
        f"{date.today().strftime('%Y/%m/%d')}**"
    )


# =========================================================
# あの日図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 あの日図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "アプリ、勉強、仕事……"
    ),
)

category_filter = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="library_category",
)

filtered_events = []

for event in events:
    if (
        category_filter
        != "すべて"
        and event.get(
            "category"
        )
        != category_filter
    ):
        continue

    searchable = " ".join(
        [
            event.get(
                "title",
                "",
            ),
            event.get(
                "category",
                "",
            ),
            event.get(
                "first_memo",
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

    filtered_events.append(event)


if not filtered_events:
    st.info(
        "条件に合う「あの日」はありません。"
    )

else:
    library_rows = []

    for event in sorted(
        filtered_events,
        key=elapsed_days,
        reverse=True,
    ):
        days = elapsed_days(event)

        library_rows.append(
            {
                "あの日": event.get(
                    "title",
                    "",
                ),
                "カテゴリー": event.get(
                    "category",
                    "",
                ),
                "開始日": format_date(
                    event.get(
                        "start_date"
                    )
                ),
                "経過": f"{days:,}日",
                "次の節目": (
                    f"{next_milestone(days):,}日"
                ),
                "⭐": (
                    "⭐"
                    if event.get(
                        "favorite",
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
# 途中経過一覧
# =========================================================

if progress_notes:
    st.divider()

    st.subheader(
        "📝 これまでの途中経過"
    )

    sorted_notes = sorted(
        progress_notes,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for note in sorted_notes:
        event = get_event(
            data,
            note.get(
                "event_id"
            ),
        )

        if not event:
            continue

        with st.container(
            border=True
        ):
            st.write(
                "🌱 **"
                + event.get(
                    "title",
                    "",
                )
                + "**"
            )

            st.write(
                note.get(
                    "note",
                    "",
                )
            )

            st.caption(
                note.get(
                    "record_date",
                    ""
                )
            )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・管理"
):
    if not events:
        st.caption(
            "まだ「あの日」がありません。"
        )

    for event in sorted(
        events,
        key=lambda item: (
            item.get(
                "start_date",
                "",
            )
        ),
        reverse=True,
    ):
        event_id = event.get(
            "id",
            "",
        )

        with st.expander(
            format_date(
                event.get(
                    "start_date"
                )
            )
            + " ｜ "
            + event.get(
                "title",
                "",
            )
        ):
            edit_title = st.text_input(
                "何が始まった日？",
                value=event.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + event_id
                ),
            )

            old_category = event.get(
                "category",
                "✨ その他",
            )

            category_index = (
                CATEGORIES.index(
                    old_category
                )
                if old_category
                in CATEGORIES
                else len(
                    CATEGORIES
                ) - 1
            )

            edit_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=category_index,
                    key=(
                        "edit_category_"
                        + event_id
                    ),
                )
            )

            parsed_start = parse_date(
                event.get(
                    "start_date"
                )
            ) or date.today()

            edit_start_date = (
                st.date_input(
                    "開始日",
                    value=parsed_start,
                    max_value=date.today(),
                    key=(
                        "edit_date_"
                        + event_id
                    ),
                )
            )

            edit_first_memo = (
                st.text_area(
                    "あの日のひとこと",
                    value=event.get(
                        "first_memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + event_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_event_"
                        + event_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "タイトルを入力してね。"
                        )

                    else:
                        update_event(
                            data=data,
                            event_id=event_id,
                            title=(
                                edit_title.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            start_date=(
                                edit_start_date
                            ),
                            first_memo=(
                                edit_first_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ 大切な日から外す"
                    if event.get(
                        "favorite",
                        False,
                    )
                    else "☆ 大切な日にする"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_favorite_"
                        + event_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        event_id,
                    )
                    st.rerun()

            event_notes = [
                note
                for note
                in progress_notes
                if note.get(
                    "event_id"
                )
                == event_id
            ]

            if event_notes:
                st.markdown(
                    "#### 📝 途中経過の管理"
                )

                for note in sorted(
                    event_notes,
                    key=lambda item: (
                        item.get(
                            "created_at",
                            "",
                        )
                    ),
                    reverse=True,
                ):
                    note_id = note.get(
                        "id",
                        "",
                    )

                    col1, col2 = (
                        st.columns([5, 1])
                    )

                    with col1:
                        st.write(
                            note.get(
                                "record_date",
                                "",
                            )
                            + " ｜ "
                            + note.get(
                                "note",
                                "",
                            )
                        )

                    with col2:
                        if st.button(
                            "🗑️",
                            key=(
                                "delete_note_"
                                + note_id
                            ),
                        ):
                            delete_progress_note(
                                data,
                                note_id,
                            )
                            st.rerun()

            confirm_delete = (
                st.checkbox(
                    "この「あの日」と"
                    "途中経過を削除する",
                    key=(
                        "confirm_delete_"
                        + event_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_event_"
                    + event_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_event(
                    data,
                    event_id,
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
            "since_that_day_"
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
    "🌱 あの日に始まったことは、"
    "今日の自分につながっている。"
)
