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
    page_title="これ、いつから気になってる？",
    page_icon="💭",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "concerns.json",
)

CATEGORIES = [
    "🎯 やりたい",
    "📚 調べたい",
    "🛒 欲しい",
    "🤔 決めたい",
    "💼 仕事",
    "🏠 生活",
    "👥 人間関係",
    "💡 アイデア",
    "✨ その他",
]

STATUSES = [
    "💭 気になる",
    "🔥 向き合い中",
    "📦 保留",
    "🍃 手放した",
    "✅ 解決",
]

ACTIVE_STATUSES = [
    "💭 気になる",
    "🔥 向き合い中",
]


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


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value
        )
    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d"
    )


def format_datetime(value):
    parsed = parse_datetime(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d %H:%M"
    )


def days_from(value):
    parsed = parse_date(value)

    if not parsed:
        return 0

    return max(
        (date.today() - parsed).days,
        0,
    )


def average(values):
    values = [
        value
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "items": [],
        "mentions": [],
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
            "items",
            [],
        )

        data.setdefault(
            "mentions",
            [],
        )

        for item in data["items"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "title",
                "",
            )

            item.setdefault(
                "category",
                "✨ その他",
            )

            item.setdefault(
                "first_date",
                today_text(),
            )

            item.setdefault(
                "last_date",
                item.get(
                    "first_date",
                    today_text(),
                ),
            )

            item.setdefault(
                "status",
                "💭 気になる",
            )

            item.setdefault(
                "memo",
                "",
            )

            item.setdefault(
                "next_action",
                "",
            )

            item.setdefault(
                "deadline",
                None,
            )

            item.setdefault(
                "hold_until",
                None,
            )

            item.setdefault(
                "resolution_note",
                "",
            )

            item.setdefault(
                "favorite",
                False,
            )

            item.setdefault(
                "created_at",
                now_text(),
            )

            item.setdefault(
                "updated_at",
                item.get(
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
# CRUD
# =========================================================

def get_item(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["items"]
            if item.get("id")
            == item_id
        ),
        None,
    )


def item_mentions(
    data,
    item_id,
):
    return [
        mention
        for mention
        in data["mentions"]
        if mention.get(
            "item_id"
        )
        == item_id
    ]


def mention_count(
    data,
    item_id,
):
    # 最初に気になった1回も含む
    return (
        len(
            item_mentions(
                data,
                item_id,
            )
        )
        + 1
    )


def add_item(
    data,
    title,
    category,
    first_date,
    memo,
):
    item_id = create_id()

    item = {
        "id": item_id,
        "title": title,
        "category": category,
        "first_date": str(
            first_date
        ),
        "last_date": str(
            first_date
        ),
        "status": "💭 気になる",
        "memo": memo,
        "next_action": "",
        "deadline": None,
        "hold_until": None,
        "resolution_note": "",
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["items"].append(item)
    save_data(data)

    return item_id


def add_mention(
    data,
    item_id,
    note="",
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    mention = {
        "id": create_id(),
        "item_id": item_id,
        "mention_date": (
            today_text()
        ),
        "note": note,
        "created_at": now_text(),
    }

    data["mentions"].append(
        mention
    )

    item["last_date"] = (
        today_text()
    )

    item["updated_at"] = (
        now_text()
    )

    # 手放し・解決済みのものを
    # 再び気になった場合は復活
    if item.get(
        "status"
    ) in [
        "🍃 手放した",
        "✅ 解決",
    ]:
        item["status"] = (
            "💭 気になる"
        )

        item["resolution_note"] = ""

    save_data(data)


def update_item(
    data,
    item_id,
    title,
    category,
    first_date,
    last_date,
    memo,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["title"] = title
    item["category"] = category
    item["first_date"] = str(
        first_date
    )
    item["last_date"] = str(
        last_date
    )
    item["memo"] = memo
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["favorite"] = (
        not item.get(
            "favorite",
            False,
        )
    )

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def face_item(
    data,
    item_id,
    next_action,
    deadline,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = (
        "🔥 向き合い中"
    )

    item["next_action"] = (
        next_action
    )

    item["deadline"] = (
        str(deadline)
        if deadline
        else None
    )

    item["hold_until"] = None
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def hold_item(
    data,
    item_id,
    hold_until,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = "📦 保留"
    item["hold_until"] = str(
        hold_until
    )
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def release_hold(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = (
        "💭 気になる"
    )

    item["hold_until"] = None
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def close_item(
    data,
    item_id,
    status,
    note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = status
    item["resolution_note"] = (
        note
    )

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data["items"]
        if item.get("id")
        != item_id
    ]

    data["mentions"] = [
        mention
        for mention
        in data["mentions"]
        if mention.get(
            "item_id"
        )
        != item_id
    ]

    save_data(data)


def delete_mention(
    data,
    mention_id,
):
    data["mentions"] = [
        mention
        for mention
        in data["mentions"]
        if mention.get("id")
        != mention_id
    ]

    save_data(data)


# =========================================================
# 保留解除
# =========================================================

def auto_release_holds(
    data,
):
    changed = False

    for item in data["items"]:
        if item.get(
            "status"
        ) != "📦 保留":
            continue

        hold_until = parse_date(
            item.get(
                "hold_until"
            )
        )

        if (
            hold_until
            and hold_until
            <= date.today()
        ):
            item["status"] = (
                "💭 気になる"
            )

            item[
                "hold_until"
            ] = None

            item[
                "updated_at"
            ] = now_text()

            changed = True

    if changed:
        save_data(data)


# =========================================================
# 気になりスコア
# =========================================================

def concern_score(
    data,
    item,
):
    item_id = item.get(
        "id",
        "",
    )

    count = mention_count(
        data,
        item_id,
    )

    # 再登場回数。
    # 初回は除外。
    repeats = max(
        count - 1,
        0,
    )

    repeat_score = min(
        repeats * 10,
        60,
    )

    last_days = days_from(
        item.get(
            "last_date"
        )
    )

    if last_days == 0:
        recent_score = 25
    elif last_days <= 7:
        recent_score = 20
    elif last_days <= 30:
        recent_score = 10
    else:
        recent_score = 0

    duration = days_from(
        item.get(
            "first_date"
        )
    )

    if duration >= 90:
        duration_score = 15
    elif duration >= 30:
        duration_score = 10
    elif duration >= 7:
        duration_score = 5
    else:
        duration_score = 0

    return min(
        repeat_score
        + recent_score
        + duration_score,
        100,
    )


def score_label(score):
    if score >= 80:
        return "🔥 かなり気になってる"

    if score >= 60:
        return "👀 何度も戻ってくる"

    if score >= 40:
        return "💭 気になってる"

    return "🌱 まだ小さな気がかり"


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
        background: rgba(140, 100, 220, 0.07);
        border: 1px solid rgba(140, 100, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(140, 100, 220, 0.18),
                rgba(100, 170, 230, 0.08)
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

    .days-number {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 8px 0;
    }

    .score-number {
        font-size: 2rem;
        font-weight: 800;
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

auto_release_holds(data)

items = data["items"]
mentions = data["mentions"]

active_items = [
    item
    for item in items
    if item.get(
        "status"
    )
    in ACTIVE_STATUSES
]

hold_items = [
    item
    for item in items
    if item.get(
        "status"
    )
    == "📦 保留"
]

closed_items = [
    item
    for item in items
    if item.get(
        "status"
    )
    in [
        "🍃 手放した",
        "✅ 解決",
    ]
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>💭 これ、いつから気になってる？</h1>
        <p>
            何度も戻ってくることには、
            まだ続きがある。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

total_mentions = (
    len(mentions)
    + len(items)
)

high_score_items = [
    item
    for item in active_items
    if concern_score(
        data,
        item,
    )
    >= 60
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "💭 気になる",
    f"{len(active_items)}個",
)

col2.metric(
    "🔥 よく戻ってくる",
    f"{len(high_score_items)}個",
)

col3.metric(
    "📦 保留",
    f"{len(hold_items)}個",
)

col4.metric(
    "🧠 気になった総回数",
    f"{total_mentions}回",
)


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "💭 気になることを追加"
)

with st.form(
    "new_item_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "💭 何が気になってる？",
        placeholder=(
            "例：作業用の椅子を"
            "買い替えたい"
        ),
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        category = (
            st.selectbox(
                "🏷️ カテゴリー",
                CATEGORIES,
            )
        )

    with col2:
        first_date = (
            st.date_input(
                "📅 最初に気になった日",
                value=date.today(),
                max_value=date.today(),
            )
        )

    memo = st.text_area(
        "📝 ひとこと",
        placeholder=(
            "例：最近ちょっと"
            "気になっている"
        ),
    )

    submitted = (
        st.form_submit_button(
            "💭 気になることに追加",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "気になっていることを"
                "入力してね。"
            )

        else:
            add_item(
                data=data,
                title=title.strip(),
                category=category,
                first_date=first_date,
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 今、頭にいること
# =========================================================

st.divider()

st.subheader(
    "🔥 今、頭にいること"
)

if not active_items:
    st.info(
        "今のところ、気になっていることはありません。"
    )

else:
    ranked_items = sorted(
        active_items,
        key=lambda item: (
            concern_score(
                data,
                item,
            ),
            mention_count(
                data,
                item.get(
                    "id"
                ),
            ),
        ),
        reverse=True,
    )

    for rank, item in enumerate(
        ranked_items[:5],
        start=1,
    ):
        item_id = item.get(
            "id",
            "",
        )

        score = concern_score(
            data,
            item,
        )

        count = mention_count(
            data,
            item_id,
        )

        duration = days_from(
            item.get(
                "first_date"
            )
        )

        last_days = days_from(
            item.get(
                "last_date"
            )
        )

        medal = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }.get(
            rank,
            f"{rank}.",
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [7, 1]
                )
            )

            with col1:
                st.subheader(
                    f"{medal} "
                    f"{item.get('title', '')}"
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "rank_favorite_"
                        + item_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ {item.get('status', '')}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "🔥 気になり",
                f"{score}pt",
            )

            col2.metric(
                "💭 回数",
                f"{count}回",
            )

            col3.metric(
                "⏳ 期間",
                f"{duration}日",
            )

            st.progress(
                score / 100
            )

            st.caption(
                score_label(score)
            )

            if last_days == 0:
                st.write(
                    "💭 **今日も気になっています。**"
                )
            else:
                st.write(
                    f"最後に浮かんだのは"
                    f" **{last_days}日前**"
                )

            if item.get(
                "memo"
            ):
                st.write(
                    "📝 "
                    + item.get(
                        "memo",
                        "",
                    )
                )

            if (
                item.get(
                    "status"
                )
                == "🔥 向き合い中"
            ):
                if item.get(
                    "next_action"
                ):
                    st.info(
                        "🎯 次にすること："
                        + item.get(
                            "next_action",
                            "",
                        )
                    )

                if item.get(
                    "deadline"
                ):
                    st.caption(
                        "期限："
                        + format_date(
                            item.get(
                                "deadline"
                            )
                        )
                    )

            if score >= 60:
                st.warning(
                    "👀 何度も戻ってきています。"
                    "一度ちゃんと向き合って"
                    "みてもいいかも。"
                )

            # -----------------------------------------
            # また気になった
            # -----------------------------------------

            with st.expander(
                "💭 また気になった！"
            ):
                mention_note = (
                    st.text_area(
                        "今、どう気になった？",
                        key=(
                            "mention_note_"
                            + item_id
                        ),
                        placeholder=(
                            "例：やっぱり"
                            "気になる……"
                        ),
                    )
                )

                if st.button(
                    "💭 記録する",
                    key=(
                        "mention_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    add_mention(
                        data,
                        item_id,
                        mention_note.strip(),
                    )

                    st.rerun()

            # -----------------------------------------
            # 向き合う
            # -----------------------------------------

            with st.expander(
                "🎯 向き合う"
            ):
                next_action = (
                    st.text_input(
                        "次にすること",
                        key=(
                            "next_action_"
                            + item_id
                        ),
                        placeholder=(
                            "例：候補を3つに絞る"
                        ),
                    )
                )

                use_deadline = (
                    st.checkbox(
                        "期限を決める",
                        key=(
                            "use_deadline_"
                            + item_id
                        ),
                    )
                )

                deadline = None

                if use_deadline:
                    deadline = (
                        st.date_input(
                            "期限",
                            value=(
                                date.today()
                                + timedelta(
                                    days=7
                                )
                            ),
                            min_value=(
                                date.today()
                            ),
                            key=(
                                "deadline_"
                                + item_id
                            ),
                        )
                    )

                if st.button(
                    "🎯 向き合い中にする",
                    key=(
                        "face_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        next_action.strip()
                    ):
                        st.warning(
                            "次にすることを"
                            "1つ決めてみよう。"
                        )

                    else:
                        face_item(
                            data,
                            item_id,
                            next_action.strip(),
                            deadline,
                        )

                        st.rerun()

            # -----------------------------------------
            # 保留
            # -----------------------------------------

            with st.expander(
                "📦 保留する"
            ):
                hold_until = (
                    st.date_input(
                        "いつまで保留？",
                        value=(
                            date.today()
                            + timedelta(
                                days=14
                            )
                        ),
                        min_value=(
                            date.today()
                            + timedelta(
                                days=1
                            )
                        ),
                        key=(
                            "hold_until_"
                            + item_id
                        ),
                    )
                )

                if st.button(
                    "📦 ここまで保留",
                    key=(
                        "hold_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    hold_item(
                        data,
                        item_id,
                        hold_until,
                    )

                    st.rerun()

            # -----------------------------------------
            # 手放す・解決
            # -----------------------------------------

            with st.expander(
                "🍃 手放す / ✅ 解決"
            ):
                close_note = (
                    st.text_area(
                        "結論・ひとこと",
                        key=(
                            "close_note_"
                            + item_id
                        ),
                        placeholder=(
                            "例：今は買わなくていい"
                        ),
                    )
                )

                col1, col2 = (
                    st.columns(2)
                )

                with col1:
                    if st.button(
                        "🍃 手放す",
                        key=(
                            "letgo_"
                            + item_id
                        ),
                        use_container_width=True,
                    ):
                        close_item(
                            data,
                            item_id,
                            "🍃 手放した",
                            close_note.strip(),
                        )

                        st.rerun()

                with col2:
                    if st.button(
                        "✅ 解決した",
                        key=(
                            "resolve_"
                            + item_id
                        ),
                        use_container_width=True,
                    ):
                        close_item(
                            data,
                            item_id,
                            "✅ 解決",
                            close_note.strip(),
                        )

                        st.rerun()


# =========================================================
# 最近気にならなくなったもの
# =========================================================

st.divider()

st.subheader(
    "🍃 最近、気にならなくなった？"
)

quiet_items = [
    item
    for item in active_items
    if days_from(
        item.get(
            "last_date"
        )
    )
    >= 30
]

quiet_items = sorted(
    quiet_items,
    key=lambda item: (
        days_from(
            item.get(
                "last_date"
            )
        )
    ),
    reverse=True,
)

if not quiet_items:
    st.caption(
        "30日以上浮かんでいないテーマは"
        "今のところありません。"
    )

else:
    for item in quiet_items:
        item_id = item.get(
            "id",
            "",
        )

        quiet_days = days_from(
            item.get(
                "last_date"
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                item.get(
                    "title",
                    "",
                )
            )

            st.write(
                f"最後に気になったのは"
                f" **{quiet_days}日前**"
            )

            st.caption(
                f"最初："
                f"{format_date(item.get('first_date'))}"
                f" ｜ "
                f"{mention_count(data, item_id)}回"
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💭 やっぱり気になる",
                    key=(
                        "quiet_again_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    add_mention(
                        data,
                        item_id,
                        "久しぶりにまた気になった",
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "🍃 もう手放す",
                    key=(
                        "quiet_close_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    close_item(
                        data,
                        item_id,
                        "🍃 手放した",
                        "しばらく気にならなくなったため手放した",
                    )

                    st.rerun()


# =========================================================
# 保留中
# =========================================================

if hold_items:
    st.divider()

    st.subheader(
        "📦 今は保留"
    )

    for item in sorted(
        hold_items,
        key=lambda item: (
            item.get(
                "hold_until",
                "",
            )
        ),
    ):
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.subheader(
                item.get(
                    "title",
                    "",
                )
            )

            st.write(
                "📅 "
                + format_date(
                    item.get(
                        "hold_until"
                    )
                )
                + " まで保留"
            )

            st.caption(
                f"気になった回数："
                f"{mention_count(data, item_id)}回"
            )

            if st.button(
                "💭 今また考える",
                key=(
                    "release_hold_"
                    + item_id
                ),
                use_container_width=True,
            ):
                release_hold(
                    data,
                    item_id,
                )

                st.rerun()


# =========================================================
# ランダム再発見
# =========================================================

rediscovery_candidates = [
    item
    for item in items
    if days_from(
        item.get(
            "last_date"
        )
    )
    >= 14
]

if rediscovery_candidates:
    st.divider()

    st.subheader(
        "🎲 こんなの気になってたよ"
    )

    candidate_ids = [
        item.get("id")
        for item
        in rediscovery_candidates
    ]

    random_id = (
        st.session_state.get(
            "rediscovery_id"
        )
    )

    if (
        not random_id
        or random_id
        not in candidate_ids
    ):
        random_id = (
            random.choice(
                candidate_ids
            )
        )

        st.session_state[
            "rediscovery_id"
        ] = random_id

    random_item = get_item(
        data,
        random_id,
    )

    if random_item:
        with st.container(
            border=True
        ):
            st.subheader(
                random_item.get(
                    "title",
                    "",
                )
            )

            st.caption(
                random_item.get(
                    "category",
                    "",
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "最初",
                f"{days_from(random_item.get('first_date'))}日前",
            )

            col2.metric(
                "最後",
                f"{days_from(random_item.get('last_date'))}日前",
            )

            col3.metric(
                "💭 回数",
                f"{mention_count(data, random_id)}回",
            )

            st.write(
                "**今も気になる？**"
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💭 やっぱり気になる",
                    key="rediscovery_again",
                    use_container_width=True,
                ):
                    add_mention(
                        data,
                        random_id,
                        "ランダム再発見から再び気になった",
                    )

                    st.session_state.pop(
                        "rediscovery_id",
                        None,
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "🍃 もう手放す",
                    key="rediscovery_close",
                    use_container_width=True,
                ):
                    close_item(
                        data,
                        random_id,
                        "🍃 手放した",
                        "振り返って、今は手放すことにした",
                    )

                    st.session_state.pop(
                        "rediscovery_id",
                        None,
                    )

                    st.rerun()

        if st.button(
            "🎲 別のテーマを見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id
                in candidate_ids
                if item_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "rediscovery_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の頭の中"
)

month_prefix = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_new = [
    item
    for item in items
    if (
        item.get(
            "created_at",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_mentions = [
    mention
    for mention in mentions
    if (
        mention.get(
            "created_at",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_faced = [
    item
    for item in items
    if (
        item.get(
            "status"
        )
        == "🔥 向き合い中"
        and (
            item.get(
                "updated_at",
                "",
            )
            or ""
        ).startswith(
            month_prefix
        )
    )
]

month_closed = [
    item
    for item in items
    if (
        item.get(
            "status"
        )
        in [
            "🍃 手放した",
            "✅ 解決",
        ]
        and (
            item.get(
                "updated_at",
                "",
            )
            or ""
        ).startswith(
            month_prefix
        )
    )
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🆕 新しく気になった",
    f"{len(month_new)}個",
)

col2.metric(
    "💭 また気になった",
    f"{len(month_mentions)}回",
)

col3.metric(
    "🎯 向き合い中",
    f"{len(month_faced)}個",
)

col4.metric(
    "🍃 結論が出た",
    f"{len(month_closed)}個",
)


# =========================================================
# カテゴリー分析
# =========================================================

if active_items:
    st.markdown(
        "### 🧠 最近よく気になる分野"
    )

    category_scores = {}

    for item in active_items:
        category = item.get(
            "category",
            "✨ その他",
        )

        count = mention_count(
            data,
            item.get(
                "id"
            ),
        )

        category_scores[
            category
        ] = (
            category_scores.get(
                category,
                0,
            )
            + count
        )

    category_df = (
        pd.DataFrame(
            [
                {
                    "カテゴリー": category,
                    "気になった回数": count,
                }
                for category, count
                in category_scores.items()
            ]
        )
        .sort_values(
            "気になった回数",
            ascending=False,
        )
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 大切なテーマ
# =========================================================

favorites = [
    item
    for item in items
    if item.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 大切なテーマ"
    )

    for item in favorites:
        with st.container(
            border=True
        ):
            st.subheader(
                item.get(
                    "title",
                    "",
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "💭 回数",
                f"{mention_count(data, item.get('id'))}回",
            )

            col2.metric(
                "🔥 スコア",
                f"{concern_score(data, item)}pt",
            )

            st.caption(
                item.get(
                    "status",
                    "",
                )
            )


# =========================================================
# 気になること図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 気になること図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "欲しいもの、やりたいこと……"
    ),
)

col1, col2 = (
    st.columns(2)
)

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
            ["すべて"]
            + STATUSES,
            key="library_status",
        )
    )

filtered_items = []

for item in items:
    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        )
        != category_filter
    ):
        continue

    if (
        status_filter
        != "すべて"
        and item.get(
            "status"
        )
        != status_filter
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "title",
                "",
            ),
            item.get(
                "category",
                "",
            ),
            item.get(
                "memo",
                "",
            ),
            item.get(
                "resolution_note",
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

    filtered_items.append(
        item
    )


if not filtered_items:
    st.info(
        "条件に合うテーマはありません。"
    )

else:
    rows = []

    for item in sorted(
        filtered_items,
        key=lambda row: (
            concern_score(
                data,
                row,
            )
        ),
        reverse=True,
    ):
        rows.append(
            {
                "テーマ": (
                    item.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    item.get(
                        "category",
                        "",
                    )
                ),
                "状態": (
                    item.get(
                        "status",
                        "",
                    )
                ),
                "期間": (
                    f"{days_from(item.get('first_date'))}日"
                ),
                "回数": (
                    f"{mention_count(data, item.get('id'))}回"
                ),
                "気になり": (
                    f"{concern_score(data, item)}pt"
                ),
                "⭐": (
                    "⭐"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・管理"
):
    if not items:
        st.caption(
            "まだテーマがありません。"
        )

    for item in sorted(
        items,
        key=lambda row: (
            row.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    ):
        item_id = item.get(
            "id",
            "",
        )

        with st.expander(
            item.get(
                "title",
                "",
            )
        ):
            edit_title = (
                st.text_input(
                    "テーマ",
                    value=item.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + item_id
                    ),
                )
            )

            old_category = (
                item.get(
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
                        + item_id
                    ),
                )
            )

            first_value = (
                parse_date(
                    item.get(
                        "first_date"
                    )
                )
                or date.today()
            )

            last_value = (
                parse_date(
                    item.get(
                        "last_date"
                    )
                )
                or date.today()
            )

            edit_first = (
                st.date_input(
                    "最初に気になった日",
                    value=first_value,
                    max_value=date.today(),
                    key=(
                        "edit_first_"
                        + item_id
                    ),
                )
            )

            edit_last = (
                st.date_input(
                    "最後に気になった日",
                    value=last_value,
                    max_value=date.today(),
                    key=(
                        "edit_last_"
                        + item_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=item.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + item_id
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
                        "save_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "テーマを入力してね。"
                        )

                    elif (
                        edit_last
                        < edit_first
                    ):
                        st.warning(
                            "最後の日は最初の日以降にしてね。"
                        )

                    else:
                        update_item(
                            data,
                            item_id,
                            edit_title.strip(),
                            edit_category,
                            edit_first,
                            edit_last,
                            edit_memo.strip(),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ 大切から外す"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆ 大切にする"
                    ),
                    key=(
                        "favorite_manage_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            item_history = sorted(
                item_mentions(
                    data,
                    item_id,
                ),
                key=lambda mention: (
                    mention.get(
                        "created_at",
                        "",
                    )
                ),
                reverse=True,
            )

            if item_history:
                st.markdown(
                    "#### 💭 再登場履歴"
                )

                for mention in (
                    item_history
                ):
                    mention_id = (
                        mention.get(
                            "id",
                            "",
                        )
                    )

                    col1, col2 = (
                        st.columns(
                            [6, 1]
                        )
                    )

                    with col1:
                        st.write(
                            "💭 "
                            + format_date(
                                mention.get(
                                    "mention_date"
                                )
                            )
                        )

                        if mention.get(
                            "note"
                        ):
                            st.caption(
                                mention.get(
                                    "note",
                                    "",
                                )
                            )

                    with col2:
                        if st.button(
                            "🗑️",
                            key=(
                                "delete_mention_"
                                + mention_id
                            ),
                        ):
                            delete_mention(
                                data,
                                mention_id,
                            )

                            st.rerun()

            if item.get(
                "resolution_note"
            ):
                st.write(
                    "**結論**"
                )

                st.write(
                    item.get(
                        "resolution_note",
                        "",
                    )
                )

            confirm_delete = (
                st.checkbox(
                    "このテーマと履歴を削除する",
                    key=(
                        "confirm_delete_"
                        + item_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + item_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_item(
                    data,
                    item_id,
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
            "still_on_my_mind_"
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
    "💭 何度も戻ってくることには、"
    "まだ続きがある。"
)
