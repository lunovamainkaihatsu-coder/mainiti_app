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
    page_title="未来の自分に預ける",
    page_icon="📮",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "letters.json",
)

CATEGORIES = [
    "🌱 成長",
    "🚀 夢・目標",
    "💼 仕事",
    "💰 お金",
    "👨‍👩‍👧 家族",
    "❤️ 自分",
    "🎨 創作",
    "🎁 楽しみ",
    "✨ その他",
]


# =========================================================
# 共通関数
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


def days_until(value):
    target = parse_date(value)

    if not target:
        return None

    return (
        target
        - date.today()
    ).days


def travel_days(letter):
    sent = parse_date(
        letter.get(
            "sent_date"
        )
    )

    open_date = parse_date(
        letter.get(
            "open_date"
        )
    )

    if not sent or not open_date:
        return 0

    return max(
        (
            open_date
            - sent
        ).days,
        0,
    )


def human_countdown(days):
    if days is None:
        return "-"

    if days < 0:
        return "開封できます"

    if days == 0:
        return "今日"

    if days == 1:
        return "あと1日"

    if days < 30:
        return f"あと{days}日"

    if days < 365:
        months = days // 30
        rest = days % 30

        if rest == 0:
            return (
                f"あと約{months}か月"
            )

        return (
            f"あと約{months}か月"
            f"{rest}日"
        )

    years = days // 365
    rest_days = days % 365
    months = rest_days // 30

    if months:
        return (
            f"あと約{years}年"
            f"{months}か月"
        )

    return f"あと約{years}年"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "letters": [],
        "replies": [],
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
            "letters",
            [],
        )
        data.setdefault(
            "replies",
            [],
        )

        for letter in data[
            "letters"
        ]:
            if not letter.get("id"):
                letter["id"] = (
                    create_id()
                )

            if not letter.get(
                "thread_id"
            ):
                letter[
                    "thread_id"
                ] = letter["id"]

            letter.setdefault(
                "parent_letter_id",
                None,
            )
            letter.setdefault(
                "title",
                "",
            )
            letter.setdefault(
                "message",
                "",
            )
            letter.setdefault(
                "category",
                "✨ その他",
            )
            letter.setdefault(
                "sent_date",
                today_text(),
            )
            letter.setdefault(
                "open_date",
                today_text(),
            )
            letter.setdefault(
                "read",
                False,
            )
            letter.setdefault(
                "favorite",
                False,
            )
            letter.setdefault(
                "created_at",
                now_text(),
            )
            letter.setdefault(
                "updated_at",
                letter.get(
                    "created_at",
                    now_text(),
                ),
            )

        for reply in data[
            "replies"
        ]:
            if not reply.get("id"):
                reply["id"] = (
                    create_id()
                )

            reply.setdefault(
                "letter_id",
                "",
            )
            reply.setdefault(
                "message",
                "",
            )
            reply.setdefault(
                "reply_date",
                today_text(),
            )
            reply.setdefault(
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
# 取得
# =========================================================

def get_letter(
    data,
    letter_id,
):
    return next(
        (
            letter
            for letter
            in data["letters"]
            if letter.get("id")
            == letter_id
        ),
        None,
    )


def get_reply(
    data,
    letter_id,
):
    replies = [
        reply
        for reply
        in data["replies"]
        if reply.get(
            "letter_id"
        ) == letter_id
    ]

    if not replies:
        return None

    replies.sort(
        key=lambda row: row.get(
            "created_at",
            "",
        )
    )

    return replies[-1]


def get_thread_letters(
    data,
    thread_id,
):
    letters = [
        letter
        for letter
        in data["letters"]
        if letter.get(
            "thread_id"
        ) == thread_id
    ]

    return sorted(
        letters,
        key=lambda row: (
            row.get(
                "sent_date",
                "",
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
    )


def is_available(letter):
    open_date = parse_date(
        letter.get(
            "open_date"
        )
    )

    if not open_date:
        return False

    return date.today() >= open_date


def is_locked(letter):
    return not is_available(
        letter
    )


def thread_count(data):
    return len(
        {
            letter.get(
                "thread_id"
            )
            for letter
            in data["letters"]
            if letter.get(
                "thread_id"
            )
        }
    )


# =========================================================
# CRUD
# =========================================================

def add_letter(
    data,
    title,
    message,
    category,
    open_date,
    thread_id=None,
    parent_letter_id=None,
):
    letter_id = create_id()

    if not thread_id:
        thread_id = letter_id

    item = {
        "id": letter_id,
        "thread_id": thread_id,
        "parent_letter_id": (
            parent_letter_id
        ),
        "title": title,
        "message": message,
        "category": category,
        "sent_date": today_text(),
        "open_date": str(
            open_date
        ),
        "read": False,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["letters"].append(
        item
    )

    save_data(data)


def mark_read(
    data,
    letter_id,
):
    letter = get_letter(
        data,
        letter_id,
    )

    if not letter:
        return

    if not is_available(
        letter
    ):
        return

    letter["read"] = True
    letter[
        "updated_at"
    ] = now_text()

    save_data(data)


def add_reply(
    data,
    letter_id,
    message,
):
    existing = get_reply(
        data,
        letter_id,
    )

    if existing:
        return False

    reply = {
        "id": create_id(),
        "letter_id": letter_id,
        "message": message,
        "reply_date": today_text(),
        "created_at": now_text(),
    }

    data["replies"].append(
        reply
    )

    save_data(data)

    return True


def toggle_favorite(
    data,
    letter_id,
):
    letter = get_letter(
        data,
        letter_id,
    )

    if not letter:
        return

    letter[
        "favorite"
    ] = not letter.get(
        "favorite",
        False,
    )

    letter[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_locked_letter(
    data,
    letter_id,
    title,
    category,
    open_date,
):
    letter = get_letter(
        data,
        letter_id,
    )

    if not letter:
        return False

    if is_available(
        letter
    ):
        return False

    current_open = parse_date(
        letter.get(
            "open_date"
        )
    )

    if (
        current_open
        and open_date
        < current_open
    ):
        return False

    letter["title"] = title
    letter[
        "category"
    ] = category
    letter[
        "open_date"
    ] = str(open_date)
    letter[
        "updated_at"
    ] = now_text()

    save_data(data)

    return True


def delete_letter(
    data,
    letter_id,
):
    letter = get_letter(
        data,
        letter_id,
    )

    if not letter:
        return

    children = [
        child
        for child
        in data["letters"]
        if child.get(
            "parent_letter_id"
        ) == letter_id
    ]

    if children:
        return False

    data["letters"] = [
        item
        for item
        in data["letters"]
        if item.get("id")
        != letter_id
    ]

    data["replies"] = [
        reply
        for reply
        in data["replies"]
        if reply.get(
            "letter_id"
        ) != letter_id
    ]

    save_data(data)

    return True


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
        background: rgba(110, 90, 190, 0.07);
        border: 1px solid rgba(110, 90, 190, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(110, 80, 210, 0.18),
                rgba(240, 150, 200, 0.12)
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

    .locked-letter {
        padding: 22px;
        border-radius: 20px;
        border: 1px solid rgba(120, 100, 190, 0.20);
        margin-bottom: 12px;
    }

    .letter-body {
        padding: 24px;
        border-radius: 20px;
        background: rgba(120, 100, 190, 0.07);
        border: 1px solid rgba(120, 100, 190, 0.16);
        margin-top: 10px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

letters = data["letters"]
replies = data["replies"]

today = date.today()

locked_letters = [
    letter
    for letter in letters
    if is_locked(letter)
]

arrived_letters = [
    letter
    for letter in letters
    if is_available(letter)
]

unread_letters = [
    letter
    for letter
    in arrived_letters
    if not letter.get(
        "read",
        False,
    )
]

replied_letters = [
    letter
    for letter
    in arrived_letters
    if get_reply(
        data,
        letter.get(
            "id",
            "",
        ),
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📮 未来の自分に預ける</h1>
        <p>
            今の気持ちを、
            まだ会ったことのない自分へ。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日届いた手紙
# =========================================================

if unread_letters:
    st.success(
        f"📬 {len(unread_letters)}通の"
        "手紙が届いています！"
    )

    st.subheader(
        "📬 あなたへの手紙"
    )

    for letter in sorted(
        unread_letters,
        key=lambda row: row.get(
            "open_date",
            "",
        ),
    ):
        letter_id = letter.get(
            "id",
            "",
        )

        sent_date = parse_date(
            letter.get(
                "sent_date"
            )
        )

        elapsed = (
            (today - sent_date).days
            if sent_date
            else 0
        )

        with st.container(
            border=True
        ):
            st.caption(
                f"📮 {elapsed}日前の"
                "あなたから"
            )

            st.subheader(
                letter.get(
                    "title",
                    "",
                )
            )

            st.write(
                f"{format_date(letter.get('sent_date'))}"
                " → "
                f"{format_date(letter.get('open_date'))}"
            )

            if st.button(
                "📬 手紙を開く",
                key=(
                    "open_"
                    + letter_id
                ),
                type="primary",
                use_container_width=True,
            ):
                mark_read(
                    data,
                    letter_id,
                )

                st.session_state[
                    "opened_letter_id"
                ] = letter_id

                st.rerun()


# =========================================================
# 開いた直後の手紙
# =========================================================

opened_letter_id = (
    st.session_state.get(
        "opened_letter_id"
    )
)

opened_letter = (
    get_letter(
        data,
        opened_letter_id,
    )
    if opened_letter_id
    else None
)

if (
    opened_letter
    and is_available(
        opened_letter
    )
):
    st.divider()

    st.subheader(
        "💌 過去の自分から"
    )

    st.caption(
        format_date(
            opened_letter.get(
                "sent_date"
            )
        )
        + " のあなたより"
    )

    st.markdown(
        '<div class="letter-body">',
        unsafe_allow_html=True,
    )

    st.write(
        opened_letter.get(
            "message",
            "",
        )
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    journey = travel_days(
        opened_letter
    )

    if journey == 0:
        st.caption(
            "📬 この手紙は今日、"
            "未来へ送られました。"
        )
    else:
        st.caption(
            f"📬 この手紙は"
            f"{journey}日間、"
            "未来を旅しました。"
        )

    reply = get_reply(
        data,
        opened_letter.get(
            "id"
        ),
    )

    if not reply:
        with st.form(
            "opened_reply_form"
        ):
            reply_text = st.text_area(
                "💭 今の自分はどう思う？",
                placeholder=(
                    "あの頃の自分へ"
                    "返事を書いてみよう。"
                ),
            )

            submitted = (
                st.form_submit_button(
                    "💌 過去の自分へ返信",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                if not (
                    reply_text.strip()
                ):
                    st.warning(
                        "返信を書いてね。"
                    )

                else:
                    add_reply(
                        data,
                        opened_letter.get(
                            "id"
                        ),
                        reply_text.strip(),
                    )
                    st.rerun()

    else:
        st.write(
            "**💌 今の自分からの返信**"
        )

        st.write(
            reply.get(
                "message",
                "",
            )
        )


# =========================================================
# ダッシュボード
# =========================================================

st.divider()

st.subheader(
    "🌙 時間のポスト"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📮 送った手紙",
    f"{len(letters)}通",
)

col2.metric(
    "🔒 未来を旅している",
    f"{len(locked_letters)}通",
)

col3.metric(
    "📬 届いた手紙",
    f"{len(arrived_letters)}通",
)

col4.metric(
    "💌 返信した手紙",
    f"{len(replied_letters)}通",
)

st.caption(
    f"🌳 時間を越えた会話："
    f"{thread_count(data)}本"
)

if locked_letters:
    longest = max(
        locked_letters,
        key=lambda letter: (
            days_until(
                letter.get(
                    "open_date"
                )
            )
            or 0
        ),
    )

    st.info(
        "⏳ 一番遠い未来へ"
        "向かっている手紙："
        f"「{longest.get('title', '')}」"
        " — "
        f"{human_countdown(days_until(longest.get('open_date')))}"
    )


# =========================================================
# 新しい手紙
# =========================================================

st.divider()

st.subheader(
    "📮 未来の自分へ"
)

with st.form(
    "new_letter_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "タイトル",
        placeholder=(
            "例：300本を作った自分へ"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    message = st.text_area(
        "💌 未来の自分へのメッセージ",
        height=180,
        placeholder=(
            "今の気持ち、"
            "未来への質問、"
            "忘れたくないこと……"
        ),
    )

    default_open_date = (
        today
        + timedelta(days=30)
    )

    open_date = st.date_input(
        "📅 いつ開ける？",
        value=default_open_date,
        min_value=(
            today
            + timedelta(days=1)
        ),
    )

    st.caption(
        "🔒 送信後、本文は"
        "開封日まで表示されません。"
        "本文の編集もできません。"
    )

    submitted = (
        st.form_submit_button(
            "📮 未来へ送る",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "タイトルを入力してね。"
            )

        elif not message.strip():
            st.warning(
                "未来の自分への"
                "メッセージを書いてね。"
            )

        else:
            add_letter(
                data=data,
                title=title.strip(),
                message=message.strip(),
                category=category,
                open_date=open_date,
            )

            st.rerun()


# =========================================================
# 未来への荷物
# =========================================================

st.divider()

st.subheader(
    "📦 未来へ預けているもの"
)

if not locked_letters:
    st.info(
        "現在、未来を旅している"
        "手紙はありません。"
    )

else:
    for letter in sorted(
        locked_letters,
        key=lambda row: row.get(
            "open_date",
            "",
        ),
    ):
        remaining = days_until(
            letter.get(
                "open_date"
            )
        )

        st.markdown(
            f"""
            <div class="locked-letter">
                <b>📮 {letter.get("title", "")}</b><br>
                <small>
                    {letter.get("category", "")}
                    ｜ {format_date(letter.get("sent_date"))}
                    → {format_date(letter.get("open_date"))}
                </small><br><br>
                🔒 <b>{human_countdown(remaining)}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "🔒 未開封の手紙の本文は"
        "表示されません。"
    )


# =========================================================
# 届いた手紙
# =========================================================

if arrived_letters:
    st.divider()

    st.subheader(
        "📬 届いた手紙"
    )

    for letter in sorted(
        arrived_letters,
        key=lambda row: row.get(
            "open_date",
            "",
        ),
        reverse=True,
    ):
        letter_id = letter.get(
            "id",
            "",
        )

        reply = get_reply(
            data,
            letter_id,
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [8, 1]
            )

            with col1:
                st.write(
                    "**"
                    + letter.get(
                        "title",
                        "",
                    )
                    + "**"
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if letter.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "fav_arrived_"
                        + letter_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        letter_id,
                    )
                    st.rerun()

            st.caption(
                letter.get(
                    "category",
                    "",
                )
                + " ｜ "
                + format_date(
                    letter.get(
                        "sent_date"
                    )
                )
                + " → "
                + format_date(
                    letter.get(
                        "open_date"
                    )
                )
            )

            st.write(
                "**📮 過去の自分より**"
            )

            st.write(
                letter.get(
                    "message",
                    "",
                )
            )

            if reply:
                st.divider()

                st.write(
                    "**💌 今の自分から**"
                )

                st.write(
                    reply.get(
                        "message",
                        "",
                    )
                )

            else:
                with st.expander(
                    "💌 この手紙に返信する"
                ):
                    reply_text = (
                        st.text_area(
                            "返信",
                            key=(
                                "reply_text_"
                                + letter_id
                            ),
                        )
                    )

                    if st.button(
                        "💌 返信を保存",
                        key=(
                            "reply_save_"
                            + letter_id
                        ),
                        type="primary",
                        use_container_width=True,
                    ):
                        if not (
                            reply_text.strip()
                        ):
                            st.warning(
                                "返信を書いてね。"
                            )
                        else:
                            add_reply(
                                data,
                                letter_id,
                                reply_text.strip(),
                            )
                            st.rerun()

            if reply:
                with st.expander(
                    "🚀 この続きを未来へ送る"
                ):
                    next_title = (
                        st.text_input(
                            "次の手紙のタイトル",
                            value=letter.get(
                                "title",
                                "",
                            ),
                            key=(
                                "next_title_"
                                + letter_id
                            ),
                        )
                    )

                    next_message = (
                        st.text_area(
                            "未来の自分へ",
                            placeholder=(
                                "今の自分から、"
                                "さらに未来の自分へ……"
                            ),
                            key=(
                                "next_message_"
                                + letter_id
                            ),
                        )
                    )

                    next_open = (
                        st.date_input(
                            "次の開封日",
                            value=(
                                today
                                + timedelta(
                                    days=365
                                )
                            ),
                            min_value=(
                                today
                                + timedelta(
                                    days=1
                                )
                            ),
                            key=(
                                "next_open_"
                                + letter_id
                            ),
                        )
                    )

                    if st.button(
                        "📮 この続きを未来へ",
                        key=(
                            "next_send_"
                            + letter_id
                        ),
                        type="primary",
                        use_container_width=True,
                    ):
                        if not (
                            next_title.strip()
                            and next_message.strip()
                        ):
                            st.warning(
                                "タイトルと"
                                "メッセージを書いてね。"
                            )
                        else:
                            add_letter(
                                data=data,
                                title=(
                                    next_title.strip()
                                ),
                                message=(
                                    next_message.strip()
                                ),
                                category=letter.get(
                                    "category",
                                    "✨ その他",
                                ),
                                open_date=(
                                    next_open
                                ),
                                thread_id=letter.get(
                                    "thread_id"
                                ),
                                parent_letter_id=(
                                    letter_id
                                ),
                            )

                            st.rerun()


# =========================================================
# 時間の手紙ツリー
# =========================================================

if letters:
    st.divider()

    st.subheader(
        "🌳 時間の手紙ツリー"
    )

    thread_ids = []

    for letter in letters:
        thread_id = letter.get(
            "thread_id"
        )

        if (
            thread_id
            and thread_id
            not in thread_ids
        ):
            thread_ids.append(
                thread_id
            )

    for thread_id in thread_ids:
        thread_letters = (
            get_thread_letters(
                data,
                thread_id,
            )
        )

        if not thread_letters:
            continue

        root = thread_letters[0]

        with st.expander(
            "🌳 "
            + root.get(
                "title",
                "時間の手紙",
            )
        ):
            for index, letter in enumerate(
                thread_letters
            ):
                available = (
                    is_available(
                        letter
                    )
                )

                status = (
                    "📬 開封済み"
                    if available
                    else "🔒 未来へ移動中"
                )

                st.write(
                    f"**📮 "
                    f"{format_date(letter.get('sent_date'))}**"
                    f" — {letter.get('title', '')}"
                )

                st.caption(
                    f"{status} ｜ "
                    f"開封日 "
                    f"{format_date(letter.get('open_date'))}"
                )

                if available:
                    st.write(
                        letter.get(
                            "message",
                            "",
                        )
                    )

                    reply = get_reply(
                        data,
                        letter.get(
                            "id"
                        ),
                    )

                    if reply:
                        st.write(
                            "💌 **返信**"
                        )
                        st.write(
                            reply.get(
                                "message",
                                "",
                            )
                        )

                else:
                    st.write(
                        "🔒 本文はまだ"
                        "未来を旅しています。"
                    )

                if (
                    index
                    < len(
                        thread_letters
                    ) - 1
                ):
                    st.markdown(
                        "### ↓"
                    )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    letter
    for letter
    in arrived_letters
    if letter.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 大切な手紙"
    )

    for letter in sorted(
        favorites,
        key=lambda row: row.get(
            "open_date",
            "",
        ),
        reverse=True,
    ):
        st.write(
            f"⭐ **{letter.get('title', '')}**"
        )

        st.caption(
            f"{format_date(letter.get('sent_date'))}"
            " → "
            f"{format_date(letter.get('open_date'))}"
        )


# =========================================================
# 過去の手紙ガチャ
# =========================================================

old_arrived = []

for letter in arrived_letters:
    open_date = parse_date(
        letter.get(
            "open_date"
        )
    )

    if (
        open_date
        and (
            today
            - open_date
        ).days >= 30
    ):
        old_arrived.append(
            letter
        )

if old_arrived:
    st.divider()

    st.subheader(
        "🎲 昔の自分から"
    )

    old_ids = [
        letter.get(
            "id"
        )
        for letter in old_arrived
    ]

    random_id = (
        st.session_state.get(
            "random_letter_id"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_letter_id"
        ] = random_id

    random_letter = (
        get_letter(
            data,
            random_id,
        )
    )

    if random_letter:
        sent = parse_date(
            random_letter.get(
                "sent_date"
            )
        )

        ago = (
            (today - sent).days
            if sent
            else 0
        )

        with st.container(
            border=True
        ):
            st.caption(
                f"🎲 {ago}日前の"
                "あなたから"
            )

            st.subheader(
                random_letter.get(
                    "title",
                    "",
                )
            )

            st.write(
                random_letter.get(
                    "message",
                    "",
                )
            )

            reply = get_reply(
                data,
                random_id,
            )

            if reply:
                st.divider()

                st.write(
                    "**💌 その時の返信**"
                )

                st.write(
                    reply.get(
                        "message",
                        "",
                    )
                )

        if st.button(
            "🎲 別の手紙を見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id
                in old_ids
                if item_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_letter_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 手紙図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 手紙図鑑"
)

search_text = st.text_input(
    "🔎 手紙を検索",
    placeholder=(
        "夢、仕事、300本……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="library_category",
        )
    )

with col2:
    status_filter = (
        st.selectbox(
            "状態",
            [
                "すべて",
                "🔒 未開封",
                "📬 開封済み",
                "⭐ お気に入り",
            ],
            key="library_status",
        )
    )

filtered = []

for letter in letters:
    available = is_available(
        letter
    )

    if (
        category_filter
        != "すべて"
        and letter.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        status_filter
        == "🔒 未開封"
        and available
    ):
        continue

    if (
        status_filter
        == "📬 開封済み"
        and not available
    ):
        continue

    if (
        status_filter
        == "⭐ お気に入り"
        and not letter.get(
            "favorite",
            False,
        )
    ):
        continue

    # 未開封の本文は
    # 検索対象にしない
    searchable_parts = [
        letter.get(
            "title",
            "",
        ),
        letter.get(
            "category",
            "",
        ),
    ]

    if available:
        searchable_parts.append(
            letter.get(
                "message",
                "",
            )
        )

        reply = get_reply(
            data,
            letter.get(
                "id"
            ),
        )

        if reply:
            searchable_parts.append(
                reply.get(
                    "message",
                    "",
                )
            )

    searchable = " ".join(
        searchable_parts
    ).lower()

    if (
        search_text.strip()
        and search_text
        .strip()
        .lower()
        not in searchable
    ):
        continue

    filtered.append(
        letter
    )

if not filtered:
    st.info(
        "条件に合う手紙はありません。"
    )

else:
    rows = []

    for letter in sorted(
        filtered,
        key=lambda row: row.get(
            "sent_date",
            "",
        ),
        reverse=True,
    ):
        available = is_available(
            letter
        )

        rows.append(
            {
                "タイトル": letter.get(
                    "title",
                    "",
                ),
                "カテゴリー": letter.get(
                    "category",
                    "",
                ),
                "送信日": format_date(
                    letter.get(
                        "sent_date"
                    )
                ),
                "開封日": format_date(
                    letter.get(
                        "open_date"
                    )
                ),
                "状態": (
                    "📬 開封済み"
                    if available
                    else "🔒 未開封"
                ),
                "返信": (
                    "💌"
                    if get_reply(
                        data,
                        letter.get(
                            "id"
                        ),
                    )
                    else ""
                ),
                "⭐": (
                    "⭐"
                    if letter.get(
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
    if not letters:
        st.caption(
            "まだ手紙がありません。"
        )

    for letter in sorted(
        letters,
        key=lambda row: row.get(
            "sent_date",
            "",
        ),
        reverse=True,
    ):
        letter_id = letter.get(
            "id",
            "",
        )

        locked = is_locked(
            letter
        )

        with st.expander(
            (
                "🔒 "
                if locked
                else "📬 "
            )
            + letter.get(
                "title",
                "",
            )
        ):
            st.caption(
                f"送信："
                f"{format_date(letter.get('sent_date'))}"
                f" ｜ 開封："
                f"{format_date(letter.get('open_date'))}"
            )

            if locked:
                st.info(
                    "🔒 本文は封印されています。"
                    "送信後の本文は編集できません。"
                )

                edit_title = (
                    st.text_input(
                        "タイトル",
                        value=letter.get(
                            "title",
                            "",
                        ),
                        key=(
                            "edit_title_"
                            + letter_id
                        ),
                    )
                )

                old_category = (
                    letter.get(
                        "category",
                        "✨ その他",
                    )
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
                            + letter_id
                        ),
                    )
                )

                current_open = (
                    parse_date(
                        letter.get(
                            "open_date"
                        )
                    )
                    or (
                        today
                        + timedelta(
                            days=1
                        )
                    )
                )

                edit_open = (
                    st.date_input(
                        "開封日を延期",
                        value=current_open,
                        min_value=current_open,
                        key=(
                            "edit_open_"
                            + letter_id
                        ),
                    )
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_"
                        + letter_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "タイトルを入力してね。"
                        )

                    else:
                        updated = (
                            update_locked_letter(
                                data=data,
                                letter_id=(
                                    letter_id
                                ),
                                title=(
                                    edit_title.strip()
                                ),
                                category=(
                                    edit_category
                                ),
                                open_date=(
                                    edit_open
                                ),
                            )
                        )

                        if updated:
                            st.rerun()

                        else:
                            st.warning(
                                "開封日を"
                                "前倒しすることは"
                                "できません。"
                            )

            else:
                st.write(
                    "**📮 手紙本文**"
                )

                st.write(
                    letter.get(
                        "message",
                        "",
                    )
                )

                reply = get_reply(
                    data,
                    letter_id,
                )

                if reply:
                    st.write(
                        "**💌 返信**"
                    )
                    st.write(
                        reply.get(
                            "message",
                            "",
                        )
                    )

                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if letter.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_fav_"
                        + letter_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        letter_id,
                    )
                    st.rerun()

            st.markdown(
                "#### 🗑️ 削除"
            )

            children = [
                child
                for child
                in letters
                if child.get(
                    "parent_letter_id"
                ) == letter_id
            ]

            if children:
                st.caption(
                    "🌳 この手紙には"
                    "続きがあるため、"
                    "単独では削除できません。"
                )

            else:
                confirm = st.checkbox(
                    "この手紙を削除する",
                    key=(
                        "confirm_delete_"
                        + letter_id
                    ),
                )

                if st.button(
                    "🗑️ 手紙を削除",
                    key=(
                        "delete_"
                        + letter_id
                    ),
                    disabled=not confirm,
                    use_container_width=True,
                ):
                    deleted = (
                        delete_letter(
                            data,
                            letter_id,
                        )
                    )

                    if deleted:
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
            "future_letters_"
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
    "📮 今の気持ちは、"
    "未来の自分にしか分からない"
    "答えを持っている。"
)

st.caption(
    "🌙 今日の自分から、"
    "まだ会ったことのない自分へ。"
)
