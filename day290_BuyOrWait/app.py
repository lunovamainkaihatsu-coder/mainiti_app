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
    page_title="これ、買う？やめる？",
    page_icon="🛒",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "wishlist.json",
)

CATEGORIES = [
    "💻 ガジェット",
    "👕 服・ファッション",
    "🏠 生活用品",
    "🎮 趣味",
    "📚 本・学習",
    "🍽️ 食べ物",
    "🎁 その他",
]

STATUSES = [
    "⏳ 待機中",
    "🤔 再検討",
    "🛍️ 購入",
    "🍃 見送り",
]

WAIT_OPTIONS = {
    "1日": 1,
    "3日": 3,
    "7日": 7,
    "14日": 14,
    "30日": 30,
}

USE_FREQUENCIES = [
    "🔥 ほぼ毎日",
    "😊 週数回",
    "🙂 たまに",
    "😴 ほぼ使ってない",
]

BUY_AGAIN_OPTIONS = [
    "👍 また買う",
    "🤔 分からない",
    "👎 もう買わない",
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


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d"
    )


def money(value):
    try:
        return f"¥{float(value):,.0f}"
    except (TypeError, ValueError):
        return "¥0"


def stars(value):
    value = max(
        1,
        min(
            int(value),
            5,
        ),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def days_since(value):
    parsed = parse_date(value)

    if not parsed:
        return 0

    return max(
        (date.today() - parsed).days,
        0,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "items": [],
        "reviews": [],
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
            "reviews",
            [],
        )

        for item in data["items"]:
            item.setdefault(
                "id",
                create_id(),
            )
            item.setdefault(
                "name",
                "",
            )
            item.setdefault(
                "category",
                "🎁 その他",
            )
            item.setdefault(
                "price",
                0,
            )
            item.setdefault(
                "need_initial",
                3,
            )
            item.setdefault(
                "want_initial",
                3,
            )
            item.setdefault(
                "need_current",
                item.get(
                    "need_initial",
                    3,
                ),
            )
            item.setdefault(
                "want_current",
                item.get(
                    "want_initial",
                    3,
                ),
            )
            item.setdefault(
                "reason",
                "",
            )
            item.setdefault(
                "registered_date",
                today_text(),
            )
            item.setdefault(
                "reconsider_date",
                today_text(),
            )
            item.setdefault(
                "status",
                "⏳ 待機中",
            )
            item.setdefault(
                "wait_count",
                0,
            )
            item.setdefault(
                "history",
                [],
            )
            item.setdefault(
                "purchase_date",
                None,
            )
            item.setdefault(
                "purchase_price",
                None,
            )
            item.setdefault(
                "passed_date",
                None,
            )
            item.setdefault(
                "favorite",
                False,
            )
            item.setdefault(
                "memo",
                "",
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

        for review in data[
            "reviews"
        ]:
            review.setdefault(
                "id",
                create_id(),
            )
            review.setdefault(
                "item_id",
                "",
            )
            review.setdefault(
                "review_date",
                today_text(),
            )
            review.setdefault(
                "satisfaction",
                3,
            )
            review.setdefault(
                "frequency",
                "🙂 たまに",
            )
            review.setdefault(
                "buy_again",
                "🤔 分からない",
            )
            review.setdefault(
                "note",
                "",
            )
            review.setdefault(
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

def get_item(
    data,
    item_id,
):
    return next(
        (
            item
            for item
            in data["items"]
            if item.get("id")
            == item_id
        ),
        None,
    )


def get_review(
    data,
    item_id,
):
    reviews = [
        review
        for review
        in data["reviews"]
        if review.get(
            "item_id"
        ) == item_id
    ]

    if not reviews:
        return None

    return sorted(
        reviews,
        key=lambda row: (
            row.get(
                "review_date",
                ""
            )
        ),
        reverse=True,
    )[0]


# =========================================================
# CRUD
# =========================================================

def add_item(
    data,
    name,
    category,
    price,
    need,
    want,
    reason,
    registered_date,
    wait_days,
    memo,
):
    reconsider_date = (
        registered_date
        + timedelta(
            days=wait_days
        )
    )

    item_id = create_id()

    item = {
        "id": item_id,
        "name": name,
        "category": category,
        "price": float(price),
        "need_initial": int(need),
        "want_initial": int(want),
        "need_current": int(need),
        "want_current": int(want),
        "reason": reason,
        "registered_date": str(
            registered_date
        ),
        "reconsider_date": str(
            reconsider_date
        ),
        "status": "⏳ 待機中",
        "wait_count": 0,
        "history": [
            {
                "date": str(
                    registered_date
                ),
                "action": (
                    "📦 欲しいものBOXに預けた"
                ),
                "need": int(need),
                "want": int(want),
                "note": reason,
            }
        ],
        "purchase_date": None,
        "purchase_price": None,
        "passed_date": None,
        "favorite": False,
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["items"].append(
        item
    )

    save_data(data)


def postpone_item(
    data,
    item_id,
    days,
    need,
    want,
    note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    new_date = (
        date.today()
        + timedelta(
            days=int(days)
        )
    )

    item[
        "reconsider_date"
    ] = str(
        new_date
    )

    item[
        "need_current"
    ] = int(need)

    item[
        "want_current"
    ] = int(want)

    item[
        "wait_count"
    ] = int(
        item.get(
            "wait_count",
            0,
        )
    ) + 1

    item[
        "status"
    ] = "⏳ 待機中"

    item.setdefault(
        "history",
        [],
    ).append(
        {
            "date": today_text(),
            "action": (
                f"⏳ あと{days}日待つ"
            ),
            "need": int(need),
            "want": int(want),
            "note": note,
        }
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def purchase_item(
    data,
    item_id,
    purchase_price,
    need,
    want,
    note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "status"
    ] = "🛍️ 購入"

    item[
        "purchase_date"
    ] = today_text()

    item[
        "purchase_price"
    ] = float(
        purchase_price
    )

    item[
        "need_current"
    ] = int(need)

    item[
        "want_current"
    ] = int(want)

    item.setdefault(
        "history",
        [],
    ).append(
        {
            "date": today_text(),
            "action": (
                "🛍️ 購入した"
            ),
            "need": int(need),
            "want": int(want),
            "note": note,
        }
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def pass_item(
    data,
    item_id,
    need,
    want,
    note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "status"
    ] = "🍃 見送り"

    item[
        "passed_date"
    ] = today_text()

    item[
        "need_current"
    ] = int(need)

    item[
        "want_current"
    ] = int(want)

    item.setdefault(
        "history",
        [],
    ).append(
        {
            "date": today_text(),
            "action": (
                "🍃 買わない選択をした"
            ),
            "need": int(need),
            "want": int(want),
            "note": note,
        }
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def add_review(
    data,
    item_id,
    satisfaction,
    frequency,
    buy_again,
    note,
):
    review = {
        "id": create_id(),
        "item_id": item_id,
        "review_date": (
            today_text()
        ),
        "satisfaction": int(
            satisfaction
        ),
        "frequency": frequency,
        "buy_again": buy_again,
        "note": note,
        "created_at": now_text(),
    }

    data["reviews"].append(
        review
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

    item[
        "favorite"
    ] = not item.get(
        "favorite",
        False,
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_item(
    data,
    item_id,
    name,
    category,
    price,
    reason,
    memo,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["name"] = name
    item[
        "category"
    ] = category
    item[
        "price"
    ] = float(price)
    item[
        "reason"
    ] = reason
    item[
        "memo"
    ] = memo
    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item
        in data["items"]
        if item.get("id")
        != item_id
    ]

    data["reviews"] = [
        review
        for review
        in data["reviews"]
        if review.get(
            "item_id"
        ) != item_id
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
        background: rgba(90, 180, 130, 0.07);
        border: 1px solid rgba(90, 180, 130, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(100, 190, 145, 0.18),
                rgba(255, 190, 90, 0.10)
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

items = data["items"]
reviews = data["reviews"]

today = date.today()

waiting_items = [
    item
    for item in items
    if item.get(
        "status"
    ) == "⏳ 待機中"
]

purchased_items = [
    item
    for item in items
    if item.get(
        "status"
    ) == "🛍️ 購入"
]

passed_items = [
    item
    for item in items
    if item.get(
        "status"
    ) == "🍃 見送り"
]

due_items = [
    item
    for item in waiting_items
    if (
        parse_date(
            item.get(
                "reconsider_date"
            )
        )
        and parse_date(
            item.get(
                "reconsider_date"
            )
        ) <= today
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛒 これ、買う？やめる？</h1>
        <p>
            欲しい気持ちは、そのままでいい。
            少し待つと、本当に欲しいものが見えてくる。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

passed_total = sum(
    float(
        item.get(
            "price",
            0,
        )
    )
    for item in passed_items
)

purchase_total = sum(
    float(
        item.get(
            "purchase_price",
            item.get(
                "price",
                0,
            ),
        )
        or 0
    )
    for item in purchased_items
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "⏳ 待機中",
    f"{len(waiting_items)}個",
)

col2.metric(
    "🤔 今日の再検討",
    f"{len(due_items)}個",
)

col3.metric(
    "🛍️ 購入",
    f"{len(purchased_items)}個",
)

col4.metric(
    "🍃 見送り",
    f"{len(passed_items)}個",
)

col1, col2 = st.columns(2)

col1.metric(
    "💰 使わない選択をした金額",
    money(
        passed_total
    ),
)

col2.metric(
    "🛍️ 購入金額",
    money(
        purchase_total
    ),
)


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "🛒 欲しいものを預ける"
)

with st.form(
    "new_item_form",
    clear_on_submit=True,
):
    name = st.text_input(
        "欲しいもの",
        placeholder=(
            "例：ワイヤレスイヤホン"
        ),
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        price = st.number_input(
            "💰 価格",
            min_value=0,
            value=0,
            step=100,
        )

        need = st.slider(
            "🧠 必要度",
            1,
            5,
            3,
        )

    with col2:
        want = st.slider(
            "❤️ 欲しい度",
            1,
            5,
            4,
        )

        registered_date = (
            st.date_input(
                "📅 登録日",
                value=today,
                max_value=today,
            )
        )

        wait_label = (
            st.selectbox(
                "⏳ 何日待つ？",
                list(
                    WAIT_OPTIONS.keys()
                ),
                index=2,
            )
        )

    reason = st.text_area(
        "なぜ欲しい？",
        placeholder=(
            "例：今のイヤホンの"
            "バッテリーが弱くなった"
        ),
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "候補の商品、型番など"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📦 欲しいものBOXに預ける",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not name.strip():
            st.warning(
                "欲しいものを入力してね。"
            )

        else:
            add_item(
                data=data,
                name=name.strip(),
                category=category,
                price=price,
                need=need,
                want=want,
                reason=reason.strip(),
                registered_date=(
                    registered_date
                ),
                wait_days=(
                    WAIT_OPTIONS[
                        wait_label
                    ]
                ),
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 再検討
# =========================================================

if due_items:
    st.divider()

    st.subheader(
        "🤔 もう一度考える日です"
    )

    st.caption(
        "以前の「欲しい」と、"
        "今の気持ちを比べてみよう。"
    )

    for item in due_items:
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.subheader(
                item.get(
                    "name",
                    "",
                )
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{money(item.get('price', 0))}"
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                st.write(
                    "**登録したとき**"
                )

                st.write(
                    "必要度："
                    + stars(
                        item.get(
                            "need_initial",
                            3,
                        )
                    )
                )

                st.write(
                    "欲しい度："
                    + stars(
                        item.get(
                            "want_initial",
                            3,
                        )
                    )
                )

                st.write(
                    "登録日："
                    + format_date(
                        item.get(
                            "registered_date"
                        )
                    )
                )

            with col2:
                current_need = (
                    st.slider(
                        "今の必要度",
                        1,
                        5,
                        int(
                            item.get(
                                "need_current",
                                3,
                            )
                        ),
                        key=(
                            "need_"
                            + item_id
                        ),
                    )
                )

                current_want = (
                    st.slider(
                        "今の欲しい度",
                        1,
                        5,
                        int(
                            item.get(
                                "want_current",
                                3,
                            )
                        ),
                        key=(
                            "want_"
                            + item_id
                        ),
                    )
                )

            want_change = (
                current_want
                - int(
                    item.get(
                        "want_initial",
                        3,
                    )
                )
            )

            if want_change < 0:
                st.info(
                    "❤️ 欲しい度は登録時より "
                    f"{abs(want_change)}段階"
                    "下がっています。"
                )

            elif want_change > 0:
                st.info(
                    "❤️ 欲しい度は登録時より "
                    f"{want_change}段階"
                    "上がっています。"
                )

            decision_note = (
                st.text_area(
                    "今の気持ち",
                    key=(
                        "decision_note_"
                        + item_id
                    ),
                    placeholder=(
                        "まだ欲しい？"
                        "気持ちは変わった？"
                    ),
                )
            )

            st.markdown(
                "#### どうする？"
            )

            tab_buy, tab_wait, tab_pass = (
                st.tabs(
                    [
                        "😍 買う！",
                        "⏳ もう少し待つ",
                        "🍃 見送る",
                    ]
                )
            )

            with tab_buy:
                purchase_price = (
                    st.number_input(
                        "実際の購入価格",
                        min_value=0.0,
                        value=float(
                            item.get(
                                "price",
                                0,
                            )
                        ),
                        step=100.0,
                        key=(
                            "purchase_price_"
                            + item_id
                        ),
                    )
                )

                if st.button(
                    "🛍️ 購入した",
                    key=(
                        "buy_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    purchase_item(
                        data=data,
                        item_id=item_id,
                        purchase_price=(
                            purchase_price
                        ),
                        need=current_need,
                        want=current_want,
                        note=(
                            decision_note.strip()
                        ),
                    )

                    st.rerun()

            with tab_wait:
                extra_days = (
                    st.selectbox(
                        "あと何日待つ？",
                        [
                            1,
                            3,
                            7,
                            14,
                            30,
                        ],
                        index=2,
                        key=(
                            "extra_days_"
                            + item_id
                        ),
                    )
                )

                if st.button(
                    "⏳ もう少し考える",
                    key=(
                        "wait_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    postpone_item(
                        data=data,
                        item_id=item_id,
                        days=extra_days,
                        need=current_need,
                        want=current_want,
                        note=(
                            decision_note.strip()
                        ),
                    )

                    st.rerun()

            with tab_pass:
                st.write(
                    "買わないことも、"
                    "ちゃんとひとつの選択。"
                )

                if st.button(
                    "🍃 今回は買わない",
                    key=(
                        "pass_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    pass_item(
                        data=data,
                        item_id=item_id,
                        need=current_need,
                        want=current_want,
                        note=(
                            decision_note.strip()
                        ),
                    )

                    st.rerun()


# =========================================================
# 待機中
# =========================================================

st.divider()

st.subheader(
    "📦 欲しいものBOX"
)

future_waiting = [
    item
    for item in waiting_items
    if item not in due_items
]

if not future_waiting:
    st.info(
        "再検討日を待っているものは"
        "ありません。"
    )

else:
    for item in sorted(
        future_waiting,
        key=lambda row: (
            row.get(
                "reconsider_date",
                "",
            )
        ),
    ):
        item_id = item.get(
            "id",
            "",
        )

        reconsider = parse_date(
            item.get(
                "reconsider_date"
            )
        )

        remaining = (
            max(
                (
                    reconsider
                    - today
                ).days,
                0,
            )
            if reconsider
            else 0
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
                st.write(
                    "**"
                    + item.get(
                        "name",
                        "",
                    )
                    + "**"
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
                        "fav_wait_"
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
                f" ｜ {money(item.get('price', 0))}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "❤️ 欲しい度",
                stars(
                    item.get(
                        "want_current",
                        3,
                    )
                ),
            )

            col2.metric(
                "🧠 必要度",
                stars(
                    item.get(
                        "need_current",
                        3,
                    )
                ),
            )

            col3.metric(
                "⏳ あと",
                f"{remaining}日",
            )

            st.caption(
                "次に考える日："
                + format_date(
                    item.get(
                        "reconsider_date"
                    )
                )
            )


# =========================================================
# 購入後レビュー
# =========================================================

review_due = [
    item
    for item in purchased_items
    if (
        item.get(
            "purchase_date"
        )
        and days_since(
            item.get(
                "purchase_date"
            )
        ) >= 7
        and not get_review(
            data,
            item.get(
                "id"
            ),
        )
    )
]

if review_due:
    st.divider()

    st.subheader(
        "❤️ 買ってよかった？"
    )

    st.caption(
        "買った後まで記録すると、"
        "自分に合う買い物が見えてきます。"
    )

    for item in review_due:
        item_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.write(
                "**"
                + item.get(
                    "name",
                    "",
                )
                + "**"
            )

            st.caption(
                "購入から "
                f"{days_since(item.get('purchase_date'))}日"
            )

            satisfaction = (
                st.slider(
                    "満足度",
                    1,
                    5,
                    4,
                    key=(
                        "review_sat_"
                        + item_id
                    ),
                )
            )

            frequency = (
                st.selectbox(
                    "どれくらい使ってる？",
                    USE_FREQUENCIES,
                    key=(
                        "frequency_"
                        + item_id
                    ),
                )
            )

            buy_again = (
                st.selectbox(
                    "また買う？",
                    BUY_AGAIN_OPTIONS,
                    key=(
                        "again_"
                        + item_id
                    ),
                )
            )

            review_note = (
                st.text_area(
                    "ひとこと",
                    key=(
                        "review_note_"
                        + item_id
                    ),
                    placeholder=(
                        "これは買って正解だった！"
                    ),
                )
            )

            if st.button(
                "❤️ レビューを保存",
                key=(
                    "save_review_"
                    + item_id
                ),
                type="primary",
                use_container_width=True,
            ):
                add_review(
                    data=data,
                    item_id=item_id,
                    satisfaction=(
                        satisfaction
                    ),
                    frequency=(
                        frequency
                    ),
                    buy_again=(
                        buy_again
                    ),
                    note=(
                        review_note.strip()
                    ),
                )

                st.rerun()


# =========================================================
# 買ってよかったランキング
# =========================================================

reviewed_items = []

for item in purchased_items:
    review = get_review(
        data,
        item.get(
            "id"
        ),
    )

    if review:
        reviewed_items.append(
            (
                item,
                review,
            )
        )

if reviewed_items:
    st.divider()

    st.subheader(
        "🏆 買ってよかったもの"
    )

    reviewed_items = sorted(
        reviewed_items,
        key=lambda pair: (
            pair[1].get(
                "satisfaction",
                0,
            ),
            pair[0].get(
                "want_initial",
                0,
            ),
        ),
        reverse=True,
    )

    for rank, (
        item,
        review,
    ) in enumerate(
        reviewed_items[:10],
        start=1,
    ):
        medal = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }.get(
            rank,
            f"{rank}.",
        )

        st.write(
            f"{medal} "
            f"**{item.get('name', '')}**"
            f" — "
            f"{stars(review.get('satisfaction', 3))}"
            f" / "
            f"{money(item.get('purchase_price', 0))}"
        )

        if review.get(
            "note"
        ):
            st.caption(
                review.get(
                    "note",
                    "",
                )
            )


# =========================================================
# 欲しい気持ち分析
# =========================================================

st.divider()

st.subheader(
    "🧠 自分の「欲しい！」分析"
)

high_want_low_need = [
    item
    for item in items
    if (
        int(
            item.get(
                "want_initial",
                0,
            )
        ) == 5
        and int(
            item.get(
                "need_initial",
                0,
            )
        ) <= 2
    )
]

if high_want_low_need:
    passed_count = sum(
        1
        for item
        in high_want_low_need
        if item.get(
            "status"
        ) == "🍃 見送り"
    )

    rate = (
        passed_count
        / len(
            high_want_low_need
        )
        * 100
    )

    st.info(
        "❤️ 欲しい度★★★★★ × "
        "必要度★★以下の商品は "
        f"{len(high_want_low_need)}件。"
        f"そのうち {passed_count}件 "
        f"({rate:.0f}%)を見送りました。"
    )

high_need_reviewed = []

for item, review in (
    reviewed_items
):
    if int(
        item.get(
            "need_initial",
            0,
        )
    ) == 5:
        high_need_reviewed.append(
            review
        )

if high_need_reviewed:
    average_satisfaction = (
        sum(
            int(
                review.get(
                    "satisfaction",
                    0,
                )
            )
            for review
            in high_need_reviewed
        )
        / len(
            high_need_reviewed
        )
    )

    st.success(
        "🧠 必要度★★★★★で購入した商品の"
        f"平均満足度は "
        f"{average_satisfaction:.1f} / 5 です。"
    )

if not (
    high_want_low_need
    or high_need_reviewed
):
    st.caption(
        "記録が増えると、"
        "「欲しい」と「買ってよかった」の"
        "関係が見えてきます。"
    )


# =========================================================
# 月間分析
# =========================================================

st.divider()

month_prefix = (
    today.strftime(
        "%Y-%m"
    )
)

month_registered = [
    item
    for item in items
    if (
        item.get(
            "registered_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_purchased = [
    item
    for item in purchased_items
    if (
        item.get(
            "purchase_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_passed = [
    item
    for item in passed_items
    if (
        item.get(
            "passed_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

st.subheader(
    f"📊 {today.month}月の買い物"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🛒 欲しくなった",
    f"{len(month_registered)}個",
)

col2.metric(
    "🛍️ 購入",
    f"{len(month_purchased)}個",
)

col3.metric(
    "🍃 見送り",
    f"{len(month_passed)}個",
)

col4.metric(
    "⏳ 現在待機",
    f"{len(waiting_items)}個",
)

registered_total = sum(
    float(
        item.get(
            "price",
            0,
        )
    )
    for item in month_registered
)

month_purchase_total = sum(
    float(
        item.get(
            "purchase_price",
            0,
        )
        or 0
    )
    for item in month_purchased
)

month_pass_total = sum(
    float(
        item.get(
            "price",
            0,
        )
    )
    for item in month_passed
)

col1, col2, col3 = (
    st.columns(3)
)

col1.metric(
    "登録価格合計",
    money(
        registered_total
    ),
)

col2.metric(
    "購入金額",
    money(
        month_purchase_total
    ),
)

col3.metric(
    "使わない選択",
    money(
        month_pass_total
    ),
)


# =========================================================
# カテゴリー分析
# =========================================================

if month_registered:
    category_totals = {}

    for item in (
        month_registered
    ):
        category = item.get(
            "category",
            "🎁 その他",
        )

        category_totals[
            category
        ] = (
            category_totals.get(
                category,
                0,
            )
            + float(
                item.get(
                    "price",
                    0,
                )
            )
        )

    category_df = (
        pd.DataFrame(
            [
                {
                    "カテゴリー": key,
                    "金額": value,
                }
                for key, value
                in category_totals.items()
            ]
        )
        .sort_values(
            "金額",
            ascending=False,
        )
    )

    st.markdown(
        "### 🏷️ 今月欲しくなったもの"
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 昔欲しかったもの
# =========================================================

old_items = [
    item
    for item in items
    if (
        parse_date(
            item.get(
                "registered_date"
            )
        )
        and (
            today
            - parse_date(
                item.get(
                    "registered_date"
                )
            )
        ).days >= 30
    )
]

if old_items:
    st.divider()

    st.subheader(
        "🎲 こんなものを欲しがっていました"
    )

    item_ids = [
        item.get("id")
        for item in old_items
    ]

    random_id = (
        st.session_state.get(
            "random_old_item"
        )
    )

    if random_id not in item_ids:
        random_id = random.choice(
            item_ids
        )

        st.session_state[
            "random_old_item"
        ] = random_id

    random_item = get_item(
        data,
        random_id,
    )

    if random_item:
        with st.container(
            border=True
        ):
            st.caption(
                format_date(
                    random_item.get(
                        "registered_date"
                    )
                )
            )

            st.subheader(
                random_item.get(
                    "name",
                    "",
                )
            )

            st.write(
                "当時の欲しい度："
                + stars(
                    random_item.get(
                        "want_initial",
                        3,
                    )
                )
            )

            st.write(
                "当時の必要度："
                + stars(
                    random_item.get(
                        "need_initial",
                        3,
                    )
                )
            )

            st.write(
                "💰 "
                + money(
                    random_item.get(
                        "price",
                        0,
                    )
                )
            )

            st.write(
                "現在："
                + random_item.get(
                    "status",
                    "",
                )
            )

            review = get_review(
                data,
                random_id,
            )

            if review:
                st.success(
                    "❤️ 購入後の満足度："
                    + stars(
                        review.get(
                            "satisfaction",
                            3,
                        )
                    )
                )

        if st.button(
            "🎲 別のものを見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id in item_ids
                if item_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_old_item"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 欲しいもの図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 欲しいもの図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "イヤホン、本、服……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="category_filter",
        )
    )

with col2:
    status_filter = (
        st.selectbox(
            "状態",
            ["すべて"]
            + STATUSES,
            key="status_filter",
        )
    )

filtered_items = []

for item in items:
    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        status_filter
        != "すべて"
        and item.get(
            "status"
        ) != status_filter
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "name",
                "",
            ),
            item.get(
                "reason",
                "",
            ),
            item.get(
                "memo",
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
        "条件に合うものはありません。"
    )

else:
    rows = []

    for item in filtered_items:
        review = get_review(
            data,
            item.get(
                "id"
            ),
        )

        rows.append(
            {
                "商品": item.get(
                    "name",
                    "",
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "価格": float(
                    item.get(
                        "price",
                        0,
                    )
                ),
                "必要度": stars(
                    item.get(
                        "need_current",
                        3,
                    )
                ),
                "欲しい度": stars(
                    item.get(
                        "want_current",
                        3,
                    )
                ),
                "状態": item.get(
                    "status",
                    "",
                ),
                "購入後満足度": (
                    stars(
                        review.get(
                            "satisfaction",
                            3,
                        )
                    )
                    if review
                    else "-"
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
        column_config={
            "価格": (
                st.column_config.NumberColumn(
                    "価格",
                    format="¥%.0f",
                )
            ),
        },
    )


# =========================================================
# 編集・履歴・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・履歴・削除"
):
    if not items:
        st.caption(
            "まだ登録がありません。"
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
                "name",
                "",
            )
        ):
            edit_name = st.text_input(
                "商品名",
                value=item.get(
                    "name",
                    "",
                ),
                key=(
                    "edit_name_"
                    + item_id
                ),
            )

            old_category = item.get(
                "category",
                "🎁 その他",
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

            edit_price = (
                st.number_input(
                    "価格",
                    min_value=0.0,
                    value=float(
                        item.get(
                            "price",
                            0,
                        )
                    ),
                    step=100.0,
                    key=(
                        "edit_price_"
                        + item_id
                    ),
                )
            )

            edit_reason = (
                st.text_area(
                    "欲しい理由",
                    value=item.get(
                        "reason",
                        "",
                    ),
                    key=(
                        "edit_reason_"
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
                        "save_edit_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_name.strip()
                    ):
                        st.warning(
                            "商品名を入力してね。"
                        )
                    else:
                        update_item(
                            data,
                            item_id,
                            edit_name.strip(),
                            edit_category,
                            edit_price,
                            edit_reason.strip(),
                            edit_memo.strip(),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_fav_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            st.markdown(
                "#### 📖 判断履歴"
            )

            history = item.get(
                "history",
                [],
            )

            if not history:
                st.caption(
                    "履歴はありません。"
                )

            for history_item in reversed(
                history
            ):
                with st.container(
                    border=True
                ):
                    st.write(
                        "**"
                        + format_date(
                            history_item.get(
                                "date"
                            )
                        )
                        + "**"
                    )

                    st.write(
                        history_item.get(
                            "action",
                            "",
                        )
                    )

                    st.caption(
                        "必要度 "
                        + stars(
                            history_item.get(
                                "need",
                                3,
                            )
                        )
                        + " ｜ 欲しい度 "
                        + stars(
                            history_item.get(
                                "want",
                                3,
                            )
                        )
                    )

                    if history_item.get(
                        "note"
                    ):
                        st.caption(
                            history_item.get(
                                "note",
                                "",
                            )
                        )

            review = get_review(
                data,
                item_id,
            )

            if review:
                st.markdown(
                    "#### ❤️ 購入後レビュー"
                )

                st.write(
                    "満足度："
                    + stars(
                        review.get(
                            "satisfaction",
                            3,
                        )
                    )
                )

                st.write(
                    review.get(
                        "frequency",
                        "",
                    )
                )

                st.write(
                    review.get(
                        "buy_again",
                        "",
                    )
                )

                if review.get(
                    "note"
                ):
                    st.caption(
                        review.get(
                            "note",
                            "",
                        )
                    )

            confirm_delete = (
                st.checkbox(
                    "この商品と履歴を削除する",
                    key=(
                        "confirm_delete_"
                        + item_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_item_"
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
            "buy_or_wait_"
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
    "🛒 欲しい気持ちは、そのままでいい。"
    "少し待つと、本当に欲しいものが見えてくる。"
)

st.caption(
    "買うことも、買わないことも正解。"
    "大切なのは、自分が何を買うと"
    "幸せなのかを知ること。"
)
