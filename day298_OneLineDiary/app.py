import calendar
import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日のひとこと日記",
    page_icon="📝",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "diary.json",
)

MOODS = [
    "記録しない",
    "😄",
    "😊",
    "😐",
    "😔",
    "😫",
]

MOOD_ONLY = [
    "😄",
    "😊",
    "😐",
    "😔",
    "😫",
]

MAX_LENGTH = 100


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


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


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d"
    )


def days_ago_text(
    target_date,
):
    if not target_date:
        return "-"

    days = (
        date.today()
        - target_date
    ).days

    if days == 0:
        return "今日"

    if days == 1:
        return "昨日"

    return f"{days}日前"


# =========================================================
# データ管理
# =========================================================

def empty_data():
    return {
        "entries": [],
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

    if not os.path.exists(
        DATA_FILE
    ):
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

        if not isinstance(
            data,
            dict,
        ):
            data = empty_data()

        data.setdefault(
            "entries",
            [],
        )

        for entry in data[
            "entries"
        ]:
            if not entry.get("id"):
                entry["id"] = (
                    create_id()
                )

            entry.setdefault(
                "date",
                today_text(),
            )
            entry.setdefault(
                "text",
                "",
            )
            entry.setdefault(
                "mood",
                "",
            )
            entry.setdefault(
                "favorite",
                False,
            )
            entry.setdefault(
                "created_at",
                now_text(),
            )
            entry.setdefault(
                "updated_at",
                entry.get(
                    "created_at",
                    now_text(),
                ),
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
# 取得
# =========================================================

def get_entry(
    data,
    entry_id,
):
    return next(
        (
            entry
            for entry
            in data["entries"]
            if entry.get("id")
            == entry_id
        ),
        None,
    )


def entry_for_date(
    data,
    target_date,
):
    target_text = str(
        target_date
    )

    return next(
        (
            entry
            for entry
            in data["entries"]
            if entry.get(
                "date"
            ) == target_text
        ),
        None,
    )


def sorted_entries(
    data,
    reverse=False,
):
    return sorted(
        data["entries"],
        key=lambda row: (
            row.get(
                "date",
                "",
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
        reverse=reverse,
    )


# =========================================================
# CRUD
# =========================================================

def add_entry(
    data,
    entry_date,
    text,
    mood,
):
    if entry_for_date(
        data,
        entry_date,
    ):
        return False

    entry = {
        "id": create_id(),
        "date": str(
            entry_date
        ),
        "text": text,
        "mood": (
            ""
            if mood
            == "記録しない"
            else mood
        ),
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["entries"].append(
        entry
    )

    save_data(data)

    return True


def update_entry(
    data,
    entry_id,
    new_date,
    text,
    mood,
):
    entry = get_entry(
        data,
        entry_id,
    )

    if not entry:
        return False, (
            "記録が見つかりません。"
        )

    duplicate = entry_for_date(
        data,
        new_date,
    )

    if (
        duplicate
        and duplicate.get(
            "id"
        ) != entry_id
    ):
        return False, (
            "この日にはすでに"
            "一行あります。"
        )

    entry["date"] = str(
        new_date
    )
    entry["text"] = text
    entry["mood"] = (
        ""
        if mood
        == "記録しない"
        else mood
    )
    entry[
        "updated_at"
    ] = now_text()

    save_data(data)

    return True, ""


def toggle_favorite(
    data,
    entry_id,
):
    entry = get_entry(
        data,
        entry_id,
    )

    if not entry:
        return

    entry[
        "favorite"
    ] = not entry.get(
        "favorite",
        False,
    )

    entry[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_entry(
    data,
    entry_id,
):
    data["entries"] = [
        entry
        for entry
        in data["entries"]
        if entry.get("id")
        != entry_id
    ]

    save_data(data)


# =========================================================
# 連続記録
# =========================================================

def unique_dates(
    entries,
):
    result = set()

    for entry in entries:
        parsed = parse_date(
            entry.get(
                "date"
            )
        )

        if parsed:
            result.add(parsed)

    return result


def current_streak(
    entries,
):
    dates = unique_dates(
        entries
    )

    if not dates:
        return 0

    today = date.today()

    if today in dates:
        cursor = today

    elif (
        today
        - timedelta(days=1)
    ) in dates:
        cursor = (
            today
            - timedelta(days=1)
        )

    else:
        return 0

    streak = 0

    while cursor in dates:
        streak += 1
        cursor -= timedelta(
            days=1
        )

    return streak


def longest_streak(
    entries,
):
    dates = sorted(
        unique_dates(entries)
    )

    if not dates:
        return 0

    longest = 1
    current = 1

    for index in range(
        1,
        len(dates),
    ):
        if (
            dates[index]
            - dates[index - 1]
        ).days == 1:
            current += 1
            longest = max(
                longest,
                current,
            )

        else:
            current = 1

    return longest


def days_since_last_entry(
    entries,
):
    dates = sorted(
        unique_dates(entries)
    )

    if not dates:
        return None

    return (
        date.today()
        - dates[-1]
    ).days


# =========================================================
# 月・年集計
# =========================================================

def entries_for_month(
    entries,
    year,
    month,
):
    result = []

    for entry in entries:
        parsed = parse_date(
            entry.get(
                "date"
            )
        )

        if (
            parsed
            and parsed.year == year
            and parsed.month == month
        ):
            result.append(entry)

    return sorted(
        result,
        key=lambda row: row.get(
            "date",
            "",
        ),
    )


def entries_for_year(
    entries,
    year,
):
    result = []

    for entry in entries:
        parsed = parse_date(
            entry.get(
                "date"
            )
        )

        if (
            parsed
            and parsed.year == year
        ):
            result.append(entry)

    return sorted(
        result,
        key=lambda row: row.get(
            "date",
            "",
        ),
    )


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
        background: rgba(100, 110, 190, 0.07);
        border: 1px solid rgba(100, 110, 190, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(100, 110, 200, 0.17),
                rgba(180, 120, 200, 0.11)
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

    .today-line {
        padding: 28px;
        border-radius: 22px;
        background: rgba(100, 110, 190, 0.07);
        border: 1px solid rgba(100, 110, 190, 0.16);
        font-size: 1.15rem;
        margin: 14px 0;
    }

    .old-line {
        padding: 20px;
        border-radius: 18px;
        background: rgba(120, 120, 180, 0.06);
        border: 1px solid rgba(120, 120, 180, 0.14);
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()
entries = data["entries"]

today = date.today()

today_entry = entry_for_date(
    data,
    today,
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📝 今日のひとこと日記</h1>
        <p>
            今日を、一行だけ残す。
            長い日記じゃなくていい。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日の一行
# =========================================================

st.subheader(
    f"🌙 {today.strftime('%Y年%m月%d日')}"
)

gap = days_since_last_entry(
    entries
)

if (
    not today_entry
    and gap is not None
    and gap >= 2
):
    st.info(
        f"{gap}日ぶりですね。\n\n"
        "🌱 また今日から、一行。"
    )


if not today_entry:
    with st.form(
        "today_form"
    ):
        today_line = st.text_area(
            "今日をひとことで言うなら？",
            max_chars=MAX_LENGTH,
            height=100,
            placeholder=(
                "例：298本目の"
                "アプリを作った。"
            ),
        )

        st.caption(
            f"最大{MAX_LENGTH}文字。"
            "一行だけでOK。"
        )

        mood = st.selectbox(
            "😊 今日の気分（任意）",
            MOODS,
        )

        submitted = (
            st.form_submit_button(
                "🌙 今日を残す",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            clean_text = (
                today_line.strip()
            )

            if not clean_text:
                st.warning(
                    "今日の一行を書いてね。"
                )

            elif (
                len(clean_text)
                > MAX_LENGTH
            ):
                st.warning(
                    f"{MAX_LENGTH}文字以内で"
                    "書いてね。"
                )

            else:
                added = add_entry(
                    data=data,
                    entry_date=today,
                    text=clean_text,
                    mood=mood,
                )

                if added:
                    st.session_state[
                        "just_saved_today"
                    ] = True
                    st.rerun()


else:
    st.markdown(
        '<div class="today-line">',
        unsafe_allow_html=True,
    )

    if today_entry.get(
        "mood"
    ):
        st.write(
            today_entry.get(
                "mood"
            )
        )

    st.write(
        f"「{today_entry.get('text', '')}」"
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            (
                "⭐ 大切な一行から外す"
                if today_entry.get(
                    "favorite",
                    False,
                )
                else "☆ 大切な一行にする"
            ),
            key="today_favorite",
            use_container_width=True,
        ):
            toggle_favorite(
                data,
                today_entry.get(
                    "id"
                ),
            )

            st.rerun()

    with col2:
        if st.button(
            "✏️ 今日を書き直す",
            use_container_width=True,
        ):
            st.session_state[
                "edit_today"
            ] = not st.session_state.get(
                "edit_today",
                False,
            )


    if st.session_state.get(
        "edit_today",
        False,
    ):
        current_mood = (
            today_entry.get(
                "mood"
            )
            or "記録しない"
        )

        mood_index = (
            MOODS.index(
                current_mood
            )
            if current_mood
            in MOODS
            else 0
        )

        with st.form(
            "edit_today_form"
        ):
            edited_text = st.text_area(
                "今日の一行",
                value=today_entry.get(
                    "text",
                    "",
                ),
                max_chars=MAX_LENGTH,
                height=100,
            )

            edited_mood = (
                st.selectbox(
                    "気分",
                    MOODS,
                    index=mood_index,
                )
            )

            submitted = (
                st.form_submit_button(
                    "💾 書き直す",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                clean_text = (
                    edited_text.strip()
                )

                if not clean_text:
                    st.warning(
                        "一行を書いてね。"
                    )

                else:
                    success, message = (
                        update_entry(
                            data=data,
                            entry_id=(
                                today_entry.get(
                                    "id"
                                )
                            ),
                            new_date=today,
                            text=clean_text,
                            mood=edited_mood,
                        )
                    )

                    if success:
                        st.session_state[
                            "edit_today"
                        ] = False
                        st.rerun()

                    else:
                        st.warning(
                            message
                        )


# =========================================================
# 保存直後
# =========================================================

if st.session_state.get(
    "just_saved_today",
    False,
):
    st.success(
        "🌙 今日の一行を残しました。"
    )

    del st.session_state[
        "just_saved_today"
    ]


# =========================================================
# ダッシュボード
# =========================================================

st.divider()

st.subheader(
    "📖 一行の積み重ね"
)

year_entries = entries_for_year(
    entries,
    today.year,
)

days_elapsed = (
    today
    - date(
        today.year,
        1,
        1,
    )
).days + 1

year_rate = (
    len(year_entries)
    / days_elapsed
    * 100
    if days_elapsed
    else 0
)

current = current_streak(
    entries
)

longest = longest_streak(
    entries
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📝 全記録",
    f"{len(entries)}日",
)

col2.metric(
    f"📅 {today.year}年",
    f"{len(year_entries)}日",
)

col3.metric(
    "🔥 現在の連続",
    f"{current}日",
)

col4.metric(
    "🏆 最長連続",
    f"{longest}日",
)

st.caption(
    f"今年の記録率："
    f"{year_rate:.0f}%"
)

if current == 0 and entries:
    st.caption(
        "🌱 連続記録はゼロでも大丈夫。"
        "また今日から一行。"
    )


# =========================================================
# 昔の今日
# =========================================================

st.divider()

st.subheader(
    "🕰️ 昔の自分"
)

memory_targets = [
    (
        "🕰️ 30日前",
        today
        - timedelta(days=30),
    ),
    (
        "🍂 半年前",
        today
        - timedelta(days=182),
    ),
]

try:
    one_year_ago = today.replace(
        year=today.year - 1
    )

except ValueError:
    one_year_ago = date(
        today.year - 1,
        2,
        28,
    )

memory_targets.append(
    (
        "🎂 1年前の今日",
        one_year_ago,
    )
)

found_memory = False

for label, target in memory_targets:
    memory = entry_for_date(
        data,
        target,
    )

    if not memory:
        continue

    found_memory = True

    with st.container(
        border=True
    ):
        st.caption(
            label
            + " ｜ "
            + format_date(
                memory.get(
                    "date"
                )
            )
        )

        if memory.get(
            "mood"
        ):
            st.write(
                memory.get(
                    "mood"
                )
            )

        st.write(
            f"「{memory.get('text', '')}」"
        )

if not found_memory:
    st.caption(
        "まだ表示できる昔の一行は"
        "ありません。"
        "記録が増えると、"
        "ここで昔の自分に会えます。"
    )


# =========================================================
# ランダムな一日
# =========================================================

old_entries = [
    entry
    for entry in entries
    if (
        parse_date(
            entry.get(
                "date"
            )
        )
        and parse_date(
            entry.get(
                "date"
            )
        ) < today
    )
]

if old_entries:
    st.divider()

    st.subheader(
        "🎲 ある日の自分"
    )

    old_ids = [
        entry.get("id")
        for entry in old_entries
    ]

    random_id = (
        st.session_state.get(
            "random_diary_id"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_diary_id"
        ] = random_id

    random_entry = get_entry(
        data,
        random_id,
    )

    if random_entry:
        random_date = parse_date(
            random_entry.get(
                "date"
            )
        )

        with st.container(
            border=True
        ):
            st.caption(
                "🎲 "
                + days_ago_text(
                    random_date
                )
                + " ｜ "
                + format_date(
                    random_entry.get(
                        "date"
                    )
                )
            )

            if random_entry.get(
                "mood"
            ):
                st.write(
                    random_entry.get(
                        "mood"
                    )
                )

            st.write(
                f"「{random_entry.get('text', '')}」"
            )

        if st.button(
            "🎲 別の日を見る",
            use_container_width=True,
        ):
            alternatives = [
                entry_id
                for entry_id
                in old_ids
                if entry_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_diary_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 月間カレンダー
# =========================================================

st.divider()

st.subheader(
    "📅 月の記録"
)

available_years = sorted(
    {
        parsed.year
        for entry in entries
        if (
            parsed := parse_date(
                entry.get(
                    "date"
                )
            )
        )
    }
    | {today.year},
    reverse=True,
)

col1, col2 = st.columns(2)

with col1:
    calendar_year = st.selectbox(
        "年",
        available_years,
        index=(
            available_years.index(
                today.year
            )
            if today.year
            in available_years
            else 0
        ),
        key="calendar_year",
    )

with col2:
    calendar_month = (
        st.selectbox(
            "月",
            list(
                range(1, 13)
            ),
            index=(
                today.month - 1
            ),
            format_func=lambda x: (
                f"{x}月"
            ),
            key="calendar_month",
        )
    )

month_entries = entries_for_month(
    entries,
    calendar_year,
    calendar_month,
)

month_entry_dates = {
    parse_date(
        entry.get(
            "date"
        )
    )
    for entry in month_entries
}

days_in_month = calendar.monthrange(
    calendar_year,
    calendar_month,
)[1]

if (
    calendar_year == today.year
    and calendar_month == today.month
):
    possible_days = today.day

elif date(
    calendar_year,
    calendar_month,
    1,
) > today:
    possible_days = 0

else:
    possible_days = days_in_month

month_rate = (
    len(month_entries)
    / possible_days
    * 100
    if possible_days > 0
    else 0
)

c1, c2 = st.columns(2)

c1.metric(
    "📝 記録",
    f"{len(month_entries)}日",
)

c2.metric(
    "📊 記録率",
    f"{month_rate:.0f}%",
)

calendar_rows = []

for day_number in range(
    1,
    days_in_month + 1,
):
    target = date(
        calendar_year,
        calendar_month,
        day_number,
    )

    if target > today:
        mark = "－"

    elif target in month_entry_dates:
        mark = "●"

    else:
        mark = "○"

    calendar_rows.append(
        {
            "日": day_number,
            "記録": mark,
        }
    )

calendar_df = pd.DataFrame(
    calendar_rows
)

calendar_df["週"] = (
    (calendar_df.index // 7)
    + 1
)

calendar_view = (
    calendar_df
    .groupby("週")["記録"]
    .apply(
        lambda values: " ".join(
            values
        )
    )
)

for week_number, marks in (
    calendar_view.items()
):
    st.caption(
        f"第{week_number}週　{marks}"
    )

st.caption(
    "● 書いた日　○ 空白の日　－ 未来"
)

if month_entries:
    st.markdown(
        "#### 🌙 この月の一行"
    )

    for entry in month_entries:
        mood_text = (
            entry.get(
                "mood"
            )
            + " "
            if entry.get(
                "mood"
            )
            else ""
        )

        st.write(
            f"**{format_date(entry.get('date'))}** "
            f"{mood_text}"
            f"「{entry.get('text', '')}」"
        )


# =========================================================
# 気分
# =========================================================

mood_entries = [
    entry
    for entry in month_entries
    if entry.get(
        "mood"
    ) in MOOD_ONLY
]

if mood_entries:
    st.divider()

    st.subheader(
        "😊 この月の気分"
    )

    mood_counts = Counter(
        entry.get(
            "mood"
        )
        for entry in mood_entries
    )

    mood_df = pd.DataFrame(
        {
            "気分": MOOD_ONLY,
            "日数": [
                mood_counts.get(
                    mood,
                    0,
                )
                for mood in MOOD_ONLY
            ],
        }
    ).set_index(
        "気分"
    )

    st.bar_chart(
        mood_df
    )

    top_mood = max(
        MOOD_ONLY,
        key=lambda mood: (
            mood_counts.get(
                mood,
                0,
            )
        ),
    )

    st.caption(
        f"{calendar_month}月は"
        f"「{top_mood}」の日が"
        "一番多かったようです。"
    )


# =========================================================
# 年間 365行
# =========================================================

st.divider()

st.subheader(
    "📖 365行の一年"
)

year_choice = st.selectbox(
    "振り返る年",
    available_years,
    key="year_book",
)

book_entries = entries_for_year(
    entries,
    year_choice,
)

if not book_entries:
    st.info(
        "この年の一行は"
        "まだありません。"
    )

else:
    month_counts = []

    for month in range(
        1,
        13,
    ):
        month_items = [
            entry
            for entry in book_entries
            if (
                parse_date(
                    entry.get(
                        "date"
                    )
                ).month
                == month
            )
        ]

        month_counts.append(
            {
                "月": f"{month}月",
                "記録日数": len(
                    month_items
                ),
            }
        )

    st.bar_chart(
        pd.DataFrame(
            month_counts
        ).set_index(
            "月"
        )
    )

    for month in range(
        1,
        13,
    ):
        month_items = [
            entry
            for entry in book_entries
            if (
                parse_date(
                    entry.get(
                        "date"
                    )
                ).month
                == month
            )
        ]

        if not month_items:
            continue

        with st.expander(
            f"🌙 {month}月 "
            f"— {len(month_items)}行"
        ):
            for entry in month_items:
                parsed = parse_date(
                    entry.get(
                        "date"
                    )
                )

                mood = (
                    entry.get(
                        "mood"
                    )
                    or ""
                )

                favorite = (
                    " ⭐"
                    if entry.get(
                        "favorite",
                        False,
                    )
                    else ""
                )

                st.write(
                    f"**{parsed.strftime('%m/%d')}** "
                    f"{mood} "
                    f"「{entry.get('text', '')}」"
                    f"{favorite}"
                )


# =========================================================
# 大切な一行
# =========================================================

favorites = [
    entry
    for entry in entries
    if entry.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 大切な一行"
    )

    for entry in sorted(
        favorites,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    ):
        st.write(
            f"**{format_date(entry.get('date'))}** "
            f"{entry.get('mood', '')} "
            f"「{entry.get('text', '')}」"
        )


# =========================================================
# 一行図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 一行図鑑"
)

search_text = st.text_input(
    "🔎 一行を検索",
    placeholder=(
        "Python、アプリ、楽しかった……"
    ),
)

filter_col1, filter_col2 = (
    st.columns(2)
)

with filter_col1:
    year_filter_options = (
        ["すべて"]
        + [
            str(year)
            for year
            in available_years
        ]
    )

    year_filter = st.selectbox(
        "年",
        year_filter_options,
        key="library_year",
    )

with filter_col2:
    mood_filter = st.selectbox(
        "気分",
        ["すべて"]
        + MOOD_ONLY
        + ["未記録"],
        key="library_mood",
    )

favorite_filter = st.checkbox(
    "⭐ 大切な一行だけ",
    key="library_favorite",
)

filtered_entries = []

for entry in entries:
    parsed = parse_date(
        entry.get(
            "date"
        )
    )

    if not parsed:
        continue

    if (
        year_filter
        != "すべて"
        and str(
            parsed.year
        ) != year_filter
    ):
        continue

    if (
        mood_filter
        in MOOD_ONLY
        and entry.get(
            "mood"
        ) != mood_filter
    ):
        continue

    if (
        mood_filter
        == "未記録"
        and entry.get(
            "mood"
        )
    ):
        continue

    if (
        favorite_filter
        and not entry.get(
            "favorite",
            False,
        )
    ):
        continue

    if (
        search_text.strip()
        and search_text
        .strip()
        .lower()
        not in entry.get(
            "text",
            ""
        ).lower()
    ):
        continue

    filtered_entries.append(
        entry
    )

if not filtered_entries:
    st.info(
        "条件に合う一行は"
        "ありません。"
    )

else:
    rows = []

    for entry in sorted(
        filtered_entries,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    ):
        rows.append(
            {
                "日付": format_date(
                    entry.get(
                        "date"
                    )
                ),
                "一行": entry.get(
                    "text",
                    "",
                ),
                "気分": (
                    entry.get(
                        "mood"
                    )
                    or "-"
                ),
                "⭐": (
                    "⭐"
                    if entry.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            rows
        ),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・削除"
):
    if not entries:
        st.caption(
            "まだ一行がありません。"
        )

    else:
        edit_options = {}

        for entry in sorted(
            entries,
            key=lambda row: row.get(
                "date",
                "",
            ),
            reverse=True,
        ):
            short_text = entry.get(
                "text",
                "",
            )

            if len(short_text) > 25:
                short_text = (
                    short_text[:25]
                    + "…"
                )

            label = (
                f"{format_date(entry.get('date'))}"
                f" ｜ {short_text}"
            )

            edit_options[
                label
            ] = entry.get(
                "id"
            )

        selected_label = (
            st.selectbox(
                "編集する一行",
                list(
                    edit_options.keys()
                ),
            )
        )

        selected_id = (
            edit_options[
                selected_label
            ]
        )

        selected = get_entry(
            data,
            selected_id,
        )

        if selected:
            selected_date = (
                parse_date(
                    selected.get(
                        "date"
                    )
                )
                or today
            )

            edit_date = st.date_input(
                "日付",
                value=selected_date,
                max_value=today,
                key=(
                    "edit_date_"
                    + selected_id
                ),
            )

            edit_text = st.text_area(
                "一行",
                value=selected.get(
                    "text",
                    "",
                ),
                max_chars=MAX_LENGTH,
                height=100,
                key=(
                    "edit_text_"
                    + selected_id
                ),
            )

            current_mood = (
                selected.get(
                    "mood"
                )
                or "記録しない"
            )

            mood_index = (
                MOODS.index(
                    current_mood
                )
                if current_mood
                in MOODS
                else 0
            )

            edit_mood = st.selectbox(
                "気分",
                MOODS,
                index=mood_index,
                key=(
                    "edit_mood_"
                    + selected_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + selected_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    clean_text = (
                        edit_text.strip()
                    )

                    if not clean_text:
                        st.warning(
                            "一行を書いてね。"
                        )

                    else:
                        success, message = (
                            update_entry(
                                data=data,
                                entry_id=(
                                    selected_id
                                ),
                                new_date=(
                                    edit_date
                                ),
                                text=clean_text,
                                mood=(
                                    edit_mood
                                ),
                            )
                        )

                        if success:
                            st.rerun()

                        else:
                            st.warning(
                                message
                            )

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if selected.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_favorite_"
                        + selected_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        selected_id,
                    )

                    st.rerun()

            st.divider()

            st.markdown(
                "#### 🗑️ この一行を削除"
            )

            delete_confirm = (
                st.checkbox(
                    "削除する",
                    key=(
                        "delete_confirm_"
                        + selected_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_entry_"
                    + selected_id
                ),
                disabled=(
                    not delete_confirm
                ),
                use_container_width=True,
            ):
                delete_entry(
                    data,
                    selected_id,
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
            "one_line_diary_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "📝 長い日記はいらない。"
    "今日を思い出せる一行が"
    "あればいい。"
)

st.caption(
    "🌙 365日後、"
    "その一行一行が、"
    "あなたの一年になる。"
)
